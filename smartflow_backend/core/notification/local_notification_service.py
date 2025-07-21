"""
本地通知服务
提供桌面通知、日志记录和本地存储功能
无需外部配置，开箱即用
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalNotificationService:
    """本地通知服务"""
    
    def __init__(self):
        # 通知存储目录
        self.notifications_dir = Path("notifications")
        self.notifications_dir.mkdir(exist_ok=True)
        
        # 通知历史文件
        self.history_file = self.notifications_dir / "notification_history.json"
        self.load_notification_history()
    
    def load_notification_history(self):
        """加载通知历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.notification_history = json.load(f)
            except Exception as e:
                logger.error(f"加载通知历史失败: {e}")
                self.notification_history = []
        else:
            self.notification_history = []
    
    def save_notification_history(self):
        """保存通知历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.notification_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存通知历史失败: {e}")
    
    def send_reminder_notification(
        self,
        user_id: int,
        username: str,
        reminder_message: str,
        task_title: str,
        reminder_time: datetime,
        reminder_id: int
    ) -> bool:
        """
        发送本地提醒通知
        
        参数:
        - user_id: 用户ID
        - username: 用户名
        - reminder_message: 提醒消息
        - task_title: 任务标题
        - reminder_time: 提醒时间
        - reminder_id: 提醒ID
        
        返回:
        - 是否发送成功
        """
        try:
            # 构建通知数据
            notification_data = {
                "id": reminder_id,
                "user_id": user_id,
                "username": username,
                "type": "reminder",
                "task_title": task_title,
                "message": reminder_message,
                "reminder_time": reminder_time.isoformat(),
                "created_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # 1. 记录到日志
            logger.info(f"🔔 本地通知: 用户 {username} 收到提醒")
            logger.info(f"   任务: {task_title}")
            logger.info(f"   消息: {reminder_message}")
            logger.info(f"   时间: {reminder_time.strftime('%Y-%m-%d %H:%M')}")
            
            # 2. 保存到通知历史
            self.notification_history.append(notification_data)
            self.save_notification_history()
            
            # 3. 保存到单独的通知文件
            notification_file = self.notifications_dir / f"reminder_{reminder_id}_{user_id}.json"
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
            
            # 4. 输出到控制台（用于开发测试）
            print("\n" + "="*60)
            print("🔔 SmartFlow 提醒通知")
            print("="*60)
            print(f"用户: {username}")
            print(f"任务: {task_title}")
            print(f"时间: {reminder_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"消息: {reminder_message}")
            print("="*60 + "\n")
            
            logger.info(f"✅ 本地通知发送成功: 用户 {username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 本地通知发送失败: {str(e)}")
            return False
    
    def send_system_notification(
        self,
        user_id: int,
        username: str,
        message: str,
        notification_type: str = "info"
    ) -> bool:
        """
        发送系统通知
        
        参数:
        - user_id: 用户ID
        - username: 用户名
        - message: 消息内容
        - notification_type: 通知类型 (info, warning, success, error)
        
        返回:
        - 是否发送成功
        """
        try:
            notification_data = {
                "user_id": user_id,
                "username": username,
                "type": "system",
                "message": message,
                "notification_type": notification_type,
                "created_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # 记录到日志
            logger.info(f"📢 系统通知: 用户 {username} - {message}")
            
            # 保存到通知历史
            self.notification_history.append(notification_data)
            self.save_notification_history()
            
            # 输出到控制台
            icon_map = {
                "info": "ℹ️",
                "warning": "⚠️",
                "success": "✅",
                "error": "❌"
            }
            icon = icon_map.get(notification_type, "ℹ️")
            
            print(f"\n{icon} 系统通知: {message}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 系统通知发送失败: {str(e)}")
            return False
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        """获取用户通知历史"""
        user_notifications = [
            n for n in self.notification_history 
            if n.get('user_id') == user_id
        ]
        return sorted(user_notifications, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def get_notification_stats(self, user_id: int) -> Dict:
        """获取用户通知统计"""
        user_notifications = [
            n for n in self.notification_history 
            if n.get('user_id') == user_id
        ]
        
        return {
            "total": len(user_notifications),
            "reminders": len([n for n in user_notifications if n.get('type') == 'reminder']),
            "system": len([n for n in user_notifications if n.get('type') == 'system']),
            "today": len([n for n in user_notifications 
                         if datetime.fromisoformat(n['created_at']).date() == datetime.now().date()])
        }
    
    def clear_old_notifications(self, days: int = 30):
        """清理旧通知"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        original_count = len(self.notification_history)
        self.notification_history = [
            n for n in self.notification_history
            if datetime.fromisoformat(n['created_at']) > cutoff_date
        ]
        
        removed_count = original_count - len(self.notification_history)
        if removed_count > 0:
            self.save_notification_history()
            logger.info(f"清理了 {removed_count} 条旧通知")

# 创建全局实例
local_notification_service = LocalNotificationService() 