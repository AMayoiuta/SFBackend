from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    """
    登录请求模型
    
    参数:
    - username: 用户名或邮箱
    - password: 密码
    """
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class TokenData(BaseModel):
    """
    令牌数据模型
    
    包含JWT令牌中存储的用户信息
    """
    sub: str = Field(..., description="用户标识 (通常是用户名)")
    exp: datetime = Field(..., description="令牌过期时间")

class TokenResponse(BaseModel):
    """
    令牌响应模型
    
    返回给客户端的访问令牌信息
    """
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field("bearer", description="令牌类型")

class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    
    参数:
    - email: 用户注册邮箱
    """
    email: EmailStr = Field(..., description="用户注册邮箱")

class PasswordResetConfirm(BaseModel):
    """
    密码重置确认模型
    
    参数:
    - token: 重置令牌
    - new_password: 新密码
    """
    token: str = Field(..., description="密码重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")

class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    
    参数:
    - refresh_token: 刷新令牌
    """
    refresh_token: str = Field(..., description="刷新令牌")

class LogoutResponse(BaseModel):
    """
    登出响应模型
    
    返回登出操作结果
    """
    message: str = Field(..., description="登出结果消息")

class AuthErrorResponse(BaseModel):
    """
    认证错误响应模型
    
    返回认证相关的错误信息
    """
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    headers: Optional[dict] = Field(None, description="认证头信息")

class UserStatus(BaseModel):
    """
    用户状态模型
    
    包含用户激活状态信息
    """
    user_id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="用户是否激活")
    username: str = Field(..., description="用户名")