import os
from dotenv import load_dotenv
import redis.asyncio as redis
from redis.exceptions import ConnectionError,TimeoutError

load_dotenv()
redis_pool = redis.ConnectionPool(
    host=os.environ.get("REDIS_HOST"),
    port=os.environ.get("REIDS_PORT")
)

async def redis_connect():
    try:
        redis_client = redis.Redis(connection_pool=redis_pool)
        return redis_client
    
    except ConnectionError:
        print("连接错误")
    except TimeoutError:
        print("连接超时")
    except Exception as e:
        print(f"Redis 连接异常: {e}")