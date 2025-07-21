"""
社群聊天室API端点 - 简化版本

主要功能:
1. 实时社群聊天消息 (WebSocket)
2. 任务进度分享
3. 日报片段分享
4. 系统总结消息推送

API端点:
- GET /chat/messages: 获取聊天消息历史
- POST /chat/send: 发送新聊天消息
- DELETE /chat/messages/{message_id}: 删除聊天消息
- GET /chat/daily-summary: 获取每日社群总结
- POST /chat/share/task: 分享任务进度到聊天室
- POST /chat/share/report: 分享日报片段到聊天室
- WebSocket /chat/ws: 实时消息推送
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
from sqlalchemy.orm import Session
from sqlalchemy import desc

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import ChatMessage, User, Task, DailyReport
from smartflow_backend.core.auth.deps import get_current_user, get_current_active_user
from smartflow_backend.api.schemas.chat_schema import (
    ChatMessageCreate,
    ChatMessageOut,
    DailySummary,
    ShareTaskRequest,
    ShareReportRequest,
    MessageType
)

router = APIRouter()

# 配置日志
logger = logging.getLogger("chat")
logger.setLevel(logging.INFO)

# 简化的WebSocket连接管理器
class SimpleConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.online_users: Dict[int, str] = {}  # user_id -> username
    
    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        user_id = user.id
        self.active_connections[user_id] = websocket
        self.online_users[user_id] = user.username
        
        # 发送欢迎消息
        welcome_msg = {
            "type": "system",
            "content": f"欢迎 {user.username} 加入聊天室!",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # 广播用户上线
        await self.broadcast_user_status()
        logger.info(f"用户 {user.username} 已连接")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            username = self.online_users.get(user_id, "未知用户")
            del self.active_connections[user_id]
            del self.online_users[user_id]
            
            # 异步广播用户下线
            asyncio.create_task(self.broadcast_user_status())
            logger.info(f"用户 {username} 已断开连接")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """发送私密消息给特定用户"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))
    
    async def broadcast(self, message: dict, exclude_user_id: Optional[int] = None):
        """广播消息给所有在线用户"""
        message_json = json.dumps(message)
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            if user_id == exclude_user_id:
                continue
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"广播消息给用户 {user_id} 失败: {str(e)}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_user_status(self):
        """广播在线用户状态更新"""
        status_msg = {
            "type": "user_status",
            "online_users": list(self.online_users.values()),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(status_msg)
    
    def get_online_users(self) -> List[str]:
        """获取在线用户列表"""
        return list(self.online_users.values())

# 全局连接管理器实例
manager = SimpleConnectionManager()

# HTTP API端点

@router.get("/messages", response_model=List[ChatMessageOut])
async def get_chat_messages(
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取聊天消息历史"""
    try:
        messages = db.query(ChatMessage).order_by(desc(ChatMessage.created_at)).offset(skip).limit(limit).all()
        
        # 转换为响应模型
        result = []
        for msg in messages:
            # 获取发送者信息
            sender = None
            if msg.user_id:
                sender = db.query(User).filter(User.id == msg.user_id).first()
            
            message_out = ChatMessageOut(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type,
                shared_task_id=msg.shared_task_id,
                shared_report_id=msg.shared_report_id,
                anonymous=msg.anonymous,
                user_id=msg.user_id,
                username=sender.username if sender else None,
                created_at=msg.created_at,
                is_system=msg.is_system
            )
            result.append(message_out)
        
        return result
    except Exception as e:
        logger.error(f"获取聊天消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取聊天消息失败")

@router.post("/send", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发送聊天消息"""
    try:
        # 创建新消息
        db_message = ChatMessage(
            content=message.content,
            message_type=message.message_type,
            shared_task_id=message.shared_task_id,
            shared_report_id=message.shared_report_id,
            anonymous=message.anonymous,
            user_id=current_user.id if not message.anonymous else None,
            is_system=False
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        # 构建响应
        response = ChatMessageOut(
            id=db_message.id,
            content=db_message.content,
            message_type=db_message.message_type,
            shared_task_id=db_message.shared_task_id,
            shared_report_id=db_message.shared_report_id,
            anonymous=db_message.anonymous,
            user_id=db_message.user_id,
            username=current_user.username if not message.anonymous else None,
            created_at=db_message.created_at,
            is_system=db_message.is_system
        )
        
        # 通过WebSocket广播消息
        broadcast_msg = {
            "type": "chat_message",
            "id": db_message.id,
            "content": db_message.content,
            "message_type": db_message.message_type,
            "user_id": db_message.user_id,
            "username": current_user.username if not message.anonymous else "匿名用户",
            "created_at": db_message.created_at.isoformat(),
            "anonymous": message.anonymous
        }
        
        await manager.broadcast(broadcast_msg)
        
        return response
    except Exception as e:
        logger.error(f"发送聊天消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="发送聊天消息失败")

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除聊天消息"""
    try:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 检查权限：只能删除自己的消息或系统消息
        if message.user_id != current_user.id and not message.is_system:
            raise HTTPException(status_code=403, detail="没有权限删除此消息")
        
        db.delete(message)
        db.commit()
        
        # 广播删除消息
        delete_msg = {
            "type": "message_deleted",
            "message_id": message_id,
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast(delete_msg)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除聊天消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除聊天消息失败")

@router.get("/daily-summary", response_model=DailySummary)
async def get_daily_summary(
    date: str = Query(None, description="日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取每日聊天摘要"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 获取当日消息
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at < end_date
        ).all()
        
        # 统计活跃用户
        user_stats = {}
        for msg in messages:
            if msg.user_id and not msg.anonymous:
                user_stats[msg.user_id] = user_stats.get(msg.user_id, 0) + 1
        
        # 获取活跃用户信息
        top_users = []
        for user_id, count in sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                top_users.append(user.username)
        
        # 生成摘要
        summary = f"今日共发送 {len(messages)} 条消息"
        if top_users:
            summary += f"，最活跃用户：{', '.join(top_users)}"
        
        progress_analysis = "今日社群交流活跃，成员参与度良好。"
        optimization_suggestions = "建议继续鼓励成员分享任务进度和心得体会。"
        
        return DailySummary(
            date=date,
            summary=summary,
            top_users=top_users,
            progress_analysis=progress_analysis,
            optimization_suggestions=optimization_suggestions
        )
    except Exception as e:
        logger.error(f"获取每日摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取每日摘要失败")

@router.post("/share/task", status_code=status.HTTP_200_OK)
async def share_task_to_chat(
    request: ShareTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分享任务到聊天"""
    try:
        # 检查任务是否存在
        task = db.query(Task).filter(Task.id == request.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 构建分享消息
        content = f"分享任务：{task.title}"
        if request.message:
            content += f"\n{request.message}"
        
        # 创建分享消息
        share_message = ChatMessage(
            content=content,
            message_type=MessageType.TASK_SHARE,
            shared_task_id=request.task_id,
            user_id=current_user.id,
            is_system=False
        )
        
        db.add(share_message)
        db.commit()
        db.refresh(share_message)
        
        # 广播分享消息
        broadcast_msg = {
            "type": "task_shared",
            "id": share_message.id,
            "content": content,
            "task_id": request.task_id,
            "task_title": task.title,
            "username": current_user.username,
            "created_at": share_message.created_at.isoformat()
        }
        
        await manager.broadcast(broadcast_msg)
        
        return {"message": "任务分享成功", "message_id": share_message.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分享任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="分享任务失败")

@router.post("/share/report", status_code=status.HTTP_200_OK)
async def share_report_to_chat(
    request: ShareReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分享报告到聊天"""
    try:
        # 检查报告是否存在
        report = db.query(DailyReport).filter(DailyReport.id == request.report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 构建分享消息
        content = f"分享日报：{report.report_type or '今日总结'}"
        if request.message:
            content += f"\n{request.message}"
        
        # 创建分享消息
        share_message = ChatMessage(
            content=content,
            message_type=MessageType.REPORT_SHARE,
            shared_report_id=request.report_id,
            user_id=current_user.id,
            is_system=False
        )
        
        db.add(share_message)
        db.commit()
        db.refresh(share_message)
        
        # 广播分享消息
        broadcast_msg = {
            "type": "report_shared",
            "id": share_message.id,
            "content": content,
            "report_id": request.report_id,
            "report_title": report.report_type or "今日总结",
            "username": current_user.username,
            "created_at": share_message.created_at.isoformat()
        }
        
        await manager.broadcast(broadcast_msg)
        
        return {"message": "报告分享成功", "message_id": share_message.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分享报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail="分享报告失败")

# WebSocket端点
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket连接端点"""
    try:
        # 验证用户
        user = await authenticate_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001, reason="认证失败")
            return
        
        # 连接WebSocket
        await manager.connect(websocket, user)
        
        try:
            # 处理消息
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 处理不同类型的消息
                if message_data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message_data.get("type") == "chat_message":
                    # 这里可以添加消息处理逻辑
                    pass
                
        except WebSocketDisconnect:
            manager.disconnect(user.id)
        except Exception as e:
            logger.error(f"WebSocket处理错误: {str(e)}")
            manager.disconnect(user.id)
    
    except Exception as e:
        logger.error(f"WebSocket连接错误: {str(e)}")
        try:
            await websocket.close(code=4000, reason="连接错误")
        except:
            pass

async def authenticate_user_from_token(token: str, db: Session) -> Optional[User]:
    """从令牌验证用户"""
    try:
        from smartflow_backend.core.auth.jwt import decode_access_token
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error(f"令牌验证失败: {str(e)}")
    return None

# 启动和关闭事件
@router.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("聊天模块已启动")

@router.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("聊天模块已关闭")