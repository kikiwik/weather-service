from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional,List,Any
from uuid import UUID
import re

class UserCreate(BaseModel):
    nickname: str  # 允许字母、数字、下划线、汉字
    email: EmailStr
    password: str  # 密码最少8位
     
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[\S]{8,20}$"
        if not re.fullmatch(pattern, value):
            raise ValueError(
                "密码必须8~20字符，且包含至少一个大写字母、小写字母和数字"
            )
        return value

    @field_validator("nickname")
    def validate_nickname(cls, value: str) -> str:
        # 定义合法字符范围（可根据需求调整允许的符号）
        allowed_chars = r"a-zA-Z0-9\u4e00-\u9fa5_#@\-"
        pattern = f"^[{allowed_chars}]{{3,10}}$"       
        if not re.fullmatch(pattern, value):
            raise ValueError(
                "昵称须3~10字符，可包含汉字、字母、数字或-_#@符号"
            )
        return value

    '''@field_validator("verification_code")
    def validate_verification_code(cls, value: str) -> str:
        if not re.fullmatch(r"^\d{6}$", value):
            raise ValueError("验证码必须是6位数字")
        return value'''

class CodeInput(BaseModel):
    verification_code: str  # 6位数字

    @field_validator("verification_code")
    def validate_verification_code(cls, value: str) -> str:
        if not re.fullmatch(r"^\d{6}$", value):
            raise ValueError("验证码必须是6位数字")
        return value
    
class UserLoginByPassword(BaseModel):
    email: EmailStr
    password: str

class UserEmail(BaseModel):
    email:EmailStr

class UserLoginByVcode(BaseModel): #验证码登录
    email: EmailStr
    verify_code: CodeInput 

class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    nickname: str    

class User(BaseModel):
    email:EmailStr
    nickname: str
    status: str

class Grid(BaseModel):
    
    lat: float
    lon: float
    
class CityIdRequest(BaseModel):
    city_id: str  # 城市的 id

class CityNameRequest(BaseModel):
    city_name: str

# 单日天气预报数据 schema，根据文档中的字段进行设计（字段类型根据实际返回数据可能为字符串或数字，可根据需要调整）
class DailyWeatherItem(BaseModel):
    fxDate: str      # 预报日期
    sunrise: str     # 日出时间
    sunset: str      # 日落时间
    tempMax: str     # 最高温度
    tempMin: str     # 最低温度
    textDay: str     # 白天天气状况描述
    iconDay: str     # 白天天气状况图标编号
    textNight: str   # 夜间天气状况描述
    iconNight: str   # 夜间天气状况图标编号
    precip: str      # 降水量
    windSpeed: str   # 风速
    windDir: str     # 风向

# 响应数据 schema，包含公共字段和 daily 字段（预报数组）
class WeatherForecastResponse(BaseModel):
    code: str              # 接口返回状态码
    updateTime: str        # 数据更新时间
    fxLink: str            # 预报详情链接
    daily: List[DailyWeatherItem]  # 未来几天天气预报数据
    #todo schemas 改为第三方库

#业务状态码
class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


# 自定义业务异常，抛出后会由全局异常处理器捕获
class BusinessException(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data

class ErrorCodes:
    # 成功
    SUCCESS = 0

    # 账户问题（1 开头）
    ACCOUNT_ERROR = 1
    ACCOUNT_NOT_LOGGED_IN = 1001
    ACCOUNT_PASSWORD_ERROR = 1002
    CAPTCHA_ERROR = 1003
    PERMISSION_DENIED = 1004
    TOKEN_EXPIRED = 1005
    ACCOUNT_EMAIL_EXISTS = 1006
    # 服务问题（2 开头）
    SERVICE_ERROR = 2
    CITY_NOT_EXIST = 2001
    COORDINATE_OUT_OF_RANGE = 2002
    REQUEST_TOO_FREQUENT = 2003

    # 网络问题（3 开头）
    NETWORK_ERROR = 3
    NETWORK_TIMEOUT = 3001
    NETWORK_CONNECTION_ERROR = 3002

    # 服务器问题（4 开头）
    SERVER_ERROR = 4
    API_PARSE_ERROR = 4001         # 天气数据解析错误
    THIRD_PARTY_API_ERROR = 4002     # 第三方接口响应错误
    DB_CONNECTION_ERROR = 4003       # 数据库连接失败
    DB_QUERY_ERROR = 4004            # 数据库查询异常
    REDIS_CONNECTION_ERROR = 4005    # redis连接失败
    REDIS_QUERY_ERROR = 4006         # redis查询异常
    SERVER_INTERNAL_ERROR = 4007     # 服务器内部错误
    SERVER_MAINTENANCE = 4008        # 服务器维护中/系统升级中
    SERVER_OVERLOAD = 4009           # 服务器过载

    # 参数问题（5 开头）
    PARAM_MISSING = 5001
    PARAM_FORMAT_ERROR = 5002
    PARAM_ILLEGAL_VALUE = 5003

    # 未知错误
    UNKNOWN_ERROR = 9999