# SmartFlow Android MVP

## 项目概述
SmartFlow是一个智能任务管理应用，集成了人工智能功能，帮助用户拆解任务、高效管理工作，并提供日报分析。该项目采用前后端分离的架构，使用Flutter构建移动端应用，FastAPI搭建后端服务。

## 项目结构

### 后端 (Python FastAPI)
```
smartflow_backend/
├── api/                    # API路由及端点定义
│   └── v1/
│       ├── api.py          # API路由注册
│       └── endpoints/      # 各功能模块端点
│           ├── auth.py     # 认证相关API
│           ├── chat.py     # 社群聊天API
│           ├── reminders.py # 提醒功能API
│           ├── reports.py  # 日报功能API
│           ├── tasks.py    # 任务管理API
│           └── users.py    # 用户管理API
├── core/                   # 核心功能模块
│   ├── ai_services/        # AI服务集成
│   │   └── task_breakdown.py # 任务拆解AI服务
│   ├── auth/               # 认证逻辑
│   └── config.py           # 应用配置
├── db/                     # 数据库相关
│   ├── base.py             # 数据库基类
│   ├── models.py           # 数据模型定义
│   └── session.py          # 数据库会话管理
├── main.py                 # 应用入口
├── migrations/             # 数据库迁移脚本
├── alembic.ini             # Alembic配置
├── requirements.txt        # 依赖库列表
└── env.example.txt         # 环境变量示例
```

### 前端 (Flutter)
```
smartflow_frontend/
├── assets/                 # 静态资源
├── lib/                    # 源代码
│   ├── models/             # 数据模型
│   │   └── task.dart       # 任务模型
│   └── services/           # 服务
│       └── api_service.dart # API服务
└── test/                   # 测试代码
```

## 核心功能模块

### 用户管理
- 用户注册、登录、认证
- 用户偏好设置

### 任务管理
- 创建和编辑任务
- 基于AI的任务拆解
- 任务优先级和状态管理
- 子任务管理

### 提醒系统
- 任务提醒设置
- 提醒优先级

### 数据分析
- 每日智能日报
- 进度分析
- 偏差分析
- 优化建议

### 社群互动
- 任务分享
- 社群聊天

## 待实现功能
- AI任务拆解器 (TODO: implement AI task splitter #3)
- 前端UI完善
- 数据持久化
- 用户认证流程
- 后端API完整实现

## 开发设置
1. 克隆仓库
2. 设置后端:
   - 复制`env.example.txt`为`.env`并配置
   - 安装依赖: `pip install -r smartflow_backend/requirements.txt`
   - 运行迁移: `alembic upgrade head`
   - 启动服务器: `uvicorn main:app --reload`

3. 设置前端:
   - 安装Flutter依赖: `flutter pub get`
   - 运行应用: `flutter run`

## 技术栈
- 后端: Python, FastAPI, SQLAlchemy, Alembic
- 前端: Flutter, Dart
- 数据库: PostgreSQL (建议)
- AI服务: 蓝心大模型API

## 贡献指南
[待添加]

## 许可证
[待添加]
