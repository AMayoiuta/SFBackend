from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from smartflow_backend.core.config import settings

# 创建SQLAlchemy引擎
engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)

# 创建本地会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 