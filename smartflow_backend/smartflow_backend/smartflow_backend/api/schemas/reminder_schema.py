from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"

class ReminderStrategy(str, Enum):
    SINGLE = "single"
    MULTI_ROUND = "multi_round"
    ESCALATING = "escalating"

class ReminderBase(BaseModel):
    task_id: int = Field(..., description="关联的任务ID")
    reminder_time: datetime = Field(..., description="计划提醒时间")
    message: str = Field(..., max_length=255, description="提醒消息内容")
    priority: int = Field(1, ge=1, le=5, description="提醒优先级（1-5）")
    status: ReminderStatus = Field(ReminderStatus.PENDING, description="提醒状态")
    strategy: ReminderStrategy = Field(ReminderStrategy.SINGLE, description="提醒策略")

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    reminder_time: Optional[datetime] = None
    message: Optional[str] = Field(None, max_length=255)
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[ReminderStatus] = None
    strategy: Optional[ReminderStrategy] = None

class ReminderOut(ReminderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_sent: bool = Field(False, description="是否已发送")
    user_id: int = Field(..., description="用户ID")

    class Config:
        orm_mode = True

class ReminderSchedule(BaseModel):
    first_reminder: datetime
    second_reminder: Optional[datetime] = None
    final_reminder: Optional[datetime] = None