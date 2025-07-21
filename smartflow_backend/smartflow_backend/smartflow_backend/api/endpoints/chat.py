"""
社群聊天室API端点

主要功能:
1. 实时社群聊天消息
2. 任务进度分享
3. 日报片段分享
4. 系统总结消息推送

API端点:
- GET /chat/messages: 获取聊天消息历史
- POST /chat/messages: 发送新聊天消息
- DELETE /chat/messages/{message_id}: 删除聊天消息
- GET /chat/daily-summary: 获取每日社群总结
- POST /chat/share-task: 分享任务进度到聊天室
- POST /chat/share-report: 分享日报片段到聊天室

WebSocket:
- /chat/ws: WebSocket连接点，用于实时消息推送
- 支持消息广播和用户在线状态

安全与隐私:
- 匿名聊天选项
- 消息内容审核
- 用户可选择隐藏特定任务详情
- 系统定时清理敏感信息

社群激励功能:
- 自动识别和表扬积极分享的用户
- 每日/每周荣誉榜
- 用户进度可视化对比
- 系统智能鼓励消息
""" 
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    WebSocket, 
    WebSocketDisconnect,
    Query
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import ChatMessage, User, Task, DailyReport
from smartflow_backend.core.auth.deps import get_current_user, get_current_active_user
from smartflow_backend.api.schemas.chat_schema import (
    ChatMessageCreate,
    ChatMessageOut,
    DailySummary,
    ShareTaskRequest,
    ShareReportRequest,
    OnlineUser,
    MessageType,
    ChatBroadcast
)

router = APIRouter()

# 配置日志
logger = logging.getLogger("chat")
logger.setLevel(logging.INFO)

# 敏感词过滤器
class SensitiveWordFilter:
    def __init__(self):
        # 实际应用中应从数据库或文件加载敏感词列表
        self.sensitive_words = ["敏感词1", "敏感词2", "不当内容"]
    
    def filter(self, content: str) -> str:
        """过滤敏感词"""
        for word in self.sensitive_words:
            content = content.replace(word, "***")
        return content

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.online_users: Dict[int, OnlineUser] = {}
        self.message_queue = asyncio.Queue()
        self.filter = SensitiveWordFilter()
        
        # 启动消息广播任务
        asyncio.create_task(self.broadcast_messages())
    
    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        user_id = user.id
        self.active_connections[user_id] = websocket
        
        # 添加在线用户
        self.online_users[user_id] = OnlineUser(
            user_id=user.id,
            username=user.username,
            last_active=datetime.utcnow()
        )
        
        # 广播用户上线消息
        await self.broadcast_user_status()
        logger.info(f"用户 {user.username} 已连接")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.online_users:
            del self.online_users[user_id]
        
        # 广播用户下线消息
        asyncio.create_task(self.broadcast_user_status())
        logger.info(f"用户 {user_id} 已断开连接")
    
    async def send_personal_message(self, message: Union[str, dict], user_id: int):
        """发送私密消息给特定用户"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if isinstance(message, dict):
                message = json.dumps(message)
            await websocket.send_text(message)
    
    async def broadcast(self, message: Union[str, dict], exclude_user_id: Optional[int] = None):
        """广播消息给所有在线用户"""
        if isinstance(message, dict):
            message = json.dumps(jsonable_encoder(message))
        
        for user_id, websocket in self.active_connections.items():
            if user_id == exclude_user_id:
                continue
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"广播消息给用户 {user_id} 失败: {str(e)}")
                self.disconnect(user_id)
    
    async def queue_message(self, message: ChatBroadcast):
        """将消息加入广播队列"""
        await self.message_queue.put(message)
    
    async def broadcast_messages(self):
        """持续处理广播队列中的消息"""
        while True:
            message = await self.message_queue.get()
            await self.broadcast(message.dict())
    
    async def broadcast_user_status(self):
        """广播在线用户状态更新"""
        broadcast = ChatBroadcast(
            event="user_status",
            data={
                "online_users": [
                    user.dict() for user in self.online_users.values()
                ]
            }
        )
        await self.queue_message(broadcast)
    
    def filter_content(self, content: str) -> str:
        """过滤敏感内容"""
        return self.filter.filter(content)
    
    def get_online_users(self) -> List[OnlineUser]:
        """获取在线用户列表"""
        return list(self.online_users.values())

# 全局连接管理器
manager = ConnectionManager()

# REST API端点
@router.get("/messages", response_model=List[ChatMessageOut])
async def get_chat_messages(
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取聊天消息历史
    
    参数:
    - skip: 跳过记录数
    - limit: 返回记录数
    
    返回:
    - 聊天消息列表
    """
    messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    return messages

@router.post("/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def create_chat_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    发送新聊天消息
    
    参数:
    - content: 消息内容
    - message_type: 消息类型
    - shared_task_id: 分享的任务ID
    - shared_report_id: 分享的日报ID
    - anonymous: 是否匿名发送
    
    返回:
    - 创建的聊天消息
    """
    # 过滤敏感内容
    filtered_content = manager.filter_content(message.content)
    
    # 创建消息记录
    db_message = ChatMessage(
        content=filtered_content,
        message_type=message.message_type.value,
        shared_task_id=message.shared_task_id,
        shared_report_id=message.shared_report_id,
        user_id=None if message.anonymous else current_user.id,
        is_system=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # 准备广播消息
    message_out = ChatMessageOut(
        id=db_message.id,
        content=filtered_content,
        message_type=message.message_type,
        shared_task_id=message.shared_task_id,
        shared_report_id=message.shared_report_id,
        user_id=None if message.anonymous else current_user.id,
        username=None if message.anonymous else current_user.username,
        created_at=db_message.created_at,
        is_system=False,
        anonymous=message.anonymous
    )
    
    # 广播新消息
    broadcast = ChatBroadcast(
        event="new_message",
        data=message_out.dict()
    )
    await manager.queue_message(broadcast)
    
    return message_out

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除聊天消息
    
    参数:
    - message_id: 消息ID
    
    返回:
    - 204 No Content
    """
    message = db.query(ChatMessage).get(message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    
    # 检查权限：只有消息发送者或管理员可以删除
    if message.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此消息"
        )
    
    db.delete(message)
    db.commit()
    
    # 广播消息删除通知
    broadcast = ChatBroadcast(
        event="message_deleted",
        data={"message_id": message_id}
    )
    await manager.queue_message(broadcast)
    
    return

@router.get("/daily-summary", response_model=DailySummary)
async def get_daily_summary(
    date: str = Query(None, description="日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    获取每日社群总结
    
    参数:
    - date: 日期 (可选，默认为今天)
    
    返回:
    - 每日总结数据
    """
    # 实际实现中应调用AI服务生成总结
    # 这里返回示例数据
    
    # 获取当天完成任务的用户
    top_users = db.query(User.username).join(Task).filter(
        Task.status == "completed",
        Task.completed_at >= datetime.utcnow() - timedelta(days=1)
    ).group_by(User.id).order_by(db.func.count(Task.id).desc()).limit(3).all()
    
    top_usernames = [user.username for user in top_users] if top_users else ["user1", "user2", "user3"]
    
    return DailySummary(
        date=date or datetime.utcnow().strftime("%Y-%m-%d"),
        summary="今日社群活跃度较高，共完成了15个任务，分享了8个日报片段。",
        top_users=top_usernames,
        progress_analysis="整体进度良好，但部分用户的任务完成率有待提高。",
        optimization_suggestions="建议合理分配任务优先级，避免任务堆积。"
    )

@router.post("/share-task", status_code=status.HTTP_200_OK)
async def share_task_to_chat(
    request: ShareTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分享任务进度到聊天室
    
    参数:
    - task_id: 任务ID
    - message: 附加消息
    
    返回:
    - 操作结果
    """
    task = db.query(Task).get(request.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    
    # 创建分享消息
    message_content = request.message or f"我分享了任务: {task.title}，当前状态: {task.status.value}"
    
    # 过滤敏感内容
    filtered_content = manager.filter_content(message_content)
    
    db_message = ChatMessage(
        content=filtered_content,
        message_type=MessageType.TASK_SHARE.value,
        shared_task_id=task.id,
        user_id=current_user.id,
        is_system=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # 广播消息
    message_out = ChatMessageOut(
        id=db_message.id,
        content=filtered_content,
        message_type=MessageType.TASK_SHARE,
        shared_task_id=task.id,
        user_id=current_user.id,
        username=current_user.username,
        created_at=db_message.created_at,
        is_system=False,
        anonymous=False
    )
    
    broadcast = ChatBroadcast(
        event="new_message",
        data=message_out.dict()
    )
    await manager.queue_message(broadcast)
    
    return {"message": "任务已成功分享"}

@router.post("/share-report", status_code=status.HTTP_200_OK)
async def share_report_to_chat(
    request: ShareReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分享日报片段到聊天室
    
    参数:
    - report_id: 日报ID
    - message: 附加消息
    
    返回:
    - 操作结果
    """
    report = db.query(DailyReport).get(request.report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日报不存在")
    
    # 创建分享消息
    message_content = request.message or "我分享了我的日报"
    
    # 过滤敏感内容
    filtered_content = manager.filter_content(message_content)
    
    db_message = ChatMessage(
        content=filtered_content,
        message_type=MessageType.REPORT_SHARE.value,
        shared_report_id=report.id,
        user_id=current_user.id,
        is_system=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # 广播消息
    message_out = ChatMessageOut(
        id=db_message.id,
        content=filtered_content,
        message_type=MessageType.REPORT_SHARE,
        shared_report_id=report.id,
        user_id=current_user.id,
        username=current_user.username,
        created_at=db_message.created_at,
        is_system=False,
        anonymous=False
    )
    
    broadcast = ChatBroadcast(
        event="new_message",
        data=message_out.dict()
    )
    await manager.queue_message(broadcast)
    
    return {"message": "日报已成功分享"}

# WebSocket端点
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket连接点，用于实时聊天
    
    参数:
    - token: JWT访问令牌
    """
    # 验证用户
    try:
        user = await authenticate_user_from_token(token, db)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception as e:
        logger.error(f"WebSocket认证失败: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # 连接管理器
    await manager.connect(websocket, user)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            # 处理消息
            try:
                message_data = json.loads(data)
                event = message_data.get("event")
                
                if event == "ping":
                    # 心跳检测
                    await websocket.send_text(json.dumps({"event": "pong"}))
                    # 更新用户活跃时间
                    if user.id in manager.online_users:
                        manager.online_users[user.id].last_active = datetime.utcnow()
                        await manager.broadcast_user_status()
                elif event == "message":
                    # 处理聊天消息
                    content = message_data.get("content", "")
                    message_type = message_data.get("message_type", "text")
                    anonymous = message_data.get("anonymous", False)
                    
                    # 创建消息
                    message = ChatMessageCreate(
                        content=content,
                        message_type=MessageType(message_type),
                        anonymous=anonymous
                    )
                    
                    # 保存并广播消息
                    await create_chat_message(message, db, current_user=user)
                    
            except Exception as e:
                logger.error(f"处理WebSocket消息失败: {str(e)}")
    
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        logger.error(f"WebSocket连接异常: {str(e)}")
        manager.disconnect(user.id)

async def authenticate_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    从令牌中获取用户
    
    参数:
    - token: JWT访问令牌
    - db: 数据库会话
    
    返回:
    - 用户对象或None
    """
    from smartflow_backend.core.auth.jwt import decode_access_token
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        return user
    
    except Exception as e:
        logger.error(f"令牌验证失败: {str(e)}")
        return None