from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TASK_SHARE = "task_share"
    REPORT_SHARE = "report_share"
    SYSTEM = "system"

class ChatMessageBase(BaseModel):
    content: str = Field(..., max_length=1000, description="消息内容")
    message_type: MessageType = Field(MessageType.TEXT, description="消息类型")
    shared_task_id: Optional[int] = Field(None, description="分享的任务ID")
    shared_report_id: Optional[int] = Field(None, description="分享的日报ID")
    anonymous: bool = Field(False, description="是否匿名发送")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageOut(ChatMessageBase):
    id: int
    user_id: Optional[int] = Field(None, description="用户ID（如果匿名则为空）")
    username: Optional[str] = Field(None, description="用户名（如果匿名则为空）")
    created_at: datetime
    is_system: bool = Field(False, description="是否为系统消息")

    class Config:
        orm_mode = True

class DailySummary(BaseModel):
    date: str
    summary: str
    top_users: List[str] = Field(..., description="今日荣誉榜用户")
    progress_analysis: str
    optimization_suggestions: str

class ShareTaskRequest(BaseModel):
    task_id: int
    message: Optional[str] = Field(None, max_length=500, description="附加消息")

class ShareReportRequest(BaseModel):
    report_id: int
    message: Optional[str] = Field(None, max_length=500, description="附加消息")

class OnlineUser(BaseModel):
    user_id: int
    username: str
    last_active: datetime

class ChatBroadcast(BaseModel):
    event: str
    data: dict