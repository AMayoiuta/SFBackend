import os
import sys
import logging
import traceback
from fastapi import APIRouter, HTTPException, status, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

# 增加递归限制，避免递归深度超出错误
sys.setrecursionlimit(5000)

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("api_router")
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别，确保所有日志都能输出

# 创建主路由器
api_router = APIRouter()

# 安全导入模块
def safe_import_module(module_path: str) -> Any:
    """安全导入模块，捕获并记录任何错误"""
    try:
        logger.debug(f"尝试导入模块: {module_path}")
        
        # 直接使用importlib，避免潜在的递归问题
        import importlib
        module = importlib.import_module(module_path)
        logger.debug(f"成功导入模块: {module_path}")
        return module
    except ImportError as e:
        logger.error(f"导入模块 {module_path} 失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None
    except AttributeError as e:
        logger.error(f"模块 {module_path} 中找不到对象: {str(e)}")
        logger.error(traceback.format_exc())
        return None
    except RecursionError as e:
        logger.error(f"导入模块 {module_path} 时发生递归错误: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("请检查模块之间是否存在循环导入")
        return None
    except Exception as e:
        logger.error(f"导入模块 {module_path} 时发生未知错误: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# 始终加载的基本模块
logger.info("开始加载基本模块...")
auth = safe_import_module("smartflow_backend.api.endpoints.auth")
users = safe_import_module("smartflow_backend.api.endpoints.users")

if auth and hasattr(auth, 'router'):
    logger.info("注册认证路由...")
    api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
    logger.info("认证路由注册完成")
else:
    logger.error("无法加载认证模块，API将无法正常工作")
    
if users and hasattr(users, 'router'):
    logger.info("注册用户管理路由...")
    api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
    logger.info("用户管理路由注册完成")
else:
    logger.error("无法加载用户管理模块，API将无法正常工作")

# 可选模块
optional_modules = [
    {
        "module_path": "smartflow_backend.api.endpoints.tasks",
        "prefix": "/tasks",
        "tags": ["任务管理"],
        "description": "任务管理模块"
    },
    {
        "module_path": "smartflow_backend.api.endpoints.reminders",
        "prefix": "/reminders",
        "tags": ["提醒"],
        "description": "提醒模块"
    },
    {
        "module_path": "smartflow_backend.api.endpoints.reports",
        "prefix": "/reports",
        "tags": ["日报"],
        "description": "日报模块"
    },
    {
        "module_path": "smartflow_backend.api.endpoints.chat",
        "prefix": "/chat",
        "tags": ["社群聊天"],
        "description": "社群聊天模块"
    }
]

# 检查SKIP_BROKEN环境变量
skip_broken_value = os.getenv("SKIP_BROKEN")
logger.info(f"SKIP_BROKEN环境变量值: '{skip_broken_value}'")

# 检查DEBUG_MODULE环境变量，只加载特定模块进行调试
debug_module = os.getenv("DEBUG_MODULE")
if debug_module:
    logger.info(f"DEBUG_MODULE已设置为'{debug_module}'，只加载该模块")
    optional_modules = [m for m in optional_modules if m["module_path"].endswith(debug_module)]

# 加载所有可选模块
logger.info("开始加载所有可选模块...")
for module_info in optional_modules:
    module_path = module_info["module_path"]
    prefix = module_info["prefix"]
    tags = module_info["tags"]
    description = module_info["description"]
    
    logger.info(f"尝试加载模块: {description} (路径: {module_path}, 前缀: {prefix})")
    try:
        module = safe_import_module(module_path)
        if module and hasattr(module, 'router'):
            logger.info(f"注册路由: {prefix}")
            api_router.include_router(
                module.router,
                prefix=prefix,
                tags=tags
            )
            logger.info(f"成功加载模块: {description}")
        else:
            logger.warning(f"跳过加载模块: {description}")
    except Exception as e:
        logger.error(f"加载模块 {description} 时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        logger.warning(f"跳过加载模块: {description}")

# 添加路由器状态端点
@api_router.get("/status", tags=["系统"])
async def router_status() -> Dict[str, Any]:
    """返回API路由器的状态信息"""
    routes = []
    for route in api_router.routes:
        route_info = {
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else ["GET"]
        }
        routes.append(route_info)
    
    return {
        "status": "ok",
        "total_routes": len(api_router.routes),
        "routes": routes
    }

# 创建FastAPI应用实例
app = FastAPI(
    title="SmartFlow API",
    description="智能工作流管理系统API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由器
app.include_router(api_router, prefix="/api/v1")

# 根路径健康检查
@app.get("/")
async def root():
    return {"message": "SmartFlow API is running", "version": "1.0.0"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"} 