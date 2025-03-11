from fastapi import HTTPException,status
import random
import time
import json
import httpx
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from config import email_settings
import logging
#import aiosmtplib
import smtplib
import asyncio
import re
import bcrypt
from dao.schemas import CodeInput
import os
from dotenv import load_dotenv
import jwt

PASSWORD_REGEX = re.compile(r"^[a-zA-Z0-9@#$%^&+=]{8,}$")
logging.basicConfig(level=logging.INFO)

load_dotenv()
api_key = os.environ.get("HEFENG_API_KEY")
api_id = os.environ.get("API_ID")
key_id = os.environ.get("KEY_ID")
my_account=os.environ.get("MAIL_ACCOUNT")
my_pass=os.environ.get("MAIL_PASS")
print(f"api{api_key}")


#密码比对
def verify_password(password,hashed_password) :
    return bcrypt.checkpw(password.encode('utf-8'),hashed_password.encode('utf-8'))

'''def password_validatora(password:str):
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain only allowed characters and be at least 8 characters long."
        )'''

#验证码发送

async def create_verification_code(email: str,redis_client) -> str:
    # 生成6位随机验证码
    code = str(random.randint(100000, 999999))
    # 当前时间戳
    current_timestamp = time.time()
    # 设置验证码有效期为300秒
    expiry_timestamp = current_timestamp + 300
    # 构造存储数据
    verification_data = {
        "code": code,
        "timestamp": current_timestamp,
        "expiry": expiry_timestamp
    }
    # 存储到redis
    await redis_client.set(
        name=email,
        value=json.dumps(verification_data),
        ex=300  # 设置300秒后自动过期
    )
    return code

async def send_verification_code(email:str,redis_client) -> bool:
    try:
        code=await create_verification_code(email,redis_client)
         # 构建邮件内容（带HTML格式）
        msg = MIMEMultipart()
        msg.attach(MIMEText(
            f"""<!DOCTYPE html>
            <html><body>
                <p>尊敬的用户：</p>
                <p>您的验证码为 <strong style="color: #1890ff;">{code}</strong></p>
                <p>有效期3分钟，请勿泄露给他人。</p>
            </body></html>""",
            'html',
            'utf-8'
        ))

        # 设置邮件头（兼容不同客户端）
        msg['From'] = formataddr(
            (Header("天气预警系统", 'utf-8').encode(), my_account)
        )
        msg['To'] = email  # 直接使用标准邮箱地址
        msg['Subject'] = Header("您的验证码（3分钟内有效）", 'utf-8').encode()
        '''async with aiosmtplib.SMTP_SSL(
            hostname="smtp.qq.com",
            port=465,
            timeout=10
        ) as server :
            await server.login(my_account,my_pass)
            await server.sendmail(my_account,[email],msg.as_string())
        print(f"验证码{code}已发送至{email}")
        return True    
    except aiosmtplib.SMTPException as e:
        print(f"邮件发送失败:{str(e)}")
        return False
    except Exception as e:
        print(f"其他错误:{str(e)}")
        return False'''
        server=smtplib.SMTP_SSL("smtp.qq.com",465)
        server.login(my_account,my_pass)
        server.sendmail(my_account,[email],msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"其他错误:{str(e)}")
        return False

async def email_worker(redis_client,stop_event:asyncio.Event): 
    while not stop_event.is_set():
        try:
            task = await redis_client.blpop("email_queue",timeout=5)
            if not task:
                continue

            _,task_data = task
            task_info = json.loads(task_data)
            email=task_info["email"]
            await send_verification_code(email,redis_client)
        except Exception as e:
            print(f"邮件发送失败: {e},任务数据: {task_data}")
            
async def verify_verification_code(email:str,user_code: CodeInput,redis_client) -> bool:
    #user_code = await get_user_input(email)  # 获取用户输入的验证码
    code=user_code.verification_code
    correct_code_json = await redis_client.get(email)
    correct_code_data=json.loads(correct_code_json.decode())
    correct_code=correct_code_data.get("code")
    if correct_code and code == correct_code:
        return True
    return False


async def check_email_rate_limit(email:str,redis_client,limit_interval:int=300,max_attempts: int = 1) -> bool:
    key=f"rate_limit{email}"
    current_attempts=await redis_client.get(key)
    if current_attempts == None:
        await redis_client.set(key,1,ex=limit_interval)
        return True
    else:
        attempts = int (current_attempts)
        if attempts < max_attempts:
            await redis_client.incr(key)
            return True
        else:
            return False

#PEM的格式
header = "-----BEGIN PRIVATE KEY-----\n"
footer = "\n-----END PRIVATE KEY-----"
api_key=header+api_key+footer
#通过api访问和风天气
payload = {
    'iat' : int(time.time()) - 30,
    'exp' : int(time.time()) + 300,
    'sub' : api_id #凭据的项目id
}

headers = {
    'kid' : key_id#凭据id
}

encoded_jwt = jwt.encode(payload, api_key, algorithm='EdDSA', headers = headers)

