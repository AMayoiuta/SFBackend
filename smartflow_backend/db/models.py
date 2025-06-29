from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
import enum
import datetime
from typing import List

from db.base import Base


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class User(Base):
    """用户模型"""
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 用户设置和偏好
    settings = Column(JSON, default={})
    
    # 用户统计
    tasks_completed = Column(Integer, default=0)
    tasks_created = Column(Integer, default=0)
    
    # 关系
    tasks = relationship("Task", back_populates="owner")
    daily_reports = relationship("DailyReport", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Task(Base):
    """主任务模型"""
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # 智能任务规划数据
    estimated_duration = Column(Integer, nullable=True)  # 预计持续时间(分钟)
    importance_score = Column(Float, default=0.0)
    
    # 关系
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="tasks")
    sub_tasks = relationship("SubTask", back_populates="parent_task", cascade="all, delete-orphan")
    task_logs = relationship("TaskLog", back_populates="task")
    reminders = relationship("Reminder", back_populates="task")


class SubTask(Base):
    """子任务模型"""
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    order = Column(Integer, default=0)  # 子任务排序
    
    # 关系
    parent_task_id = Column(Integer, ForeignKey("task.id"))
    parent_task = relationship("Task", back_populates="sub_tasks")


class TaskLog(Base):
    """任务执行日志"""
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # 持续时间(秒)
    status = Column(Enum(TaskStatus))
    notes = Column(Text, nullable=True)
    
    # 关系
    task_id = Column(Integer, ForeignKey("task.id"))
    task = relationship("Task", back_populates="task_logs")


class Reminder(Base):
    """提醒设置"""
    reminder_time = Column(DateTime, nullable=False)
    message = Column(String(255), nullable=False)
    is_sent = Column(Boolean, default=False)
    priority = Column(Integer, default=1)  # 提醒优先级
    
    # 关系
    task_id = Column(Integer, ForeignKey("task.id"))
    task = relationship("Task", back_populates="reminders")


class DailyReport(Base):
    """每日智能日报"""
    date = Column(DateTime, default=datetime.datetime.utcnow)
    summary = Column(Text, nullable=True)
    progress_analysis = Column(Text, nullable=True)
    deviation_analysis = Column(Text, nullable=True)
    optimization_suggestions = Column(Text, nullable=True)
    tasks_completed = Column(Integer, default=0)
    tasks_pending = Column(Integer, default=0)
    
    # 关系
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="daily_reports")


class ChatMessage(Base):
    """社群聊天消息"""
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, task_share
    is_system = Column(Boolean, default=False)  # 系统消息还是用户消息
    
    # 关系
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # 允许匿名消息
    user = relationship("User", back_populates="chat_messages")
    
    # 如果是任务分享
    shared_task_id = Column(Integer, ForeignKey("task.id"), nullable=True) 