from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    settings: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class UserOut(UserInDB):
    """用户信息输出模型"""
    pass