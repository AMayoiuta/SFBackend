"""
API配置文件

用于控制API的行为，包括：
1. 模型序列化选项
2. 调试选项
3. 性能优化选项
"""

from typing import Dict, Any

# API配置
API_CONFIG: Dict[str, Any] = {
    # 模型序列化选项
    "model_serialization": {
        # 是否使用简单字典代替嵌套模型（解决循环引用问题）
        "use_dict_for_nested_models": True,
        # 是否包含模型验证错误详情
        "include_validation_errors": True,
        # 是否在响应中包含模型的额外字段
        "exclude_unset": True,
    },
    
    # 调试选项
    "debug": {
        # 是否启用详细日志
        "verbose_logging": True,
        # 是否在响应中包含堆栈跟踪
        "include_stack_trace": False,
        # 最大递归深度
        "max_recursion_depth": 100,
    },
    
    # 性能优化选项
    "performance": {
        # 是否启用响应缓存
        "enable_response_cache": False,
        # 缓存过期时间（秒）
        "cache_expiry": 300,
        # 是否启用数据库连接池
        "enable_db_pool": True,
        # 数据库连接池大小
        "db_pool_size": 5,
    },
    
    # 安全选项
    "security": {
        # 是否启用请求限流
        "enable_rate_limiting": True,
        # 每分钟最大请求数
        "max_requests_per_minute": 100,
    }
} 