import redis.asyncio as redis
from redis.exceptions import ConnectionError,TimeoutError

redis_pool = redis.ConnectionPool(
    host='127.0.0.1',
    port=6379
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