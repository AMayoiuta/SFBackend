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
from __future__ import annotations
import json
import logging
import sys
import traceback
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, TYPE_CHECKING, cast

# 增加递归限制，避免递归深度超出错误
sys.setrecursionlimit(10000)

# 设置详细的调试日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)

# 打印导入路径
logger.debug("开始导入reports.py模块")

# 导入基础模块
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from smartflow_backend.db.session import get_db
from smartflow_backend.core.auth.deps import get_current_active_user
from smartflow_backend.db.models import DailyReport, Task, TaskLog

# 导入所有需要的schema
from smartflow_backend.api.schemas.report_schema import (
    ReportRequest,
    ReportType,
    ReportGenerateRequest,
    ReportOut,
    ReportStatsOut
)

# 导入报告生成器
from smartflow_backend.core.ai_services.report_generator import ReportGenerator

router = APIRouter()

def get_report_date(report_date: Optional[date] = None) -> date:
    """获取报告日期（默认为当天）"""
    return report_date or date.today()

async def get_or_generate_report(
    user_id: int, 
    report_type: ReportType, 
    report_date: date, 
    db: Session,
    regenerate: bool = False
):
    """获取或生成报告"""
    try:
        logger.debug(f"开始获取报告: user_id={user_id}, type={report_type}, date={report_date}")
        report_generator = ReportGenerator()
        
        # 尝试获取现有报告
        if not regenerate:
            report = db.query(DailyReport).filter(
                DailyReport.user_id == user_id,
                DailyReport.report_date == report_date,
                DailyReport.report_type == report_type.value
            ).first()
            
            if report:
                logger.debug("找到现有报告，直接返回")
                return ReportOut.from_orm(report)
        
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
            total_time_spent=data.get("total_time_spent", 0),
            avg_task_duration=data.get("avg_task_duration", 0.0),
            progress_analysis=ai_insights.get("progress_analysis", ""),
            deviation_analysis=ai_insights.get("deviation_analysis", ""),
            optimization_suggestions=ai_insights.get("optimization_suggestions", ""),
            ai_insights=ai_insights.get("ai_insights", ""),
            next_steps=json.dumps(ai_insights.get("next_steps", [])),
            top_tasks=json.dumps(data.get("important_tasks", [])),
            report_data=json.dumps(data)  # 存储原始数据用于分析
        )
        
        # 保存报告
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"为用户 {user_id} 生成{report_type.value}报告，日期: {report_date}")
        return ReportOut.from_orm(report)
    except Exception as e:
        logger.error(f"生成报告时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@router.get("/daily")
async def get_daily_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取当日智能报告"""
    try:
        report_date = get_report_date(request.report_date)
        report = await get_or_generate_report(
            current_user.id, ReportType.DAILY, report_date, db
        )
        return report
    except Exception as e:
        logger.error(f"获取日报时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取日报失败: {str(e)}"
        )

@router.get("/date/{report_date}")
async def get_report_by_date(
    report_date: date,
    include_details: bool = Query(False, description="是否包含详细任务数据"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取指定日期的报告"""
    try:
        report = await get_or_generate_report(
            current_user.id, ReportType.DAILY, report_date, db
        )
        
        # 如果需要详细数据，从report_data中提取
        if include_details and hasattr(report, "report_data"):
            try:
                report_data = json.loads(report.report_data)
                report.task_details = report_data.get("task_logs", [])
            except:
                pass
        
        return report
    except Exception as e:
        logger.error(f"获取指定日期报告时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告失败: {str(e)}"
        )

@router.get("/weekly")
async def get_weekly_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取本周汇总报告"""
    try:
        report_date = get_report_date(request.report_date)
        # 找到本周的周一
        start_of_week = report_date - timedelta(days=report_date.weekday())
        report = await get_or_generate_report(
            current_user.id, ReportType.WEEKLY, start_of_week, db
        )
        return report
    except Exception as e:
        logger.error(f"获取周报时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取周报失败: {str(e)}"
        )

@router.get("/monthly")
async def get_monthly_report(
    request: ReportRequest = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取本月汇总报告"""
    try:
        report_date = get_report_date(request.report_date)
        # 使用月份的第一天
        month_start = date(report_date.year, report_date.month, 1)
        report = await get_or_generate_report(
            current_user.id, ReportType.MONTHLY, month_start, db
        )
        return report
    except Exception as e:
        logger.error(f"获取月报时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取月报失败: {str(e)}"
        )

@router.get("/stats")
async def get_report_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取报告统计数据"""
    try:
        # 查询用户的所有报告
        reports = db.query(DailyReport).filter(
            DailyReport.user_id == current_user.id
        ).all()
        
        if not reports:
            return ReportStatsOut()
        
        # 计算统计数据
        total_reports = len(reports)
        completion_rates = []
        days_data = {}
        
        for report in reports:
            if report.tasks_completed + report.tasks_pending > 0:
                rate = report.tasks_completed / (report.tasks_completed + report.tasks_pending)
                completion_rates.append(rate)
                
                report_date = report.report_date.date()
                days_data[report_date] = {
                    "completion_rate": rate,
                    "tasks_completed": report.tasks_completed,
                    "total_time": report.total_time_spent
                }
        
        # 计算平均完成率
        avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        # 找出最佳和最差的日期
        best_day = None
        worst_day = None
        best_rate = 0
        worst_rate = 1
        
        for day, data in days_data.items():
            if data["completion_rate"] > best_rate:
                best_rate = data["completion_rate"]
                best_day = day
            
            if data["completion_rate"] < worst_rate:
                worst_rate = data["completion_rate"]
                worst_day = day
        
        # 查询任务类型分布
        task_types = db.query(
            Task.priority, func.count(Task.id)
        ).filter(
            Task.owner_id == current_user.id
        ).group_by(Task.priority).all()
        
        task_distribution = {}
        total_tasks = sum(count for _, count in task_types)
        
        if total_tasks > 0:
            for task_type, count in task_types:
                task_distribution[task_type] = count / total_tasks
        
        # 构建统计数据
        stats = ReportStatsOut(
            total_reports=total_reports,
            avg_completion_rate=avg_completion_rate,
            best_day=best_day,
            worst_day=worst_day,
            task_distribution=task_distribution,
            # 这里可以添加更多统计数据
        )
        
        return stats
    except Exception as e:
        logger.error(f"获取报告统计数据时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告统计数据失败: {str(e)}"
        )

@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """手动生成报告"""
    try:
        report = await get_or_generate_report(
            current_user.id, request.report_type, request.report_date, db, request.regenerate
        )
        return report
    except Exception as e:
        logger.error(f"手动生成报告时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成报告失败: {str(e)}"
        )