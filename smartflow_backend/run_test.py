# run_tests.py (在项目根目录创建)
import sys
import os
import pytest

def main():
    # 添加项目根目录到 Python 路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 运行测试
    exit_code = pytest.main([
        "-v", 
        "test/unit/core/ai_services/test_task_breakdown.py"
    ])
    return exit_code

if __name__ == "__main__":
    sys.exit(main())