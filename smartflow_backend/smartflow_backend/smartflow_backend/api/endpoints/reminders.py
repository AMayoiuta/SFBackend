"""
提醒服务API端点

主要功能:
1. 创建智能提醒
2. 查询待处理提醒
3. 更新提醒状态
4. 实现多轮提醒策略

API端点:
- POST /reminders/: 创建新提醒
- GET /reminders/: 获取用户所有提醒
- GET /reminders/pending: 获取待处理提醒
- GET /reminders/{reminder_id}: 获取特定提醒详情
- PUT /reminders/{reminder_id}: 更新提醒信息
- DELETE /reminders/{reminder_id}: 删除提醒
- POST /reminders/{reminder_id}/mark-sent: 标记提醒已发送

智能提醒功能:
- 根据任务优先级和截止日期自动计算最佳提醒时间
- 支持多轮提醒策略(首次提醒、临近提醒、最终提醒)
- 集成外部通知服务(如Firebase)发送推送通知
- 分析用户响应模式，优化提醒策略

数据关联:
- 与任务模块紧密集成
- 记录提醒发送历史和用户响应
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import Reminder, Task, User
from smartflow_backend.core.auth.deps import get_current_active_user
from smartflow_backend.core.config import settings
from smartflow_backend.api.schemas.reminder_schema import (
    ReminderCreate,
    ReminderUpdate,
    ReminderOut,
    ReminderSchedule,
    ReminderStatus,
    ReminderStrategy
)

router = APIRouter()
logger = logging.getLogger("reminders")

# 智能提醒策略计算
def calculate_smart_reminder_schedule(
    due_date: datetime, 
    task_priority: str,
    strategy: ReminderStrategy
) -> ReminderSchedule:
    """
    根据任务优先级和截止日期计算智能提醒时间
    
    参数:
    - due_date: 任务截止日期
    - task_priority: 任务优先级 (low, medium, high, urgent)
    - strategy: 提醒策略
    
    返回:
    - 提醒时间计划
    """
    now = datetime.utcnow()
    schedule = ReminderSchedule(
        first_reminder=now + timedelta(hours=1)  # 默认1小时后提醒
    )
    # 根据任务优先级调整提醒时间
    if task_priority == "urgent":
        schedule.first_reminder = now + timedelta(minutes=30)
    elif task_priority == "high":
        schedule.first_reminder = now + timedelta(hours=2)
    elif task_priority == "medium":
        schedule.first_reminder = now + timedelta(hours=6)
    else:  # low
        schedule.first_reminder = now + timedelta(days=1)
    
    # 如果截止日期很近，调整提醒时间
    if due_date - now < timedelta(hours=24):
        schedule.first_reminder = now + timedelta(minutes=30)
    
    # 多轮提醒策略
    if strategy in [ReminderStrategy.MULTI_ROUND, ReminderStrategy.ESCALATING]:
        schedule.second_reminder = due_date - timedelta(hours=6)
        schedule.final_reminder = due_date - timedelta(minutes=30)
    
    return schedule

# 发送通知到外部服务
def send_notification(user: User, reminder: Reminder, message: str):
    """
    发送通知到外部服务（Firebase、邮件等）
    
    实际实现中应集成具体通知服务
    """
    logger.info(f"发送提醒给用户 {user.username} (ID: {user.id}): {message}")
    # 实际实现中应调用Firebase、邮件或SMS服务
    # 示例: firebase.send_message(user.fcm_token, message)

@router.post("/", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_in: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新提醒
    
    参数:
    - task_id: 关联的任务ID
    - message: 提醒消息内容
    - priority: 提醒优先级（1-5）
    - strategy: 提醒策略
    
    返回:
    - 创建的提醒
    """
    # 检查关联的任务是否存在
    task = db.query(Task).get(reminder_in.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    
    # 检查用户是否有权为此任务创建提醒
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权为此任务创建提醒")
    
    # 智能计算提醒时间
    schedule = calculate_smart_reminder_schedule(
        due_date=task.due_date,
        task_priority=task.priority.value,
        strategy=reminder_in.strategy
    )
    
    # 创建主提醒
    reminder = Reminder(
        **reminder_in.dict(),
        reminder_time=schedule.first_reminder,
        user_id=current_user.id
    )
    db.add(reminder)
    
    # 如果使用多轮策略，创建额外提醒
    if schedule.second_reminder:
        second_reminder = Reminder(
            task_id=reminder_in.task_id,
            message=f"即将到期: {reminder_in.message}",
            priority=reminder_in.priority + 1,
            strategy=reminder_in.strategy,
            reminder_time=schedule.second_reminder,
            user_id=current_user.id
        )
        db.add(second_reminder)
    
    if schedule.final_reminder:
        final_reminder = Reminder(
            task_id=reminder_in.task_id,
            message=f"最后提醒: {reminder_in.message}",
            priority=reminder_in.priority + 2,
            strategy=reminder_in.strategy,
            reminder_time=schedule.final_reminder,
            user_id=current_user.id
        )
        db.add(final_reminder)
    
    db.commit()
    db.refresh(reminder)
    
    # 记录创建日志
    logger.info(f"用户 {current_user.username} 为任务 {task.id} 创建了提醒")
    
    return reminder

@router.get("/", response_model=List[ReminderOut])
async def get_user_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    获取用户所有提醒
    
    参数:
    - skip: 跳过记录数
    - limit: 返回记录数
    
    返回:
    - 提醒列表
    """
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).order_by(Reminder.reminder_time.asc()).offset(skip).limit(limit).all()
    return reminders

@router.get("/pending", response_model=List[ReminderOut])
async def get_pending_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取待处理提醒
    
    返回:
    - 待处理提醒列表
    """
    now = datetime.utcnow()
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.status == ReminderStatus.PENDING,
        Reminder.reminder_time <= now
    ).order_by(Reminder.reminder_time.asc()).all()
    return reminders

@router.get("/{reminder_id}", response_model=ReminderOut)
async def get_reminder_detail(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取特定提醒详情
    
    参数:
    - reminder_id: 提醒ID
    
    返回:
    - 提醒详情
    """
    reminder = db.query(Reminder).get(reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提醒不存在")
    
    if reminder.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看此提醒")
    
    return reminder

@router.put("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(
    reminder_id: int,
    reminder_in: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新提醒信息
    
    参数:
    - reminder_id: 提醒ID
    - 更新字段
    
    返回:
    - 更新后的提醒
    """
    reminder = db.query(Reminder).get(reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提醒不存在")
    
    if reminder.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新此提醒")
    
    # 更新字段
    for field, value in reminder_in.dict(exclude_unset=True).items():
        setattr(reminder, field, value)
    
    db.commit()
    db.refresh(reminder)
    
    return reminder

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除提醒
    
    参数:
    - reminder_id: 提醒ID
    """
    reminder = db.query(Reminder).get(reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提醒不存在")
    
    if reminder.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此提醒")
    
    db.delete(reminder)
    db.commit()
    
    # 记录删除日志
    logger.info(f"用户 {current_user.username} 删除了提醒 {reminder_id}")

@router.post("/{reminder_id}/mark-sent", response_model=ReminderOut)
async def mark_reminder_sent(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    标记提醒已发送
    
    参数:
    - reminder_id: 提醒ID
    
    返回:
    - 更新后的提醒
    """
    reminder = db.query(Reminder).get(reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提醒不存在")
    
    if reminder.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作此提醒")
    
    # 更新状态
    reminder.status = ReminderStatus.SENT
    reminder.is_sent = True
    db.commit()
    db.refresh(reminder)
    
    # 发送实际通知
    user = db.query(User).get(current_user.id)
    send_notification(user, reminder, reminder.message)
    
    # 记录发送日志
    logger.info(f"提醒 {reminder_id} 已标记为已发送")
    
    return reminder