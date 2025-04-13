# routers/users
from fastapi import APIRouter, Depends, HTTPException,Query,Response,Request,status
from fastapi.responses import RedirectResponse,HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from dao.redis import redis_connect
from dao import crud, databases,schemas
from utils import services
import asyncio
import time
import json
import httpx
import secrets
#import requests

router = APIRouter()

@router.post("/register",response_model=schemas.ApiResponse)
async def register_user(
    user:schemas.UserCreate,
    db: AsyncSession = Depends(databases.get_async_db),
    redis_client: Redis = Depends(redis_connect)
):
    try:
        
        existing_user=await crud.get_user_by_email(db,user.email)
        if existing_user:
                raise schemas.BusinessException(schemas.ErrorCodes.ACCOUNT_EMAIL_EXISTS, "邮箱已经被注册")
        if not await services.check_email_rate_limit(user.email,redis_client): 
            raise schemas.BusinessException(
                schemas.ErrorCodes.REQUEST_TOO_FREQUENT, "Verification send too fast!"
            )
        await redis_client.rpush("email_queue", json.dumps({
                "email": user.email,
                "timestamp": time.time()
                }))
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
             raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误: {str(e)}"
        )
    ''' ret =await (services.verify_verification_code(user.email,redis_client))
        if ret==True:
             new_user=await crud.create_user(db,user)
             return new_user
        else :
             raise HTTPException(status_code=400, detail="Invalid or expired verification code")'''
    
@router.post("/register/verify",response_model=schemas.UserResponse)
async def verify_user_input_code(
      code:schemas.CodeInput,
      user:schemas.UserCreate,
      db: AsyncSession = Depends(databases.get_async_db),
      redis_client: Redis = Depends(redis_connect)
):  
    try:
        ret =await services.verify_verification_code(user.email,code,redis_client)
        if ret==True:
            new_user=await crud.create_user(db,user)
            return new_user
        else :
            raise schemas.BusinessException(
                schemas.ErrorCodes.CAPTCHA_ERROR, "验证码错误或已过期"
            )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        # 捕捉未知错误，返回服务器内部错误：4007
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误，请稍后重试: {str(e)}"
        )   
    
@router.post("/login")
async def login(
    request: Request,
    redis_client: Redis = Depends(redis_connect)
):
    # 尝试从请求 Cookie 中获取 token
    token = request.cookies.get("session_token")
    if token:
        # 在 Redis 中检查该 token 是否有效
        session_data = await redis_client.get(token)
        if session_data:
            return RedirectResponse(url="/api/users//weather-service", status_code=status.HTTP_200_OK)
    # 如果没有 token 或 Redis 中未找到匹配数据，说明需要重新登录
    return RedirectResponse(url="/api/users/login/by_pswd", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/login/by_pswd",response_model=schemas.ApiResponse)
async def login_by_pswd(
     user:schemas.UserLoginByPassword,
     response: Response,
     db:AsyncSession = Depends(databases.get_async_db),
     redis_client: Redis = Depends(redis_connect)
):
    try:
        
        login_user=await crud.get_user_by_email(db,user.email)
        if not login_user:
            raise HTTPException(401,detail="Email do not registered")
        else:
            ret = services.verify_password(user.password,login_user.password)
            if ret == True:
                token = await services.create_session_token(login_user.email, redis_client)
                response.set_cookie(
                    key="session_token", 
                    value=token, 
                    httponly=True, 
                    secure=True,  # 如果是https环境下建议开启
                    max_age=3600  # 过期时间（秒）
                )
                return {"code": schemas.ErrorCodes.SUCCESS, "message": "登录成功", "data": None}
            else:
                # 密码错误的情况
                raise schemas.BusinessException(
                    schemas.ErrorCodes.ACCOUNT_PASSWORD_ERROR, "密码错误！"
                )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        # 捕捉未知错误，返回服务器内部错误：4007
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误，请稍后重试: {str(e)}"
        )

@router.post("/login/by_verification_code",response_model=schemas.ApiResponse)
async def login_by_Vcode(
    user:schemas.UserEmail,
    db:AsyncSession = Depends(databases.get_async_db),
    redis_client: Redis = Depends(redis_connect)
):
    try:
        login_user=await crud.get_user_by_email(db,user.email)
        if not login_user:
            raise schemas.BusinessException(
                schemas.ErrorCodes.ACCOUNT_NOT_LOGGED_IN, "Email未注册"
            )
        else:
            if not await services.check_email_rate_limit(user.email,redis_client): 
                raise schemas.BusinessException(
                    schemas.ErrorCodes.REQUEST_TOO_FREQUENT, "Verification send too fast!"
                )
            await redis_client.rpush("email_queue", json.dumps({
                "email": user.email,
                "timestamp": time.time()
                }))        
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        # 捕捉未知错误，返回服务器内部错误：4007
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误，请稍后重试: {str(e)}"
        )
    
@router.post("/login/verify",response_model=schemas.ApiResponse)
async def verify_user_input_code(
      user:schemas.UserLoginByVcode,
      db: AsyncSession = Depends(databases.get_async_db),
      redis_client: Redis = Depends(redis_connect)
):  
    try:
        ret =await services.verify_verification_code(user.email,user.verify_code,redis_client)
        if ret==True:
            return {"code": schemas.ErrorCodes.SUCCESS, "message": "登录成功", "data": None}
        else :
            raise schemas.BusinessException(
                schemas.ErrorCodes.CAPTCHA_ERROR, "验证码错误或已过期"
            )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        # 捕捉未知错误，返回服务器内部错误：4007
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误，请稍后重试: {str(e)}"
        )
    
'''@router.post("/get_weather_by_grid")
async def get_weather_by_location(
    location: schemas.Grid
):
    url = "https://devapi.qweather.com/v7/grid-weather/24h"
    try:
        token =  services.get_api_token()
        params={
            "location": f"{location.lon},{location.lat}"
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response = requests.get(url,params=params,headers=header_req)
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"发生错误: {e}")'''
@router.get("/weather-service", response_class=HTMLResponse) #  如果您想返回 HTML 页面
async def weather_service_page():
    #  这里返回您的主页面 HTML 内容，或者渲染模板
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>天气服务主页面</title></head>
    <body><h1>欢迎来到天气服务主页面！</h1></body>
    </html>
    """
    return HTMLResponse(content=html_content)