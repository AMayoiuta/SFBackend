 # smartflow_backend/core/ai_services/reminder_generator.py
import json
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from smartflow_backend.core.config import settings
from smartflow_backend.core.ai_services.auth_util import gen_sign_headers

# 配置日志
logger = logging.getLogger(__name__)

class ReminderContent(BaseModel):
    """智能提醒内容模型"""
    title: str
    message: str
    urgency_level: str  # low, medium, high, urgent
    suggested_action: Optional[str] = None
    motivation_quote: Optional[str] = None

class ReminderStrategy(BaseModel):
    """提醒策略模型"""
    timing: str  # early, on_time, late
    tone: str  # friendly, professional, urgent
    include_motivation: bool = True
    include_suggestions: bool = True

class ReminderGeneratorError(Exception):
    """提醒生成异常基类"""
    pass

class ReminderGeneratorService:
    """智能提醒生成服务"""
    
    def __init__(self):
        self.api_url = str(settings.VIVO_AIGC_URL)  # 转换为字符串
        self.app_id = settings.VIVO_APP_ID
        self.app_key = settings.VIVO_APP_KEY
        self.timeout = settings.AI_API_TIMEOUT
        
    def _build_payload(self, task_info: Dict[str, Any], strategy: ReminderStrategy) -> dict:
        """构建蓝心大模型API请求"""
        
        # 根据策略调整提示词
        tone_mapping = {
            "friendly": "友好温和",
            "professional": "专业正式", 
            "urgent": "紧急提醒"
        }
        
        timing_mapping = {
            "early": "提前提醒",
            "on_time": "准时提醒",
            "late": "延迟提醒"
        }
        
        tone = tone_mapping.get(strategy.tone, "友好温和")
        timing = timing_mapping.get(strategy.timing, "准时提醒")
        
        system_prompt = f"""你是智能任务提醒助手，需要为用户生成个性化的任务提醒。

**提醒风格**: {tone}
**提醒时机**: {timing}

**返回格式要求**:
- 必须使用纯JSON格式
- 包含以下字段:
  - "title": 提醒标题(简洁有力)
  - "message": 提醒正文(详细说明)
  - "urgency_level": 紧急程度(low/medium/high/urgent)
  - "suggested_action": 建议行动(可选)
  - "motivation_quote": 激励语录(可选)

**生成原则**:
1. 根据任务优先级调整紧急程度
2. 根据用户习惯调整提醒风格
3. 提供具体可行的建议
4. 适当加入激励元素
5. 保持简洁明了

**示例输出**:
{{
  "title": "任务即将到期",
  "message": "您的任务'项目报告'将在2小时后到期，建议立即开始处理。",
  "urgency_level": "high",
  "suggested_action": "建议先列出报告大纲，然后逐步完善内容",
  "motivation_quote": "每一个伟大的成就都始于一个决定。"
}}"""

        user_prompt = f"""请为以下任务生成智能提醒:

任务信息:
- 标题: {task_info.get('title', '未命名任务')}
- 描述: {task_info.get('description', '无描述')}
- 优先级: {task_info.get('priority', 'medium')}
- 截止时间: {task_info.get('due_date', '未设置')}
- 当前状态: {task_info.get('status', 'pending')}
- 预计时长: {task_info.get('estimated_duration', '未知')}分钟

用户偏好:
- 提醒风格: {tone}
- 提醒时机: {timing}
- 包含激励: {'是' if strategy.include_motivation else '否'}
- 包含建议: {'是' if strategy.include_suggestions else '否'}

请生成个性化的提醒内容。"""

        return {
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "model": "vivo-BlueLM-TB-Pro",
            "sessionId": str(uuid.uuid4()),
            "extra": {
                "temperature": 0.7,
                "max_new_tokens": 512
            }
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
        """调用蓝心大模型-70B API"""
        # 生成请求参数
        request_id = str(uuid.uuid4())
        params = {"requestId": request_id}
        
        # 生成签名头
        headers = gen_sign_headers(
            self.app_id, 
            self.app_key, 
            "POST", 
            "/vivogpt/completions", 
            params
        )
        headers["Content-Type"] = "application/json"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}?requestId={request_id}",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, raw_response: dict) -> ReminderContent:
        """解析蓝心大模型响应"""
        try:
            # 检查响应状态
            if raw_response.get("code") != 0:
                error_msg = raw_response.get("msg", "未知错误")
                raise ReminderGeneratorError(f"AI服务错误: {error_msg}")
            
            # 提取内容
            data = raw_response.get("data", {})
            content = data.get("content", "")
            
            # 尝试解析JSON内容
            try:
                response_data = json.loads(content)
                return ReminderContent(**response_data)
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建一个简单的提醒内容
                return ReminderContent(
                    title="智能提醒",
                    message=content,
                    urgency_level="medium"
                )
                
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"响应解析失败: {str(e)}")
            raise ReminderGeneratorError(f"无效的AI响应格式: {str(e)}") from e
    
    async def generate_reminder(
        self, 
        task_info: Dict[str, Any], 
        strategy: ReminderStrategy
    ) -> ReminderContent:
        """
        生成智能提醒内容
        
        :param task_info: 任务信息字典
        :param strategy: 提醒策略
        :return: 生成的提醒内容
        :raises ReminderGeneratorError: 生成失败时抛出
        """
        logger.info(f"开始生成提醒内容，任务: {task_info.get('title', 'Unknown')}")
        
        try:
            payload = self._build_payload(task_info, strategy)
            raw_response = await self._call_ai_api(payload)
            reminder_content = self._parse_response(raw_response)
            
            logger.info(f"提醒内容生成成功: {reminder_content.title}")
            return reminder_content
        except Exception as e:
            logger.exception("提醒内容生成失败")
            raise ReminderGeneratorError(f"提醒内容生成失败: {str(e)}") from e
    
    def calculate_urgency_level(self, task_info: Dict[str, Any]) -> str:
        """根据任务信息计算紧急程度"""
        priority = task_info.get('priority', 'medium')
        due_date = task_info.get('due_date')
        
        if due_date:
            now = datetime.utcnow()
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            time_left = due_date - now
            
            if time_left < timedelta(hours=1):
                return 'urgent'
            elif time_left < timedelta(hours=6):
                return 'high'
            elif time_left < timedelta(days=1):
                return 'medium'
            else:
                return 'low'
        
        # 根据优先级判断
        priority_levels = {
            'urgent': 'urgent',
            'high': 'high', 
            'medium': 'medium',
            'low': 'low'
        }
        
        return priority_levels.get(priority, 'medium')

# 导出单例服务实例
ai_reminder_service = ReminderGeneratorService()