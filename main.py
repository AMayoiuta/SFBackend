"""
SmartFlow FastAPI 应用入口

主要功能:
1. 初始化FastAPI应用
2. 配置CORS中间件
3. 注册API路由
4. 设置数据库连接
5. 集成健康检查端点
6. 配置API文档(Swagger/ReDoc)
7. 启动应用服务器

使用方法:
- 开发环境: uvicorn main:app --reload
- 生产环境: uvicorn main:app --host 0.0.0.0 --port 8000

依赖模块:
- fastapi: Web框架
- uvicorn: ASGI服务器
- sqlalchemy: ORM数据库交互
- core.config: 应用配置
- api.v1.api: API路由
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.v1.api import api_router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="智序SmartFlow API - 智能任务规划和数据驱动的执行反馈系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含所有API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 健康检查端点
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 