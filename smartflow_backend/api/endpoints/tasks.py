"""
任务管理API端点

主要功能:
1. 创建和管理用户任务
2. 实现智能任务拆解
3. 跟踪任务状态和进度
4. 处理子任务管理

API端点:
- POST /tasks/: 创建新任务
- GET /tasks/: 获取用户所有任务
- GET /tasks/{task_id}: 获取特定任务详情
- PUT /tasks/{task_id}: 更新任务信息
- DELETE /tasks/{task_id}: 删除任务
- POST /tasks/breakdown: AI智能拆解任务
- POST /tasks/{task_id}/subtasks: 添加子任务

实现要点:
- 集成AI服务进行任务拆解
- 关联用户认证系统确保数据安全
- 实现任务优先级和状态管理
- 提供任务过滤和排序功能
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import Task, SubTask, User
from smartflow_backend.core.auth.deps import get_current_active_user
from smartflow_backend.core.ai_services.task_breakdown import ai_task_service
from smartflow_backend.api.schemas.tasks_schema import (
    TaskCreate,
    TaskUpdate,
    TaskOut,
    SubTaskCreate,
    SubTaskOut,
    SubTaskDict,
    TaskBreakdownRequest,
    TaskBreakdownResponse,
    TaskPriority,
    TaskStatus
)

router = APIRouter()
logger = logging.getLogger("tasks")

def convert_subtask_to_dict(subtask: SubTask) -> Dict[str, Any]:
    """将SubTask对象转换为字典，避免循环引用"""
    # 使用SubTaskDict模型进行转换，确保数据格式正确
    return SubTaskDict(
        id=subtask.id,
        title=subtask.title,
        description=subtask.description,
        status=subtask.status,
        order=subtask.order,
        parent_task_id=subtask.parent_task_id,
        created_at=subtask.created_at,
        updated_at=subtask.updated_at
    ).model_dump()

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新任务
    
    参数:
    - title: 任务标题 (必需)
    - description: 任务描述 (可选)
    - due_date: 截止日期 (可选)
    - priority: 任务优先级 (默认为medium)
    - estimated_duration: 预计持续时间(分钟) (可选)
    
    返回:
    - 创建的任务对象
    """
    try:
        task = Task(
            **task_in.dict(),
            owner_id=current_user.id,
            status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 转换子任务为字典
        task.sub_tasks = [convert_subtask_to_dict(st) for st in task.sub_tasks]
        
        return task
    except Exception as e:
        db.rollback()
        logger.error(f"任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务创建失败: {str(e)}"
        )

@router.get("/", response_model=List[TaskOut])
async def get_tasks(
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(100, description="返回记录数"),
    status: Optional[TaskStatus] = Query(None, description="任务状态过滤"),
    priority: Optional[TaskPriority] = Query(None, description="优先级过滤"),
    sort_by: str = Query("due_date", description="排序字段 (id, due_date, priority)"),
    sort_order: str = Query("asc", description="排序方向 (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户任务列表
    
    参数:
    - skip: 跳过的记录数
    - limit: 返回的最大记录数
    - status: 任务状态过滤
    - priority: 优先级过滤
    - sort_by: 排序字段
    - sort_order: 排序方向
    
    返回:
    - 任务对象列表
    """
    # 构建查询
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    # 应用过滤
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    # 应用排序
    sort_field = {
        "id": Task.id,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "created_at": Task.created_at
    }.get(sort_by, Task.due_date)
    
    sort_func = asc if sort_order == "asc" else desc
    query = query.order_by(sort_func(sort_field))
    
    # 应用分页
    tasks = query.offset(skip).limit(limit).all()
    
    # 为每个任务加载子任务并转换为字典
    for task in tasks:
        task.sub_tasks = [convert_subtask_to_dict(st) for st in task.sub_tasks]
    
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个任务详情
    
    参数:
    - task_id: 任务ID
    
    返回:
    - 任务详情对象
    """
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 加载子任务并转换为字典
    task.sub_tasks = [convert_subtask_to_dict(st) for st in task.sub_tasks]
    
    return task

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新任务信息
    
    参数:
    - task_id: 要更新的任务ID
    - 更新字段
    
    返回:
    - 更新后的任务对象
    """
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此任务"
        )
    
    # 更新字段
    update_data = task_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    # 自动更新状态为完成
    if update_data.get("status") == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    # 加载子任务并转换为字典
    task.sub_tasks = [convert_subtask_to_dict(st) for st in task.sub_tasks]
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除任务
    
    参数:
    - task_id: 要删除的任务ID
    
    返回:
    - 204 No Content
    """
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此任务"
        )
    
    # 删除任务及其子任务
    db.delete(task)
    db.commit()
    
    return None

@router.post("/breakdown", response_model=TaskBreakdownResponse)
async def breakdown_task(
    breakdown_in: TaskBreakdownRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    AI智能拆解任务
    
    参数:
    - task_description: 任务描述
    - user_preferences: 用户偏好设置(可选)
    
    返回:
    - 任务拆解结果
    """
    try:
        result = await ai_task_service.breakdown_task(
            task_description=breakdown_in.task_description,
            user_preferences=breakdown_in.user_preferences or {}
        )
        return result
    except Exception as e:
        logger.error(f"任务拆解失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务拆解失败: {str(e)}"
        )

@router.post("/{task_id}/subtasks", response_model=SubTaskOut, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_id: int,
    subtask_in: SubTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    添加子任务
    
    参数:
    - task_id: 父任务ID
    - title: 子任务标题
    - description: 子任务描述(可选)
    - order: 子任务排序(可选)
    
    返回:
    - 创建的子任务对象
    """
    # 检查父任务是否存在且属于当前用户
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="父任务不存在"
        )
    
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    try:
        # 创建子任务
        subtask = SubTask(
            **subtask_in.dict(),
            parent_task_id=task_id,
            status=TaskStatus.PENDING
        )
        db.add(subtask)
        db.commit()
        db.refresh(subtask)
        return subtask
    except Exception as e:
        db.rollback()
        logger.error(f"子任务创建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"子任务创建失败: {str(e)}"
        )

@router.put("/subtasks/{subtask_id}", response_model=SubTaskOut)
async def update_subtask(
    subtask_id: int,
    subtask_in: SubTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新子任务
    
    参数:
    - subtask_id: 子任务ID
    - title: 子任务标题
    - description: 子任务描述(可选)
    - order: 子任务排序(可选)
    
    返回:
    - 更新后的子任务对象
    """
    # 获取子任务
    subtask = db.query(SubTask).get(subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="子任务不存在"
        )
    
    # 检查父任务是否属于当前用户
    task = db.query(Task).get(subtask.parent_task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此子任务"
        )
    
    # 更新子任务
    update_data = subtask_in.dict()
    for key, value in update_data.items():
        setattr(subtask, key, value)
    
    db.commit()
    db.refresh(subtask)
    return subtask

@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除子任务
    
    参数:
    - subtask_id: 子任务ID
    
    返回:
    - 204 No Content
    """
    # 获取子任务
    subtask = db.query(SubTask).get(subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="子任务不存在"
        )
    
    # 检查父任务是否属于当前用户
    task = db.query(Task).get(subtask.parent_task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此子任务"
        )
    
    # 删除子任务
    db.delete(subtask)
    db.commit()
    
    return None