"""
数据库初始化脚本

主要功能:
1. 创建数据库表
2. 添加初始数据
3. 建立示例用户账户

使用方法:
python initialize_db.py

需要先设置环境变量或.env文件
"""

from sqlalchemy import create_engine
from db.base import Base
from db.models import User, Task, SubTask, TaskStatus, TaskPriority
from db.session import get_db, engine
from core.auth.password import get_password_hash
import datetime

def init_db():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 初始化示例数据
    db = next(get_db())
    
    # 检查是否已存在用户
    user = db.query(User).first()
    if not user:
        print("创建示例用户...")
        # 创建示例用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="管理员",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # 创建示例任务
        print("创建示例任务...")
        task = Task(
            title="完成SmartFlow MVP开发",
            description="实现智序SmartFlow的最小可行产品版本",
            due_date=datetime.datetime.now() + datetime.timedelta(days=30),
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            estimated_duration=120,
            importance_score=9.0,
            owner_id=admin_user.id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 添加子任务
        subtasks = [
            SubTask(
                title="搭建后端框架", 
                description="使用FastAPI搭建后端API框架", 
                order=1,
                parent_task_id=task.id
            ),
            SubTask(
                title="实现用户认证", 
                description="添加JWT认证系统", 
                order=2,
                parent_task_id=task.id
            ),
            SubTask(
                title="开发Flutter前端", 
                description="实现移动端UI和业务逻辑", 
                order=3,
                parent_task_id=task.id
            ),
            SubTask(
                title="集成AI服务", 
                description="接入蓝心大模型实现智能任务拆解", 
                order=4,
                parent_task_id=task.id
            )
        ]
        
        for subtask in subtasks:
            db.add(subtask)
        
        db.commit()
        print("初始数据创建完成!")
    else:
        print("数据库已初始化，无需重新创建示例数据。")

if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("完成!") 