from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Union
from smartflow_backend.core.config import settings  

# --------------------------
# 密码哈希工具
# --------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def create_access_token(
    subject: Union[str, Dict], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    生成JWT访问令牌
    :param subject: 用户ID或其他标识数据
    :param expires_delta: 自定义过期时间(默认使用settings中的配置)
    :return: 签名的JWT令牌
    """
    if isinstance(subject, dict):
        to_encode = subject.copy()
    else:
        to_encode = {"sub": str(subject)}
    
    expire = datetime.utcnow() + (
        expires_delta or 
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码JWT令牌（不验证过期）"""
    try:
        return jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
    except JWTError:
        return None

def verify_token(token: str) -> bool:
    """验证令牌有效性和过期时间"""
    try:
        payload = decode_access_token(token)
        if payload is None:
            return False
        return datetime.utcnow() <= datetime.fromtimestamp(payload["exp"])
    except (JWTError, KeyError):
        return False

def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """从有效令牌中提取用户信息"""
    if not verify_token(token):
        return None
    return decode_access_token(token)

def get_password_hash(password: str) -> str:
    """生成密码的bcrypt哈希值"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)