from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
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