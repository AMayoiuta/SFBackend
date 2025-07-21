from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.config import settings

# 创建SQLAlchemy引擎 - 修复 SQLite 多线程问题
if "sqlite" in settings.DATABASE_URI:
    engine = create_engine(
        settings.DATABASE_URI, 
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)

# 创建本地会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库依赖项
def get_db(db_connection=None):
    """
    提供依赖注入 / 测试用 Session：
    - 常规调用：yield 一个新 Session
    - 测试时调用 get_db(db_connection=test_conn) → 绑定外部 connection
    """
    if db_connection:
        # 测试模式：使用提供的连接
        db = SessionLocal(bind=db_connection)
    else:
        # 正常模式：创建新会话
        db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()

# 为测试提供绑定外部 connection 的方法
def get_db_for_test(connection):
    """测试专用：绑定外部 connection 创建 session"""
    return get_db(db_connection=connection)

# 不再需要这个包装器，因为 get_db 现在直接支持 connection 参数
# get_db.__wrapped__ = get_db_for_test