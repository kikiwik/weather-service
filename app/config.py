class redisSettings:
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

redis_settings = redisSettings()

class emailSettings:
    email = {
        "my_account": "1600615695@qq.com",
        "my_pass": "ypfzrplgymqhhage"
    }

email_settings = emailSettings()
#删