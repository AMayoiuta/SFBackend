from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class ReportRequest(BaseModel):
    date: Optional[date] = Field(None, description="报告日期 (默认为当天)")
    include_details: bool = Field(False, description="是否包含详细任务数据")

class ReportOut(BaseModel):
    id: int
    user_id: int
    report_type: ReportType
    report_date: date
    summary: str = Field(..., description="总结摘要")
    tasks_completed: int = Field(..., description="完成任务数量")
    tasks_pending: int = Field(..., description="待处理任务数量")
    total_time_spent: int = Field(..., description="总用时(分钟)")
    avg_task_duration: float = Field(..., description="平均任务用时(分钟)")
    top_tasks: List[str] = Field([], description="重要任务列表")
    progress_analysis: str = Field(..., description="进度分析")
    deviation_analysis: str = Field(..., description="偏差分析")
    optimization_suggestions: str = Field(..., description="优化建议")
    ai_insights: str = Field(..., description="AI洞察")
    next_steps: List[str] = Field(..., description="下一步行动计划")
    created_at: datetime
    
    class Config:
        orm_mode = True

class ReportStatsOut(BaseModel):
    total_reports: int = Field(..., description="总报告数")
    avg_completion_rate: float = Field(..., description="平均完成率")
    best_day: date = Field(..., description="最佳效率日期")
    worst_day: date = Field(..., description="最低效率日期")
    most_productive_time: str = Field(..., description="最高效时间段")
    task_distribution: Dict[str, float] = Field(..., description="任务类型分布")
    weekly_trend: Dict[str, float] = Field(..., description="每周趋势数据")
    monthly_comparison: Dict[str, int] = Field(..., description="月度对比数据")
    
    class Config:
        orm_mode = True

class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    date: date = Field(..., description="报告日期")
    regenerate: bool = Field(False, description="是否重新生成现有报告")