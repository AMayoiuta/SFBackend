from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务详细描述")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="任务优先级")
    estimated_duration: Optional[int] = Field(None, description="预计持续时间(分钟)")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_duration: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    owner_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    sub_tasks: List["SubTaskOut"] = Field([], description="子任务列表")
    
    class Config:
        orm_mode = True

class SubTaskBase(BaseModel):
    title: str = Field(..., max_length=200, description="子任务标题")
    description: Optional[str] = Field(None, description="子任务描述")
    order: int = Field(0, description="子任务排序")

class SubTaskCreate(SubTaskBase):
    pass

class SubTaskOut(SubTaskBase):
    id: int
    parent_task_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TaskBreakdownRequest(BaseModel):
    task_description: str = Field(..., description="任务描述")
    user_preferences: Optional[dict] = Field(None, description="用户偏好设置")

class TaskBreakdownResponse(BaseModel):
    main_task: str = Field(..., description="主任务标题")
    description: str = Field(..., description="主任务描述")
    estimated_duration: int = Field(..., description="预计完成总时间(分钟)")
    priority: float = Field(..., description="优先级(1-10)")
    subtasks: List[dict] = Field(..., description="子任务列表")