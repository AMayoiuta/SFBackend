# test/unit/core/ai_services/test_task_breakdown.py
import sys
import os
import pytest
import json
import httpx
from unittest.mock import AsyncMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

# 导入生产代码
from core.ai_services.task_breakdown import (
    TaskBreakdownService, TaskBreakdownError
)

# 测试fixture
@pytest.fixture
def breakdown_service(monkeypatch):
    """创建测试用的任务分解服务实例"""
    # 使用 monkeypatch 模拟配置
    monkeypatch.setattr('core.config.settings.AI_TASK_BREAKDOWN_URL', 'https://mock-api.com')
    monkeypatch.setattr('core.config.settings.AI_API_KEY', 'test-key')
    monkeypatch.setattr('core.config.settings.AI_API_TIMEOUT', 5)
    
    service = TaskBreakdownService()
    return service

# 测试用例
@pytest.mark.asyncio
async def test_successful_task_breakdown(breakdown_service):
    """测试任务分解成功场景"""
    # 模拟API响应
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "main_task": "开发用户管理系统",
                    "description": "实现用户注册、登录和管理功能",
                    "estimated_duration": 480,
                    "priority": 8.5,
                    "subtasks": [
                        {"title": "设计数据库模型", "description": "创建用户表和权限表", 
                         "estimated_duration": 120, "priority": 1}
                    ]
                })
            }
        }]
    }
    
    # 模拟HTTP请求
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        # 调用被测试方法
        result = await breakdown_service.breakdown_task("开发一个用户管理系统")
        
        # 验证结果
        assert result.main_task == "开发用户管理系统"
        assert result.estimated_duration == 480
        assert len(result.subtasks) == 1
        assert result.subtasks[0].title == "设计数据库模型"


def test_service_initialization(breakdown_service):
    """测试服务初始化"""
    assert breakdown_service.api_url == "https://mock-api.com"
    assert breakdown_service.api_key == "test-key"
    assert breakdown_service.timeout == 5
# 更多测试用例...