"""
报告生成器模块
负责收集数据、生成AI洞察和创建报告
"""
import logging
import traceback
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import json
import httpx

# 设置详细的调试日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("report_generator")
logger.setLevel(logging.DEBUG)

# 导入基础配置
from smartflow_backend.core.config import settings

class ReportGenerator:
    def __init__(self):
        try:
            logger.debug("初始化ReportGenerator")
            self.ai_api_url = settings.VIVO_AIGC_URL
            self.app_id = settings.VIVO_APP_ID
            self.app_key = settings.VIVO_APP_KEY
            logger.debug(f"AI API URL: {self.ai_api_url}")
        except Exception as e:
            logger.error(f"初始化ReportGenerator失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def collect_daily_data(self, user_id: int, report_date: date, db) -> Dict[str, Any]:
        """收集每日报告数据"""
        try:
            logger.debug(f"开始收集日报数据: user_id={user_id}, date={report_date}")
            # 直接导入模型，避免循环依赖
            from smartflow_backend.db.models import Task, TaskLog
            
            start_date = datetime.combine(report_date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            logger.debug(f"查询时间范围: {start_date} 至 {end_date}")
            
            # 查询当天的任务日志
            task_logs = db.query(TaskLog).filter(
                TaskLog.start_time >= start_date,
                TaskLog.start_time < end_date,
                Task.owner_id == user_id
            ).join(Task).all()
            
            logger.debug(f"找到任务日志数量: {len(task_logs)}")
            
            # 查询当天的任务完成情况
            completed_tasks = db.query(Task).filter(
                Task.status == "completed",
                Task.completed_at >= start_date,
                Task.completed_at < end_date,
                Task.owner_id == user_id
            ).all()
            
            logger.debug(f"找到已完成任务数量: {len(completed_tasks)}")
            
            pending_tasks = db.query(Task).filter(
                Task.status.in_(["pending", "in_progress"]),
                Task.owner_id == user_id
            ).all()
            
            logger.debug(f"找到待处理任务数量: {len(pending_tasks)}")
            
            # 计算统计数据
            total_time = sum(log.duration or 0 for log in task_logs) // 60  # 转换为分钟
            task_count = len(completed_tasks)
            avg_duration = total_time / task_count if task_count > 0 else 0
            
            # 识别重要任务
            important_tasks = [task.title for task in completed_tasks if task.priority in ["high", "urgent"]]
            
            result = {
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
            
            logger.debug(f"日报数据收集完成: {result}")
            return result
        except Exception as e:
            logger.error(f"收集日报数据时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def generate_ai_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI生成报告洞察"""
        try:
            logger.debug("开始生成AI洞察")
            if not self.ai_api_url or not self.app_id or not self.app_key:
                logger.warning("AI服务未配置，使用默认报告")
                return self.default_report(data)
            
            prompt = self.build_insight_prompt(data)
            headers = {
                "app-id": self.app_id,
                "app-key": self.app_key,
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": prompt,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            logger.debug(f"发送AI API请求: {self.ai_api_url}")
            
            async with httpx.AsyncClient(timeout=settings.AI_API_TIMEOUT) as client:
                response = await client.post(self.ai_api_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # 提取AI生成的JSON
                ai_output = result["choices"][0]["text"].strip()
                if ai_output.startswith("```json"):
                    ai_output = ai_output[7:]
                if ai_output.endswith("```"):
                    ai_output = ai_output[:-3]
                
                insights = json.loads(ai_output)
                logger.debug(f"AI洞察生成成功: {insights}")
                return insights
        
        except Exception as e:
            logger.error(f"AI报告生成失败: {str(e)}")
            logger.error(traceback.format_exc())
            return self.default_report(data)
    
    def build_insight_prompt(self, data: Dict[str, Any]) -> str:
        """构建AI提示词"""
        try:
            logger.debug("构建AI提示词")
            prompt = f"""
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
            return prompt
        except Exception as e:
            logger.error(f"构建AI提示词时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def default_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """默认报告模板（当AI服务不可用时）"""
        try:
            logger.debug("使用默认报告模板")
            return {
                "summary": f"在{data['date']}完成了{data['tasks_completed']}个任务，用时{data['total_time_spent']}分钟。",
                "progress_analysis": "整体进度良好，但部分任务耗时较长。",
                "deviation_analysis": "有3个任务未按计划完成。",
                "optimization_suggestions": "建议优先处理重要任务并合理分配时间。",
                "ai_insights": "您在上午时段工作效率最高。",
                "next_steps": ["审查未完成任务", "规划明日优先级", "优化时间分配"]
            }
        except Exception as e:
            logger.error(f"生成默认报告时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def aggregate_weekly_data(self, user_id: int, start_date: date, db) -> Dict[str, Any]:
        """聚合周报数据"""
        try:
            logger.debug(f"开始聚合周报数据: user_id={user_id}, start_date={start_date}")
            # 直接导入模型，避免循环依赖
            from smartflow_backend.db.models import Task, TaskLog
            
            # 计算周的时间范围
            end_date = start_date + timedelta(days=7)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            logger.debug(f"周报查询时间范围: {start_datetime} 至 {end_datetime}")
            
            # 查询本周的任务日志
            task_logs = db.query(TaskLog).filter(
                TaskLog.start_time >= start_datetime,
                TaskLog.start_time < end_datetime,
                Task.owner_id == user_id
            ).join(Task).all()
            
            # 查询本周完成的任务
            completed_tasks = db.query(Task).filter(
                Task.status == "completed",
                Task.completed_at >= start_datetime,
                Task.completed_at < end_datetime,
                Task.owner_id == user_id
            ).all()
            
            # 查询待处理任务
            pending_tasks = db.query(Task).filter(
                Task.status.in_(["pending", "in_progress"]),
                Task.owner_id == user_id
            ).all()
            
            # 计算统计数据
            total_time = sum(log.duration or 0 for log in task_logs) // 60
            task_count = len(completed_tasks)
            avg_duration = total_time / task_count if task_count > 0 else 0
            
            # 识别重要任务
            important_tasks = [task.title for task in completed_tasks if task.priority in ["high", "urgent"]]
            
            result = {
                "summary": f"本周完成了{len(completed_tasks)}个任务，用时{total_time}分钟。",
                "tasks_completed": len(completed_tasks),
                "tasks_pending": len(pending_tasks),
                "total_time_spent": total_time,
                "avg_task_duration": round(avg_duration, 1),
                "important_tasks": important_tasks,
                "date": start_date.isoformat(),
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
            
            logger.debug(f"周报数据聚合完成: {result}")
            return result
        except Exception as e:
            logger.error(f"聚合周报数据时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def aggregate_monthly_data(self, user_id: int, month: int, year: int, db) -> Dict[str, Any]:
        """聚合月报数据"""
        try:
            logger.debug(f"开始聚合月报数据: user_id={user_id}, month={month}, year={year}")
            # 直接导入模型，避免循环依赖
            from smartflow_backend.db.models import Task, TaskLog
            
            # 计算月的时间范围
            month_start = date(year, month, 1)
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            
            start_datetime = datetime.combine(month_start, datetime.min.time())
            end_datetime = datetime.combine(next_month, datetime.min.time())
            
            logger.debug(f"月报查询时间范围: {start_datetime} 至 {end_datetime}")
            
            # 查询本月的任务日志
            task_logs = db.query(TaskLog).filter(
                TaskLog.start_time >= start_datetime,
                TaskLog.start_time < end_datetime,
                Task.owner_id == user_id
            ).join(Task).all()
            
            # 查询本月完成的任务
            completed_tasks = db.query(Task).filter(
                Task.status == "completed",
                Task.completed_at >= start_datetime,
                Task.completed_at < end_datetime,
                Task.owner_id == user_id
            ).all()
            
            # 查询待处理任务
            pending_tasks = db.query(Task).filter(
                Task.status.in_(["pending", "in_progress"]),
                Task.owner_id == user_id
            ).all()
            
            # 计算统计数据
            total_time = sum(log.duration or 0 for log in task_logs) // 60
            task_count = len(completed_tasks)
            avg_duration = total_time / task_count if task_count > 0 else 0
            
            # 识别重要任务
            important_tasks = [task.title for task in completed_tasks if task.priority in ["high", "urgent"]]
            
            result = {
                "summary": f"本月完成了{len(completed_tasks)}个任务，用时{total_time}分钟。",
                "tasks_completed": len(completed_tasks),
                "tasks_pending": len(pending_tasks),
                "total_time_spent": total_time,
                "avg_task_duration": round(avg_duration, 1),
                "important_tasks": important_tasks,
                "date": month_start.isoformat(),
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
            
            logger.debug(f"月报数据聚合完成: {result}")
            return result
        except Exception as e:
            logger.error(f"聚合月报数据时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise