from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from smartflow_backend.db import models
from smartflow_backend.db.session import get_db
from smartflow_backend.core.auth import (
    get_current_active_user,
    get_current_active_superuser,
    get_password_hash
)
from smartflow_backend.api.schemas.user_schema import UserCreate, UserUpdate, UserInDB, UserOut

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    注册新用户
    
    参数:
    - username: 用户名 (3-50字符)
    - email: 邮箱地址
    - password: 密码 (至少8字符)
    - full_name: 全名 (可选)
    
    返回:
    - 注册成功的用户对象
    """
    # 检查用户名是否已存在
    db_user = db.query(models.User).filter(
        models.User.username == user_create.username
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    db_user = db.query(models.User).filter(
        models.User.email == user_create.email
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_create.password)
    db_user = models.User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    获取当前登录用户信息
    
    返回:
    - 当前用户对象
    """
    return current_user

@router.get("/", response_model=List[UserOut])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
):
    """
    获取用户列表 (管理员权限)
    
    参数:
    - skip: 跳过记录数
    - limit: 返回记录数
    
    返回:
    - 用户对象列表
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
):
    """
    获取特定用户信息 (管理员权限)
    
    参数:
    - user_id: 用户ID
    
    返回:
    - 用户对象
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user

@router.patch("/me", response_model=UserOut)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    更新当前用户信息
    
    参数:
    - email: 新邮箱 (可选)
    - full_name: 新全名 (可选)
    - password: 新密码 (可选，至少8字符)
    - is_active: 激活状态 (可选)
    
    返回:
    - 更新后的用户对象
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 检查邮箱是否已被其他用户使用
    if "email" in update_data:
        existing_user = db.query(models.User).filter(
            models.User.email == update_data["email"],
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被其他用户使用"
            )
    
    # 处理密码更新
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    # 更新字段
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
):
    """
    更新特定用户信息 (管理员权限)
    
    参数:
    - user_id: 用户ID
    - 更新字段
    
    返回:
    - 更新后的用户对象
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 检查邮箱是否已被其他用户使用
    if "email" in update_data:
        existing_user = db.query(models.User).filter(
            models.User.email == update_data["email"],
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被其他用户使用"
            )
    
    # 处理密码更新
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
):
    """
    删除用户 (管理员权限)
    
    参数:
    - user_id: 用户ID
    
    返回:
    - 204 No Content
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(db_user)
    db.commit()