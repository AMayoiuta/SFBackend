"""
报告模块的数据模型定义
完全重构以避免任何循环引用
"""
from datetime import datetime, date
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

# 简单枚举类型
class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# 基础请求模型
class ReportRequest(BaseModel):
    """报告请求参数"""
    report_date: Optional[date] = Field(None, description="报告日期 (默认为当天)")
    include_details: bool = Field(False, description="是否包含详细任务数据")

# 报告生成请求模型
class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    report_type: ReportType
    report_date: date = Field(..., description="报告日期")
    regenerate: bool = Field(False, description="是否重新生成现有报告")

# 任务日志输出模型
class TaskLogOut(BaseModel):
    """任务日志输出"""
    task_title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    status: str

# 报告统计数据输出模型
class ReportStatsOut(BaseModel):
    """报告统计数据输出"""
    total_reports: int = Field(0, description="总报告数")
    avg_completion_rate: float = Field(0.0, description="平均完成率")
    best_day: Optional[date] = None
    worst_day: Optional[date] = None
    most_productive_time: Optional[str] = None
    task_distribution: dict = Field({}, description="任务类型分布")
    weekly_trend: dict = Field({}, description="每周趋势数据")
    monthly_comparison: dict = Field({}, description="月度对比数据")

# 报告输出模型
class ReportOut(BaseModel):
    """报告输出模型"""
    id: int
    user_id: int
    report_type: str
    report_date: datetime
    summary: str = Field("", description="总结摘要")
    tasks_completed: int = Field(0, description="完成任务数量")
    tasks_pending: int = Field(0, description="待处理任务数量")
    total_time_spent: int = Field(0, description="总用时(分钟)")
    avg_task_duration: float = Field(0.0, description="平均任务用时(分钟)")
    progress_analysis: str = Field("", description="进度分析")
    deviation_analysis: str = Field("", description="偏差分析")
    optimization_suggestions: str = Field("", description="优化建议")
    ai_insights: str = Field("", description="AI洞察")
    next_steps: List[str] = Field([], description="下一步行动计划")
    top_tasks: List[str] = Field([], description="重要任务列表")
    created_at: Optional[datetime] = None
    task_details: Optional[List[dict]] = None

    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建模型实例，手动实现而不使用model_validate，避免递归"""
        data = {}
        # 复制所有基本属性
        for field in [
            "id", "user_id", "report_type", "report_date", "summary",
            "tasks_completed", "tasks_pending", "total_time_spent",
            "avg_task_duration", "progress_analysis", "deviation_analysis",
            "optimization_suggestions", "ai_insights", "created_at"
        ]:
            if hasattr(obj, field):
                data[field] = getattr(obj, field)

        # 解析JSON字段
        import json
        data["next_steps"] = []
        if hasattr(obj, "next_steps") and isinstance(obj.next_steps, str):
            try:
                data["next_steps"] = json.loads(obj.next_steps)
            except Exception:
                pass

        data["top_tasks"] = []
        if hasattr(obj, "top_tasks") and isinstance(obj.top_tasks, str):
            try:
                data["top_tasks"] = json.loads(obj.top_tasks)
            except Exception:
                pass

        # 解析report_data中的task_logs为task_details
        data["task_details"] = []
        if hasattr(obj, "report_data") and isinstance(obj.report_data, str):
            try:
                report_data = json.loads(obj.report_data)
                if isinstance(report_data, dict) and "task_logs" in report_data:
                    data["task_details"] = report_data["task_logs"]
            except Exception:
                pass

        return cls(**data)