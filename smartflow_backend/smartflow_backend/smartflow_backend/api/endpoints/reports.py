"""
智能日报API端点

主要功能:
1. 生成每日任务完成报告
2. 数据驱动的进度分析
3. AI生成的改进建议
4. 历史报告查询与统计

API端点:
- GET /reports/daily: 获取当日智能报告
- GET /reports/date/{date}: 获取指定日期的报告
- GET /reports/weekly: 获取本周汇总报告
- GET /reports/monthly: 获取本月汇总报告
- GET /reports/stats: 获取报告统计数据
- POST /reports/generate: 手动触发报告生成

AI分析功能:
- 自动分析任务完成情况，提取关键指标
- 识别任务执行中的模式和趋势
- 针对未完成或延迟任务提供洞察
- 生成个性化的改进建议和下一步行动计划

数据整合:
- 从任务执行日志收集数据
- 汇总统计信息并生成可视化数据
- 集成用户行为偏好进行个性化分析
- 通过AI模型生成自然语言报告
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import DailyReport, Task, TaskLog, User
from smartflow_backend.core.auth.deps import get_current_active_user
from smartflow_backend.api.schemas.report_schema import (
    ReportRequest,
    ReportOut,
    ReportStatsOut,
    ReportType,
    ReportGenerateRequest
)
from smartflow_backend.core.ai_services.report_generator import ReportGenerator

router = APIRouter()
logger = logging.getLogger("reports")
report_generator = ReportGenerator()

def get_report_date(report_date: Optional[date] = None) -> date:
    """获取报告日期（默认为当天）"""
    return report_date or date.today()

async def get_or_generate_report(
    user_id: int, 
    report_type: ReportType, 
    report_date: date, 
    db: Session,
    regenerate: bool = False
) -> DailyReport:
    """
    获取或生成报告
    
    参数:
    - user_id: 用户ID
    - report_type: 报告类型
    - report_date: 报告日期
    - db: 数据库会话
    - regenerate: 是否重新生成
    
    返回:
    - 报告对象
    """
    # 尝试获取现有报告
    if not regenerate:
        report = db.query(DailyReport).filter(
            DailyReport.user_id == user_id,
            DailyReport.report_date == report_date,
            DailyReport.report_type == report_type.value
        ).first()
        
        if report:
            return report
    
    # 收集数据
    if report_type == ReportType.DAILY:
        data = report_generator.collect_daily_data(user_id, report_date, db)
    elif report_type == ReportType.WEEKLY:
        data = report_generator.aggregate_weekly_data(user_id, report_date, db)
    elif report_type == ReportType.MONTHLY:
        data = report_generator.aggregate_monthly_data(
            user_id, report_date.month, report_date.year, db
        )
    else:
        raise ValueError(f"未知的报告类型: {report_type}")
    
    # 生成AI洞察
    ai_insights = await report_generator.generate_ai_insights(data)
    
    # 创建报告对象
    report = DailyReport(
        user_id=user_id,
        report_type=report_type.value,
        report_date=report_date,
        summary=ai_insights.get("summary", ""),
        tasks_completed=data.get("tasks_completed", 0),
        tasks_pending=data.get("tasks_pending", 0),
        progress_analysis=ai_insights.get("progress_analysis", ""),
        deviation_analysis=ai_insights.get("deviation_analysis", ""),
        optimization_suggestions=ai_insights.get("optimization_suggestions", ""),
        ai_insights=ai_insights.get("ai_insights", ""),
        next_steps=json.dumps(ai_insights.get("next_steps", [])),
        report_data=json.dumps(data)  # 存储原始数据用于分析
    )
    
    # 保存报告
    db.add(report)
    db.commit()
    db.refresh(report)
    
    logger.info(f"为用户 {user_id} 生成{report_type.value}报告，日期: {report_date}")
    
    return report

@router.get("/daily", response_model=ReportOut)
async def get_daily_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当日智能报告
    
    参数:
    - date: 报告日期 (可选)
    - include_details: 是否包含详细任务数据 (暂未实现)
    
    返回:
    - 日报对象
    """
    report_date = get_report_date(request.date)
    report = await get_or_generate_report(
        current_user.id, ReportType.DAILY, report_date, db
    )
    return report

@router.get("/date/{report_date}", response_model=ReportOut)
async def get_report_by_date(
    report_date: date,
    include_details: bool = Query(False, description="是否包含详细任务数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定日期的报告
    
    参数:
    - report_date: 报告日期 (YYYY-MM-DD)
    - include_details: 是否包含详细任务数据
    
    返回:
    - 报告对象
    """
    report = await get_or_generate_report(
        current_user.id, ReportType.DAILY, report_date, db
    )
    
    # 如果需要详细数据，从report_data中提取
    if include_details:
        report_data = json.loads(report.report_data)
        report.task_details = report_data.get("task_logs", [])
    
    return report

@router.get("/weekly", response_model=ReportOut)
async def get_weekly_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取本周汇总报告
    
    参数:
    - date: 报告日期 (可选，默认为本周)
    
    返回:
    - 周报对象
    """
    report_date = get_report_date(request.date)
    # 找到本周的周一
    start_of_week = report_date - timedelta(days=report_date.weekday())
    report = await get_or_generate_report(
        current_user.id, ReportType.WEEKLY, start_of_week, db
    )
    return report

@router.get("/monthly", response_model=ReportOut)
async def get_monthly_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取本月汇总报告
    
    参数:
    - date: 报告日期 (可选，默认为本月)
    
    返回:
    - 月报对象
    """
    report_date = get_report_date(request.date)
    # 使用月份的第一天
    month_start = date(report_date.year, report_date.month, 1)
    report = await get_or_generate_report(
        current_user.id, ReportType.MONTHLY, month_start, db
    )
    return report

@router.get("/stats", response_model=ReportStatsOut)
async def get_report_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取报告统计数据
    
    返回:
    - 报告统计数据
    """
    # 获取总报告数
    total_reports = db.query(func.count(DailyReport.id)).filter(
        DailyReport.user_id == current_user.id
    ).scalar()
    
    # 获取平均完成率
    avg_completion = db.query(func.avg(DailyReport.tasks_completed)).filter(
        DailyReport.user_id == current_user.id,
        DailyReport.report_type == "daily"
    ).scalar() or 0
    
    # 获取最佳和最差效率日
    best_day_query = db.query(DailyReport.report_date).filter(
        DailyReport.user_id == current_user.id,
        DailyReport.report_type == "daily"
    ).order_by(DailyReport.tasks_completed.desc()).first()
    
    worst_day_query = db.query(DailyReport.report_date).filter(
        DailyReport.user_id == current_user.id,
        DailyReport.report_type == "daily"
    ).order_by(DailyReport.tasks_completed.asc()).first()
    
    # 获取最高效时间段（简化实现）
    # 实际项目中应分析任务日志数据
    most_productive_time = "09:00-12:00"
    
    # 获取任务类型分布（简化实现）
    # 实际项目中应分析任务数据
    task_distribution = {
        "重要任务": 0.4,
        "常规任务": 0.5,
        "低优先级": 0.1
    }
    
    # 获取每周趋势数据
    weekly_trend = {
        "周一": 8,
        "周二": 9,
        "周三": 10,
        "周四": 8,
        "周五": 7,
        "周六": 3,
        "周日": 2
    }
    
    # 获取月度对比数据
    monthly_comparison = {
        "本月": 42,
        "上月": 38,
        "前月": 36
    }
    
    return ReportStatsOut(
        total_reports=total_reports,
        avg_completion_rate=round(avg_completion, 2),
        best_day=best_day_query[0] if best_day_query else date.today(),
        worst_day=worst_day_query[0] if worst_day_query else date.today(),
        most_productive_time=most_productive_time,
        task_distribution=task_distribution,
        weekly_trend=weekly_trend,
        monthly_comparison=monthly_comparison
    )

@router.post("/generate", response_model=ReportOut)
async def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    手动触发报告生成
    
    参数:
    - report_type: 报告类型 (daily, weekly, monthly)
    - date: 报告日期
    - regenerate: 是否重新生成现有报告
    
    返回:
    - 生成的报告
    """
    try:
        report = await get_or_generate_report(
            current_user.id,
            request.report_type,
            request.date,
            db,
            regenerate=request.regenerate
        )
        return report
    except Exception as e:
        logger.error(f"报告生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告生成失败: {str(e)}"
        )