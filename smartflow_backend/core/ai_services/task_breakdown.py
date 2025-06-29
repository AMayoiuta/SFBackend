import httpx
from typing import List, Dict, Any, Optional
import json

from core.config import settings


class AITaskService:
    """蓝心大模型AI服务封装"""

    def __init__(self):
        self.api_key = settings.AI_MODEL_API_KEY
        self.api_url = settings.AI_MODEL_API_URL

    async def _call_model_api(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """调用AI大模型API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["text"]
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e}")
            raise
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
            raise
        except Exception as e:
            print(f"其他错误: {e}")
            raise

    def _build_task_breakdown_prompt(self, task_description: str, user_preferences: Dict = None) -> str:
        """构建任务拆解的提示词"""
        prompt = f"""
        任务: {task_description}
        
        请将上述任务拆解为合理的子任务和执行步骤，并根据优先级排序。
        返回JSON格式如下:
        {{
            "main_task": "任务标题",
            "description": "任务详细描述",
            "estimated_duration": "预计完成总时间(分钟)",
            "priority": "优先级(1-10)",
            "subtasks": [
                {{
                    "title": "子任务1标题",
                    "description": "子任务1描述",
                    "order": 1,
                    "estimated_duration": "预计时间(分钟)"
                }},
                ...
            ]
        }}
        """
        
        if user_preferences:
            prompt += f"\n用户偏好:\n{json.dumps(user_preferences, ensure_ascii=False, indent=2)}"
        
        return prompt

    async def breakdown_task(self, task_description: str, user_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """拆解任务为子任务和执行步骤"""
        prompt = self._build_task_breakdown_prompt(task_description, user_preferences)
        response_text = await self._call_model_api(prompt)
        
        try:
            # 提取JSON部分
            json_str = response_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
                
            task_data = json.loads(json_str)
            return task_data
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response_text}")
            # 返回一个基本结构，防止整个流程中断
            return {
                "main_task": task_description,
                "description": "解析错误，请重试",
                "estimated_duration": 0,
                "priority": 5,
                "subtasks": []
            }


# 单例实例
ai_task_service = AITaskService() 