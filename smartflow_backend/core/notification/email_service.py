"""
邮件通知服务
用于发送提醒邮件
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from smartflow_backend.core.config import settings

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """邮件通知服务"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@smartflow.com')
        
    def send_reminder_email(
        self, 
        to_email: str, 
        username: str, 
        reminder_message: str,
        task_title: str,
        reminder_time: datetime
    ) -> bool:
        """
        发送提醒邮件
        
        参数:
        - to_email: 收件人邮箱
        - username: 用户名
        - reminder_message: 提醒消息
        - task_title: 任务标题
        - reminder_time: 提醒时间
        
        返回:
        - 是否发送成功
        """
        try:
            # 创建邮件内容
            subject = f"🔔 SmartFlow 提醒: {task_title}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                    .reminder-box {{ background: white; padding: 15px; border-left: 4px solid #667eea; 
                                   margin: 15px 0; border-radius: 4px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .time {{ color: #667eea; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔔 SmartFlow 智能提醒</h1>
                        <p>您好 {username}，您有一个重要提醒</p>
                    </div>
                    <div class="content">
                        <div class="reminder-box">
                            <h2>📋 任务: {task_title}</h2>
                            <p><strong>提醒时间:</strong> <span class="time">{reminder_time.strftime('%Y-%m-%d %H:%M')}</span></p>
                            <hr>
                            <p>{reminder_message}</p>
                        </div>
                        <p>请及时处理您的任务，保持高效工作！</p>
                    </div>
                    <div class="footer">
                        <p>此邮件由 SmartFlow 系统自动发送</p>
                        <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            if self.smtp_username and self.smtp_password:
                # 使用真实SMTP服务器
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # 模拟发送（用于测试）
                logger.info(f"📧 模拟发送邮件到 {to_email}")
                logger.info(f"主题: {subject}")
                logger.info(f"内容: {reminder_message[:100]}...")
                return True
            
            logger.info(f"✅ 邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {str(e)}")
            return False
    
    def send_test_email(self, to_email: str) -> bool:
        """发送测试邮件"""
        return self.send_reminder_email(
            to_email=to_email,
            username="测试用户",
            reminder_message="这是一封测试邮件，用于验证邮件服务是否正常工作。",
            task_title="邮件服务测试",
            reminder_time=datetime.now()
        )

# 创建全局实例
email_service = EmailNotificationService() 