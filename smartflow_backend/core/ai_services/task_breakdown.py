# smartflow_backend/core/ai_services/task_breakdown.py
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, ValidationError, Field
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from smartflow_backend.core.config import settings
import uuid
from smartflow_backend.core.ai_services.auth_util import gen_sign_headers

# 配置日志
logger = logging.getLogger(__name__)

class SubtaskBreakdown(BaseModel):
    """单个子任务分解模型"""
    title: str
    description: Optional[str] = None
    order: Optional[int] = None  # 用于子任务排序

class TaskBreakdownResponse(BaseModel):
    """AI分解任务的响应模型，匹配API schema"""
    main_task: str = Field(..., description="主任务标题")
    description: str = Field(..., description="主任务描述")
    estimated_duration: int = Field(..., description="预计完成总时间(分钟)")
    priority: float = Field(..., description="优先级(1-10)")
    subtasks: List[dict] = Field(..., description="子任务列表")

class TaskBreakdownError(Exception):
    """任务分解异常基类"""
    pass

class TaskBreakdownService:
    """任务分解服务"""
    
    def __init__(self):
        # 使用蓝心大模型70B接口URL
        self.api_url = str(settings.VIVO_AIGC_URL)
        self.app_id = settings.VIVO_APP_ID
        # 提供给测试断言
        self.api_key = settings.AI_API_KEY
        # 兼容旧属性名
        self.app_key = self.api_key
        self.timeout = settings.AI_API_TIMEOUT
        
    def _build_payload(self, task_description: str, user_preferences: Optional[dict] = None) -> dict:
        """构建优化后的提示词模板"""
        # 使用蓝心大模型70B的completions接口Payload
        session_id = str(uuid.uuid4())
        # 构建提示词
        system_prompt = (
            "你是智能任务规划专家，请将用户任务分解为3-8个可执行的原子子任务。"
            "要求："
            "1. 每个子任务应该是独立的、可执行的"
            "2. 子任务标题要具体明确，避免与主任务重复"
            "3. 子任务按执行顺序排列，order从1开始"
            "4. 每个子任务包含'title','description','order'字段"
            "5. 返回纯JSON格式，包含subtasks数组"
        )
        user_prompt = f"请分解以下任务: {task_description}"
        prompt = system_prompt + "\n\n" + user_prompt
        return {
            "prompt": prompt,
            "model": "vivo-BlueLM-TB-Pro",
            "sessionId": session_id,
            "extra": {"temperature": 0.3, "max_new_tokens": 1024}
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
        # 使用签名头进行API调用
        request_id = str(uuid.uuid4())
        params = {"requestId": request_id}
        # 签名URI路径与参数，使用/vivogpt/completions
        headers = gen_sign_headers(
            self.app_id,
            self.app_key,
            "POST",
            "/vivogpt/completions",
            params
        )
        headers["Content-Type"] = "application/json"
        # 构建带请求ID的URL
        url = f"{self.api_url}?requestId={request_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, raw_response: dict) -> TaskBreakdownResponse:
        """解析并验证AI响应"""
        try:
            # 如果是VIVO大模型接口响应格式
            if "code" in raw_response:
                # 非0 code视为错误
                if raw_response.get("code") != 0:
                    msg = raw_response.get("msg", "Unknown error")
                    logger.error(f"VIVO AI服务错误: {msg}")
                    raise TaskBreakdownError(f"AI服务错误: {msg}")
                # 解析返回的内容字段
                data = raw_response.get("data", {})
                content = data.get("content", "")
                response_data = json.loads(content)
                logger.debug(f"解析后的response_data: {response_data}")
                # 如果返回的是列表，则视为直接的子任务列表
                if isinstance(response_data, list):
                    response_data = {"subtasks": response_data}
                # 如果返回的是单个字典且包含title等字段，则包装为列表
                elif isinstance(response_data, dict) and "title" in response_data:
                    response_data = {"subtasks": [response_data]}
                # 如果返回的字典没有subtasks字段，尝试包装
                elif isinstance(response_data, dict) and "subtasks" not in response_data:
                    response_data = {"subtasks": [response_data]}
                # 确保subtasks中的每个项目都有正确的order字段
                if "subtasks" in response_data:
                    for i, subtask in enumerate(response_data["subtasks"], 1):
                        # 确保subtask是字典类型
                        if isinstance(subtask, dict):
                            # 确保order是整数
                            if "order" in subtask:
                                try:
                                    subtask["order"] = int(subtask["order"])
                                except (ValueError, TypeError):
                                    subtask["order"] = i
                            else:
                                subtask["order"] = i
                        # 如果subtask不是字典，跳过处理
                        else:
                            logger.warning(f"跳过非字典类型的subtask: {subtask}")
                # 如果response_data只有subtasks，需要构造其他必需字段
                if "subtasks" in response_data and len(response_data) == 1:
                    # 从第一个子任务提取主任务信息
                    first_subtask = response_data["subtasks"][0] if response_data["subtasks"] else {}
                    # 确保first_subtask是字典
                    if not isinstance(first_subtask, dict):
                        first_subtask = {}
                    response_data.update({
                        "main_task": first_subtask.get("title", "主任务"),
                        "description": first_subtask.get("description", "任务描述"),
                        "estimated_duration": 120,  # 默认2小时
                        "priority": 7.0  # 默认优先级
                    })
                return TaskBreakdownResponse(**response_data)
            # OpenAI兼容格式
            if "choices" in raw_response and len(raw_response["choices"]) > 0:
                content = raw_response["choices"][0]["message"]["content"]
                response_data = json.loads(content)
                logger.debug(f"解析后的response_data: {response_data}")
                if isinstance(response_data, list):
                    response_data = {"subtasks": response_data}
                elif isinstance(response_data, dict) and "title" in response_data:
                    response_data = {"subtasks": [response_data]}
                elif isinstance(response_data, dict) and "subtasks" not in response_data:
                    response_data = {"subtasks": [response_data]}
                # 确保subtasks中的每个项目都有正确的order字段
                if "subtasks" in response_data:
                    for i, subtask in enumerate(response_data["subtasks"], 1):
                        # 确保subtask是字典类型
                        if isinstance(subtask, dict):
                            # 确保order是整数
                            if "order" in subtask:
                                try:
                                    subtask["order"] = int(subtask["order"])
                                except (ValueError, TypeError):
                                    subtask["order"] = i
                            else:
                                subtask["order"] = i
                        # 如果subtask不是字典，跳过处理
                        else:
                            logger.warning(f"跳过非字典类型的subtask: {subtask}")
                # 如果response_data只有subtasks，需要构造其他必需字段
                if "subtasks" in response_data and len(response_data) == 1:
                    # 从第一个子任务提取主任务信息
                    first_subtask = response_data["subtasks"][0] if response_data["subtasks"] else {}
                    # 确保first_subtask是字典
                    if not isinstance(first_subtask, dict):
                        first_subtask = {}
                    response_data.update({
                        "main_task": first_subtask.get("title", "主任务"),
                        "description": first_subtask.get("description", "任务描述"),
                        "estimated_duration": 120,  # 默认2小时
                        "priority": 7.0  # 默认优先级
                    })
                return TaskBreakdownResponse(**response_data)
            # 其他格式
            if "output" in raw_response:
                response_data = raw_response["output"]
            else:
                response_data = raw_response
            return TaskBreakdownResponse(**response_data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"响应解析失败: {str(e)}")
            raise TaskBreakdownError(f"无效的AI响应格式: {str(e)}") from e
    
    async def breakdown_task(self, task_description: str, user_preferences: Optional[dict] = None) -> TaskBreakdownResponse:
        """
        分解主任务为子任务
        
        :param task_description: 任务描述文本
        :param user_preferences: 用户偏好设置（可选）
        :return: 验证后的分解结果
        :raises TaskBreakdownError: 分解失败时抛出
        """
        if not task_description.strip():
            raise ValueError("任务描述不能为空")
            
        logger.info(f"开始分解任务: {task_description[:50]}...")
        
        try:
            # 构建请求payload
            payload = self._build_payload(task_description, user_preferences)
            logger.debug(f"任务拆解请求Payload: {payload}")
            # 调用AI API
            raw_response = await self._call_ai_api(payload)
            logger.debug(f"任务拆解Raw响应: {raw_response}")
            # 解析响应
            parsed = self._parse_response(raw_response)
            
            # 后处理：确保子任务顺序
            if parsed.subtasks:
                for i, subtask in enumerate(parsed.subtasks, 1):
                    # 确保subtask是字典类型，并且有order字段
                    if isinstance(subtask, dict):
                        subtask["order"] = subtask.get("order", i)
                    # 如果是SubtaskBreakdown对象
                    elif hasattr(subtask, "order"):
                        subtask.order = subtask.order or i
            
            logger.info(f"任务分解成功，生成{len(parsed.subtasks)}个子任务")
            return parsed
        except Exception as e:
            logger.exception("任务分解失败")
            raise TaskBreakdownError(f"任务分解失败: {str(e)}") from e

# 导出单例服务实例，供 API 路由调用
ai_task_service = TaskBreakdownService()