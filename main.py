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

import os
import sys
import logging
import traceback
import fastapi  # 添加fastapi模块导入
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from smartflow_backend.api.endpoints.reports import router as reports_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

try:
    # 导入API路由和配置
    logger.info("正在导入API路由和配置...")
    from smartflow_backend.api.api import api_router
    from smartflow_backend.core.config import settings
    logger.info("成功导入API路由和配置")
except Exception as e:
    logger.error(f"导入API路由和配置失败: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# 创建FastAPI应用
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

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"未捕获的异常: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误",
            "type": str(type(exc).__name__),
            "message": str(exc),
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.warning(f"请求验证错误: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "请求参数验证失败",
            "errors": exc.errors(),
            "path": request.url.path
        }
    )

# 包含所有API路由
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix="/api/v1/reports")

# 健康检查端点
@app.get("/health")
def health_check():
    """健康检查端点，返回服务状态"""
    # 检查环境变量
    env_vars = {
        "SKIP_BROKEN": os.getenv("SKIP_BROKEN", "未设置"),
        "API_V1_STR": settings.API_V1_STR,
        "PROJECT_NAME": settings.PROJECT_NAME
    }
    
    # 检查路由数量
    route_count = len(app.routes)
    api_route_count = len(api_router.routes)
    
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": env_vars,
        "routes": {
            "total": route_count,
            "api": api_route_count
        }
    }

# 添加系统信息端点
@app.get("/system/info")
def system_info():
    """返回系统信息"""
    import platform
    
    return {
        "system": platform.system(),
        "python_version": platform.python_version(),
        "fastapi_version": fastapi.__version__,
        "project_name": settings.PROJECT_NAME,
        "api_prefix": settings.API_V1_STR,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    # 启动服务器
    try:
        logger.info("正在启动服务器...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 