# smartflow_backend/core/ai_services/task_breakdown.py
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, ValidationError
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from smartflow_backend.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class SubtaskBreakdown(BaseModel):
    """单个子任务分解模型"""
    title: str
    description: Optional[str] = None
    order: Optional[int] = None  # 用于子任务排序

class TaskBreakdownResponse(BaseModel):
    """AI分解任务的响应模型"""
    subtasks: List[SubtaskBreakdown]
    reasoning: Optional[str] = None  # AI的推理过程
    confidence_score: Optional[float] = None  # 分解结果置信度

class TaskBreakdownError(Exception):
    """任务分解异常基类"""
    pass

class TaskBreakdownService:
    """任务分解服务"""
    
    def __init__(self):
        self.api_url = settings.AI_TASK_BREAKDOWN_URL
        self.api_key = settings.AI_API_KEY
        self.timeout = settings.AI_API_TIMEOUT
        
    def _build_payload(self, task_description: str) -> dict:
        """构建优化后的提示词模板"""
        return {
            "model": "gpt-4-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是智能任务规划专家，请将用户任务分解为可执行的原子子任务。\n"
                        "**返回格式要求**:\n"
                        "- 必须使用纯JSON格式\n"
                        "- 包含'subtasks'数组，每个元素包含'title'(字符串), 'description'(字符串), 'order'(整数)\n"
                        "- 可选的'reasoning'字段解释分解逻辑\n"
                        "- 可选的'confidence_score'表示结果置信度(0-1)\n\n"
                        "**任务分解原则**:\n"
                        "1. 每个子任务应是可独立执行的原子操作\n"
                        "2. 保持合理的分解粒度(5-15个子任务)\n"
                        "3. 子任务按执行顺序排列\n"
                        "4. 使用用户原始语言描述\n\n"
                        "**示例输出**:\n"
                        "{\"subtasks\":["
                        "{\"title\":\"需求分析\",\"description\":\"明确核心需求\",\"order\":1},"
                        "...],"
                        "\"reasoning\":\"...\","
                        "\"confidence_score\":0.95}"
                    )
                },
                {
                    "role": "user",
                    "content": f"请分解以下任务: {task_description}"
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"}
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(httpx.RequestError) | 
            retry_if_exception_type(httpx.HTTPStatusError)
        ),
        reraise=True
    )
    async def _call_ai_api(self, payload: dict) -> dict:
        """调用AI API并处理重试逻辑"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, raw_response: dict) -> TaskBreakdownResponse:
        """解析并验证AI响应"""
        try:
            # 尝试从不同位置提取JSON内容
            if "choices" in raw_response and len(raw_response["choices"]) > 0:
                content = raw_response["choices"][0]["message"]["content"]
                response_data = json.loads(content)
            elif "output" in raw_response:
                response_data = raw_response["output"]
            else:
                response_data = raw_response
            
            return TaskBreakdownResponse(**response_data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"响应解析失败: {str(e)}")
            raise TaskBreakdownError(f"无效的AI响应格式: {str(e)}") from e
    
    async def breakdown_task(self, task_description: str) -> TaskBreakdownResponse:
        """
        分解主任务为子任务
        
        :param task_description: 任务描述文本
        :return: 验证后的分解结果
        :raises TaskBreakdownError: 分解失败时抛出
        """
        if not task_description.strip():
            raise ValueError("任务描述不能为空")
            
        logger.info(f"开始分解任务: {task_description[:50]}...")
        
        try:
            payload = self._build_payload(task_description)
            raw_response = await self._call_ai_api(payload)
            parsed = self._parse_response(raw_response)
            
            # 后处理：确保子任务顺序
            if parsed.subtasks:
                for i, subtask in enumerate(parsed.subtasks, 1):
                    subtask.order = subtask.order or i
            
            logger.info(f"任务分解成功，生成{len(parsed.subtasks)}个子任务")
            return parsed
        except Exception as e:
            logger.exception("任务分解失败")
            raise TaskBreakdownError(f"任务分解失败: {str(e)}") from e

# 使用示例 (实际使用时通过依赖注入调用)
# service = TaskBreakdownService()
# result = await service.breakdown_task("开发用户管理模块")