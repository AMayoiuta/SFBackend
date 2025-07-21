"""
WebSocket实时通知服务
用于向在线用户发送实时提醒
"""

import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketNotificationService:
    """WebSocket实时通知服务"""
    
    def __init__(self):
        # 存储用户连接: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储用户连接时间: {user_id: datetime}
        self.connection_times: Dict[int, datetime] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """用户连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.connection_times[user_id] = datetime.now()
        logger.info(f"🔗 用户 {user_id} WebSocket连接建立")
    
    def disconnect(self, user_id: int):
        """用户断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.connection_times:
            del self.connection_times[user_id]
        logger.info(f"🔌 用户 {user_id} WebSocket连接断开")
    
    async def send_reminder_notification(
        self, 
        user_id: int, 
        reminder_message: str,
        task_title: str,
        reminder_time: datetime,
        reminder_id: int
    ) -> bool:
        """
        发送提醒通知
        
        参数:
        - user_id: 用户ID
        - reminder_message: 提醒消息
        - task_title: 任务标题
        - reminder_time: 提醒时间
        - reminder_id: 提醒ID
        
        返回:
        - 是否发送成功
        """
        if user_id not in self.active_connections:
            logger.warning(f"⚠️ 用户 {user_id} 不在线，无法发送WebSocket通知")
            return False
        
        try:
            websocket = self.active_connections[user_id]
            
            # 构建通知消息
            notification_data = {
                "type": "reminder",
                "reminder_id": reminder_id,
                "task_title": task_title,
                "message": reminder_message,
                "reminder_time": reminder_time.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            # 发送消息
            await websocket.send_text(json.dumps(notification_data))
            logger.info(f"✅ WebSocket通知发送成功: 用户 {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket通知发送失败: 用户 {user_id}, 错误: {str(e)}")
            # 连接可能已断开，清理连接
            self.disconnect(user_id)
            return False
    
    async def send_system_notification(self, user_id: int, message: str, notification_type: str = "info") -> bool:
        """发送系统通知"""
        if user_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[user_id]
            
            notification_data = {
                "type": "system",
                "message": message,
                "notification_type": notification_type,  # info, warning, success, error
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(notification_data))
            logger.info(f"✅ 系统通知发送成功: 用户 {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 系统通知发送失败: 用户 {user_id}, 错误: {str(e)}")
            self.disconnect(user_id)
            return False
    
    def get_online_users(self) -> Set[int]:
        """获取在线用户列表"""
        return set(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections

# 创建全局实例
websocket_service = WebSocketNotificationService() 