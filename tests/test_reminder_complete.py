#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SmartFlow 提醒模块完整测试流程
覆盖所有API端点和功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
from datetime import datetime, timedelta

# 测试配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "testuser",
    "password": "password123"
}

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_result(success, message, details=None):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if details:
        print(f"   详情: {details}")

def test_reminder_complete():
    """完整的提醒模块测试流程"""
    print_separator("开始 SmartFlow 提醒模块完整测试")
    
    # 测试结果记录
    test_results = {}
    
    # 1. 用户登录
    print("1. 用户登录")
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print_result(False, f"登录失败: {response.status_code}", response.text)
        return False
    
    token_data = response.json()
    access_token = token_data["access_token"]
    print_result(True, "用户登录成功!")
    test_results["login"] = True
    
    # 2. 创建测试任务
    print("\n2. 创建测试任务")
    task_data = {
        "title": "提醒模块完整测试任务",
        "description": "这是一个用于测试提醒模块完整功能的任务",
        "priority": "high",
        "estimated_duration": 120
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/",
        json=task_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    if response.status_code != 201:
        print_result(False, f"任务创建失败: {response.status_code}", response.text)
        return False
    
    task = response.json()
    task_id = task["id"]
    print_result(True, f"任务创建成功! ID: {task_id}")
    test_results["create_task"] = True
    
    # 3. 测试AI提醒生成
    print("\n3. 测试AI提醒生成")
    
    # 使用正确的参数格式：task_id作为query参数，strategy作为body参数
    # AI提醒生成需要timing和tone参数
    response = requests.post(
        f"{BASE_URL}/reminders/generate?task_id={task_id}",
        json={
            "timing": "early",
            "tone": "friendly",
            "include_motivation": True,
            "include_suggestions": True
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    if response.status_code == 200:
        ai_result = response.json()
        print_result(True, "AI提醒生成成功!")
        print(f"   AI内容: {ai_result.get('reminder_content', {}).get('message', 'N/A')[:100]}...")
        test_results["ai_generate"] = True
    else:
        print_result(False, f"AI提醒生成失败: {response.status_code}", response.text)
        test_results["ai_generate"] = False
    
    # 4. 创建提醒
    print("\n4. 创建提醒")
    reminder_time = datetime.now() + timedelta(minutes=2)
    
    reminder_data = {
        "reminder_in": {
            "task_id": task_id,
            "message": "这是一个测试提醒，用于验证提醒模块的完整功能。",
            "priority": 3,
            "strategy": "single",
            "reminder_time": reminder_time.isoformat()
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/reminders/",
        json=reminder_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    if response.status_code != 201:
        print_result(False, f"提醒创建失败: {response.status_code}", response.text)
        return False
    
    reminder = response.json()
    reminder_id = reminder["id"]
    print_result(True, f"提醒创建成功! ID: {reminder_id}")
    test_results["create_reminder"] = True
    
    # 5. 获取用户所有提醒
    print("\n5. 获取用户所有提醒")
    response = requests.get(
        f"{BASE_URL}/reminders/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        reminders = response.json()
        print_result(True, f"获取提醒列表成功! 共 {len(reminders)} 条提醒")
        test_results["get_reminders"] = True
    else:
        print_result(False, f"获取提醒列表失败: {response.status_code}", response.text)
        test_results["get_reminders"] = False
    
    # 6. 获取待处理提醒
    print("\n6. 获取待处理提醒")
    response = requests.get(
        f"{BASE_URL}/reminders/pending",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        pending_reminders = response.json()
        print_result(True, f"获取待处理提醒成功! 共 {len(pending_reminders)} 条待处理")
        test_results["get_pending_reminders"] = True
    else:
        print_result(False, f"获取待处理提醒失败: {response.status_code}", response.text)
        test_results["get_pending_reminders"] = False
    
    # 7. 获取特定提醒详情
    print(f"\n7. 获取提醒详情 (ID: {reminder_id})")
    response = requests.get(
        f"{BASE_URL}/reminders/{reminder_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        reminder_detail = response.json()
        print_result(True, f"获取提醒详情成功! 任务: {reminder_detail.get('task', {}).get('title', 'N/A')}")
        test_results["get_reminder_detail"] = True
    else:
        print_result(False, f"获取提醒详情失败: {response.status_code}", response.text)
        test_results["get_reminder_detail"] = False
    
    # 8. 更新提醒信息
    print(f"\n8. 更新提醒信息 (ID: {reminder_id})")
    update_data = {
        "message": "这是已更新的提醒消息，用于测试更新功能。",
        "priority": 4
    }
    
    response = requests.put(
        f"{BASE_URL}/reminders/{reminder_id}",
        json=update_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    if response.status_code == 200:
        updated_reminder = response.json()
        print_result(True, "提醒更新成功!")
        test_results["update_reminder"] = True
    else:
        print_result(False, f"提醒更新失败: {response.status_code}", response.text)
        test_results["update_reminder"] = False
    
    # 9. 标记提醒已发送（触发通知）
    print(f"\n9. 标记提醒已发送 (ID: {reminder_id})")
    response = requests.post(
        f"{BASE_URL}/reminders/{reminder_id}/mark-sent",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        sent_reminder = response.json()
        print_result(True, "提醒已标记为已发送，本地通知已触发!")
        test_results["mark_reminder_sent"] = True
    else:
        print_result(False, f"标记提醒已发送失败: {response.status_code}", response.text)
        test_results["mark_reminder_sent"] = False
    
    # 10. 获取通知历史
    print("\n10. 获取通知历史")
    response = requests.get(
        f"{BASE_URL}/reminders/notifications/history?limit=10",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        notifications = response.json()
        print_result(True, f"获取通知历史成功! 共 {len(notifications)} 条记录")
        if notifications:
            latest = notifications[0]
            print(f"   最新通知: {latest.get('task_title', 'N/A')}")
        test_results["get_notification_history"] = True
    else:
        print_result(False, f"获取通知历史失败: {response.status_code}", response.text)
        test_results["get_notification_history"] = False
    
    # 11. 获取通知统计
    print("\n11. 获取通知统计")
    response = requests.get(
        f"{BASE_URL}/reminders/notifications/stats",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_result(True, "获取通知统计成功!")
        print(f"   总通知数: {stats.get('total', 0)}")
        print(f"   提醒通知: {stats.get('reminders', 0)}")
        print(f"   系统通知: {stats.get('system', 0)}")
        print(f"   今日通知: {stats.get('today', 0)}")
        test_results["get_notification_stats"] = True
    else:
        print_result(False, f"获取通知统计失败: {response.status_code}", response.text)
        test_results["get_notification_stats"] = False
    
    # 12. 检查本地通知文件
    print("\n12. 检查本地通知文件")
    import pathlib
    notifications_dir = pathlib.Path("notifications")
    
    if notifications_dir.exists():
        history_file = notifications_dir / "notification_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            print_result(True, f"本地通知文件存在，包含 {len(history)} 条记录")
            test_results["local_notification_file"] = True
        else:
            print_result(False, "本地通知历史文件不存在")
            test_results["local_notification_file"] = False
    else:
        print_result(False, "本地通知目录不存在")
        test_results["local_notification_file"] = False
    
    # 13. 删除提醒
    print(f"\n13. 删除提醒 (ID: {reminder_id})")
    response = requests.delete(
        f"{BASE_URL}/reminders/{reminder_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 204:
        print_result(True, "提醒删除成功!")
        test_results["delete_reminder"] = True
    else:
        print_result(False, f"提醒删除失败: {response.status_code}", response.text)
        test_results["delete_reminder"] = False
    
    # 输出测试总结
    print_separator("测试结果总结")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if failed_tests == 0:
        print("\n🎉 所有测试通过! 提醒模块功能完整")
    else:
        print(f"\n⚠️ 有 {failed_tests} 个测试失败，需要检查相关功能")
    
    print_separator("提醒模块功能说明")
    print("✅ 已实现功能:")
    print("  - 提醒的创建、查询、更新、删除")
    print("  - AI智能提醒内容生成")
    print("  - 本地通知服务（日志、文件存储）")
    print("  - WebSocket实时推送支持")
    print("  - 通知历史和统计API")
    print("  - 提醒状态管理（待处理、已发送）")
    print("  - 智能提醒时间计算")
    print("\n📋 前端集成建议:")
    print("  - 使用 WebSocket 连接 /api/v1/chat/ws 接收实时通知")
    print("  - 调用 /reminders/notifications/history 获取通知历史")
    print("  - 使用浏览器 Notification API 实现弹窗提醒")
    print("  - 实现通知中心页面，支持已读/未读管理")
    
    return failed_tests == 0

if __name__ == "__main__":
    try:
        success = test_reminder_complete()
        if success:
            print("\n🎉 提醒模块测试完成，所有功能正常!")
        else:
            print("\n⚠️ 提醒模块测试完成，部分功能需要检查")
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 