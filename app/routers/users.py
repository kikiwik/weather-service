# routers/users
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from dao.redis import redis_connect
from dao import crud, databases,schemas
from utils import services
import asyncio
import time
import json
import httpx
router = APIRouter()

'''@router.post("/register", response_model=schemas.UserResponse)#注册用户
def register_user(user: schemas.UserCreate, db: Session = Depends(databases.get_db)):
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    services.password_validator(user.password)
    
    code=services.create_verification_code(email=user.email)
    ret = services.send_verification_code(code=code,email=user.email)
    if ret :
        print("验证码发送成功")
    else:
        print("验证码发送失败")
    
    new_user = crud.create_user(db, user=user)
    return new_user

    asyncio.create_task(services.delete_expired_codes())
    ret = services.send_verification_code(code=code,email=user.email)
    if ret :
        print("验证码发送成功")
    else:
        print("验证码发送失败")
    new_user = crud.create_user(db, user=user)
    session_token = crud.create_token(db, user_id=new_user.user_id)
    return {"user": new_user, 
            "token": session_token["token"],
            "permissions": session_token["permissions"],
            "expires_time": session_token["expires_time"]}

@router.post("/login/password", response_model=schemas.UserResponse)
def login_user(user: schemas.UserLoginA, db: Session = Depends(databases.get_db)):
    # 在数据库中查找用户
    services.password_validator(user.password)
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not services.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    session_token = crud.create_or_update_token(db, user_id=db_user.user_id)
    return {"user": db_user,  
            "token": session_token["token"],
            "permissions": session_token["permissions"],
            "expires_time": session_token["expires_time"]}

@router.post("/login/verification_code",response_model=schemas.UserResponse)
async def login_user(user:schemas.UserloginB,db: Session = Depends(databases.get_db)):
    #查找用户
    db_user = crud.get_user_by_email(db,email=user.email)
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found !")
    code=services.create_verification_code(email=db_user.email)
    asyncio.create_task(services.delete_expired_codes())
    ret = services.send_verification_code(code=code,email=db_user.email)
    if ret :
        print("验证码发送成功")
    else:
        print("验证码发送失败")

        if services.verify_verification_code(code=user.verification_code, email=db_user.email):
            session_token = crud.create_or_update_token(db, user_id=db_user.user_id)
        return {"user": db_user, 
                "token": session_token["token"],
                "permissions": session_token["permissions"],
                "expires_time": session_token["expires_time"]}
    
    raise HTTPException(status_code=401, detail="Verification code is incorrect or has expired.")'''

@router.post("/register")
async def register_user(
    user:schemas.UserCreate,
    db: AsyncSession = Depends(databases.get_async_db),
    redis_client: Redis = Depends(redis_connect)
):
    try:
        
        existing_user=await crud.get_user_by_email(db,user.email)
        if existing_user:
                raise HTTPException(409,detail="Email already registered")
        if not await services.check_email_rate_limit(user.email,redis_client): 
            raise HTTPException (409,detail="Verification send too fast !")
        await redis_client.rpush("email_queue", json.dumps({
                "email": user.email,
                "timestamp": time.time()
                }))

    except Exception as e:
             raise HTTPException(422,detail=str(e))
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
    ret =await services.verify_verification_code(user.email,code,redis_client)
    if ret==True:
        new_user=await crud.create_user(db,user)
        return new_user
    else :
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
@router.post("/login/by_pswd")
async def login_by_pswd(
     user:schemas.UserLoginByPassword,
     db:AsyncSession = Depends(databases.get_async_db)
):
    try:
        
        login_user=await crud.get_user_by_email(db,user.email)
        if not login_user:
            raise HTTPException(401,detail="Email do not registered")
        else:
            ret = services.verify_password(user.password,login_user.password)
            if ret == True:
                 return {"message":"login sucsessfully !"}
            else:
                # 密码错误的情况
                raise HTTPException(status_code=401, detail="password error !")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"登录过程中发生未知错误: {e}") 
        raise HTTPException( status_code=500, detail="服务器内部错误，请稍后重试")

@router.post("/login/by_verification_code")
async def login_by_Vcode(
    user:schemas.UserEmail,
    db:AsyncSession = Depends(databases.get_async_db),
    redis_client: Redis = Depends(redis_connect)
):
    try:
        login_user=await crud.get_user_by_email(db,user.email)
        if not login_user:
            raise HTTPException(401,detail="Email do not registered")
        else:
            if not await services.check_email_rate_limit(user.email,redis_client): 
                raise HTTPException (409,detail="Verification send too fast !")
            await redis_client.rpush("email_queue", json.dumps({
                "email": user.email,
                "timestamp": time.time()
                }))        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"登录过程中发生未知错误: {e}") 
        raise HTTPException( status_code=500, detail="服务器内部错误，请稍后重试")
    
@router.post("/login/verify")
async def verify_user_input_code(
      user:schemas.UserLoginByVcode,
      db: AsyncSession = Depends(databases.get_async_db),
      redis_client: Redis = Depends(redis_connect)
):  
    try:
        ret =await services.verify_verification_code(user.email,user.verify_code,redis_client)
        if ret==True:
            return {"message":"login sucsessfully !"}
        else :
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"登录过程中发生未知错误: {e}") 
        raise HTTPException( status_code=500, detail="服务器内部错误，请稍后重试")