from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
from typing import Optional, Tuple, Dict
import os
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from smartflow_backend.db.models import User
from smartflow_backend.db.session import get_db

# 密码哈希配置（使用 bcrypt 算法）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 重置令牌存储（生产环境应使用 Redis 或数据库）
_reset_tokens = {}

# --------------------------
# 密码核心功能
# --------------------------

def get_password_hash(plain_password: str) -> str:
    """生成密码的 bcrypt 哈希值（自动处理 salt）"""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配（防时序攻击）"""
    return pwd_context.verify(plain_password, hashed_password)

async def update_user_password(
    user_id: int, 
    new_password: str, 
    db: Session = Depends(get_db)
) -> dict:
    """
    更新用户密码
    
    参数:
        user_id: 用户ID
        new_password: 新密码明文
        db: 数据库会话
        
    返回:
        {"message": "Password updated successfully"}
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# --------------------------
# 密码重置令牌
# --------------------------

def generate_reset_token(user_id: str, expires_minutes: int = 15) -> str:
    """生成加密安全的随机重置令牌"""
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=expires_minutes)
    _reset_tokens[token] = {"user_id": user_id, "expiry": expiry}
    return token

def verify_reset_token(token: str) -> Optional[str]:
    """验证重置令牌是否有效，返回关联的 user_id"""
    token_data = _reset_tokens.get(token)
    if not token_data:
        return None
    
    if datetime.utcnow() > token_data["expiry"]:
        _reset_tokens.pop(token, None)  # 清理过期令牌
        return None
    
    return token_data["user_id"]