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