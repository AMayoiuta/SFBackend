"""
认证依赖项模块

主要功能:
1. 提供API路由认证依赖
2. 验证用户身份与权限
3. 实现基于JWT的认证流程
4. 提供当前用户访问方法

关键依赖函数:
- get_current_user(): 从请求中获取当前认证用户
- get_current_active_user(): 确保获取的用户是激活状态
- get_current_active_superuser(): 验证超级管理员权限

使用方法:
在FastAPI路由中使用Depends注入这些依赖，例如:
@router.get("/users/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user

依赖模块:
- fastapi: 依赖注入系统
- jose: JWT验证
- db: 数据库会话
- models: 用户模型
""" 