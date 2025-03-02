from fastapi import FastAPI,Request,Response,status,Depends
from contextlib import asynccontextmanager
from dao.redis import redis_connect
from utils.services import email_worker,create_verification_code
from redis import Redis
import asyncio
import json
import time


@asynccontextmanager
async def redis_service(app: FastAPI):
    app.state.redis = await redis_connect()
    app.state.email_worker_stop = asyncio.Event()
    app.state.email_worker_task = asyncio.create_task(
        email_worker(app.state.redis, app.state.email_worker_stop)
    )

    yield print("reids服务已启动")
    app.state.email_worker_stop.set()
    await app.state.email_worker_task
    await app.state.redis.close()
    print("reids服务已关闭")

app=FastAPI(
    lifespan=redis_service
)

@app.get("/")
async def status_test():
    return{"message":"OK"}

@app.post("/send-verification-code")
async def send_verification_code(redis_client: Redis = Depends(redis_connect)):
    email="alwaysfive1207@gmail.com"
    # 生成验证码
    code = await create_verification_code(email, redis_client)
    await redis_client.rpush("email_queue", json.dumps({
        "email": email,
        "code": code,
        "timestamp": time.time()
    }))
    
    return {
        "status": "queue_success",
        "message": "验证码请求已加入队列",
        "queue_position": await redis_client.llen("email_queue")
    }