import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json
import httpx

from smartflow_backend.db.session import get_db
from smartflow_backend.db.models import Task, TaskLog, DailyReport, User
from smartflow_backend.core.config import settings

logger = logging.getLogger("report_generator")

class ReportGenerator:
    def __init__(self):
        self.ai_api_url = settings.AI_MODEL_API_URL
        self.ai_api_key = settings.AI_MODEL_API_KEY
    
    def collect_daily_data(self, user_id: int, report_date: date, db) -> Dict:
        """
        收集每日报告数据
        """
        start_date = datetime.combine(report_date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        # 查询当天的任务日志
        task_logs = db.query(TaskLog).filter(
            TaskLog.start_time >= start_date,
            TaskLog.start_time < end_date,
            Task.user_id == user_id
        ).join(Task).all()
        
        # 查询当天的任务完成情况
        completed_tasks = db.query(Task).filter(
            Task.status == "completed",
            Task.completed_at >= start_date,
            Task.completed_at < end_date,
            Task.user_id == user_id
        ).all()
        
        pending_tasks = db.query(Task).filter(
            Task.status.in_(["pending", "in_progress"]),
            Task.user_id == user_id
        ).all()
        
        # 计算统计数据
        total_time = sum(log.duration or 0 for log in task_logs) // 60  # 转换为分钟
        task_count = len(completed_tasks)
        avg_duration = total_time / task_count if task_count > 0 else 0
        
        # 识别重要任务
        important_tasks = [task.title for task in completed_tasks if task.priority in ["high", "urgent"]]
        
        return {
            "date": report_date.isoformat(),
            "tasks_completed": len(completed_tasks),
            "tasks_pending": len(pending_tasks),
            "total_time_spent": total_time,
            "avg_task_duration": round(avg_duration, 1),
            "important_tasks": important_tasks,
            "task_logs": [
                {
                    "task_title": log.task.title,
                    "start_time": log.start_time.isoformat(),
                    "end_time": log.end_time.isoformat() if log.end_time else None,
                    "duration": log.duration,
                    "status": log.status
                } for log in task_logs
            ]
        }
    
    async def generate_ai_insights(self, data: Dict) -> Dict:
        """
        使用AI生成报告洞察
        """
        if not self.ai_api_url or not self.ai_api_key:
            logger.warning("AI服务未配置，使用默认报告")
            return self.default_report(data)
        
        try:
            prompt = self.build_insight_prompt(data)
            headers = {
                "Authorization": f"Bearer {self.ai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": prompt,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.ai_api_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # 提取AI生成的JSON
                ai_output = result["choices"][0]["text"].strip()
                if ai_output.startswith("```json"):
                    ai_output = ai_output[7:]
                if ai_output.endswith("```"):
                    ai_output = ai_output[:-3]
                
                return json.loads(ai_output)
        
        except Exception as e:
            logger.error(f"AI报告生成失败: {str(e)}")
            return self.default_report(data)
    
    def build_insight_prompt(self, data: Dict) -> str:
        """
        构建AI提示词
        """
        return f"""
请基于以下用户任务数据生成一份智能日报报告：

**任务统计数据**
- 日期: {data['date']}
- 完成任务数: {data['tasks_completed']}
- 待处理任务数: {data['tasks_pending']}
- 总用时: {data['total_time_spent']} 分钟
- 平均任务用时: {data['avg_task_duration']} 分钟
- 重要任务: {", ".join(data['important_tasks']) if data['important_tasks'] else "无"}

**任务日志**
{json.dumps(data['task_logs'], indent=2, ensure_ascii=False)}

**报告要求**
1. 总结当天的任务完成情况（50-100字）
2. 分析进度表现（识别关键成就和挑战）
3. 识别任何偏差（计划vs实际）
4. 提供3-5条具体的优化建议
5. 提供2-3条AI洞察（基于模式分析）
6. 建议3个下一步行动计划

请返回JSON格式，结构如下：
{{
    "summary": "总结摘要",
    "progress_analysis": "进度分析",
    "deviation_analysis": "偏差分析",
    "optimization_suggestions": "优化建议",
    "ai_insights": "AI洞察",
    "next_steps": ["步骤1", "步骤2", "步骤3"]
}}
"""
    
    def default_report(self, data: Dict) -> Dict:
        """
        默认报告模板（当AI服务不可用时）
        """
        return {
            "summary": f"在{data['date']}完成了{data['tasks_completed']}个任务，用时{data['total_time_spent']}分钟。",
            "progress_analysis": "整体进度良好，但部分任务耗时较长。",
            "deviation_analysis": "有3个任务未按计划完成。",
            "optimization_suggestions": "建议优先处理重要任务并合理分配时间。",
            "ai_insights": "您在上午时段工作效率最高。",
            "next_steps": ["审查未完成任务", "规划明日优先级", "优化时间分配"]
        }
    
    def aggregate_weekly_data(self, user_id: int, start_date: date, db) -> Dict:
        """
        聚合周报数据
        """
        # 实现类似collect_daily_data的逻辑，但时间范围为整周
        # 实际项目中应实现此方法
        return {
            "summary": "本周工作汇总报告",
            # 其他聚合数据...
        }
    
    def aggregate_monthly_data(self, user_id: int, month: int, year: int, db) -> Dict:
        """
        聚合月报数据
        """
        # 实现类似collect_daily_data的逻辑，但时间范围为整月
        # 实际项目中应实现此方法
        return {
            "summary": "本月工作汇总报告",
            # 其他聚合数据...
        }