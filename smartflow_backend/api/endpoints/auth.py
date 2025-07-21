from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from smartflow_backend.core.auth import (
    create_access_token,
    decode_access_token,
    generate_reset_token,
    get_password_hash,
    verify_password,
    verify_reset_token
)
from smartflow_backend.core.auth.deps import (
    authenticate_user,
    get_current_active_user,
    oauth2_scheme
)
from smartflow_backend.core.config import settings
from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import User
from smartflow_backend.api.schemas.auth_schema import (
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    RefreshTokenRequest
)

router = APIRouter()

# 登录端点 - 使用OAuth2密码模式
@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    用户登录并获取访问令牌 (OAuth2兼容)
    
    参数:
    - username: 用户名或邮箱
    - password: 密码
    
    返回:
    - access_token: JWT访问令牌
    - token_type: 令牌类型 (Bearer)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户名或密码",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# 登出端点 - 可选令牌黑名单
@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    用户登出(可选实现令牌黑名单)
    
    参数:
    - token: 当前访问令牌
    
    返回:
    - message: 登出成功消息
    """
    # 在实际应用中，这里应将令牌加入黑名单（如Redis）
    # 本示例仅返回成功消息
    return {"message": f"用户 {current_user.username} 已成功登出"}

# 密码重置请求
@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    请求密码重置
    
    参数:
    - email: 用户注册邮箱
    
    返回:
    - message: 重置请求处理结果
    """
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # 出于安全考虑，即使邮箱不存在也返回成功
        return {"message": "如果邮箱存在，重置链接已发送"}
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 生成密码重置令牌
    reset_token = generate_reset_token(str(user.id))
    
    # 在实际应用中，这里应发送包含重置链接的电子邮件
    # 示例: send_reset_email(user.email, reset_token)
    print(f"密码重置令牌: {reset_token} (用户ID: {user.id})")
    
    return {"message": "如果邮箱存在，重置链接已发送"}

# 密码重置确认
@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    确认密码重置
    
    参数:
    - token: 重置令牌
    - new_password: 新密码
    
    返回:
    - message: 重置结果
    """
    # 验证重置令牌
    user_id = verify_reset_token(request.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或过期的重置令牌"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 更新密码
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    # 清除使用过的令牌
    verify_reset_token(request.token, remove=True)
    
    return {"message": "密码已成功重置"}

# 刷新访问令牌
@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    刷新访问令牌
    
    参数:
    - refresh_token: 刷新令牌
    
    返回:
    - access_token: 新的访问令牌
    - token_type: 令牌类型 (Bearer)
    """
    try:
        # 解码令牌
        payload = decode_access_token(request.refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 获取用户信息
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌内容"
            )
        
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账户已被禁用"
            )
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )