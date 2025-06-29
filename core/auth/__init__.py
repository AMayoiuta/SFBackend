"""
认证模块初始化文件

主要功能:
1. 导出关键认证函数和依赖
2. 简化认证组件的导入方式

导出组件:
- 从deps模块: get_current_user, get_current_active_user
- 从jwt模块: create_access_token
- 从password模块: verify_password, get_password_hash

使用方法:
from core.auth import get_current_active_user, create_access_token
"""

# 导出主要的认证函数
from .deps import get_current_user, get_current_active_user, get_current_active_superuser
from .jwt import create_access_token, decode_access_token
from .password import verify_password, get_password_hash 