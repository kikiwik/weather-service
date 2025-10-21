#main
from fastapi import FastAPI,Request,Response,status,Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
from dao.redis import redis_connect
from dao import databases,schemas
from utils.services import email_worker
from routers import users,servers
from redis import Redis
import asyncio
import json
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("数据库连接池初始化")
    async with databases.async_engine.connect() as conn:
        await conn.exec_driver_sql("SELECT 1")

    print("Redis初始化链接")
    app.state.redis = await redis_connect()
    app.state.email_worker_stop = asyncio.Event()
    app.state.email_worker_task = asyncio.create_task(
        email_worker(app.state.redis, app.state.email_worker_stop)
    )

    yield print("redis服务已启动\n数据库服务已启动\n")
    await databases.async_engine.dispose()
    print("数据库连接池已关闭")

    app.state.email_worker_stop.set()
    await app.state.email_worker_task
    await app.state.redis.close()
    print("redis服务已关闭")

app=FastAPI(
    lifespan=lifespan
)

@app.exception_handler(schemas.BusinessException)
async def business_exception_handler(request: Request, exc: schemas.BusinessException):
    return JSONResponse(
        status_code=200,  # 业务错误使用 200 状态码，具体错误由 code 区分
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )

@app.get("/")
async def status_test():
    return{"message":"OK"}

app.include_router(users.router, prefix="/weather-service/users",tags=["users"])
app.include_router(servers.router, prefix="/weather-service/servers", tags=["servers"])

#测试
@app.post("/test-send-verification-code")
async def send_verification_code(redis_client: Redis = Depends(redis_connect)):
    email="alwaysfive1207@gmail.com"
    # 生成验证码
    #code = await create_verification_code(email, redis_client)
    await redis_client.rpush("email_queue", json.dumps({
        "email": email,
        "timestamp": time.time()
    }))
    
    return {
        "status": "queue_success",
        "message": "验证码请求已加入队列",
        "queue_position": await redis_client.llen("email_queue")
    }

@app.get("/test-db")
async def test_db_connection(db :databases.AsyncSession =Depends(databases.get_async_db)):
    result = await db.execute(text("SELECT NOW()"))
    current_time = result.scalar_one()
    return{"Current_time":current_time}