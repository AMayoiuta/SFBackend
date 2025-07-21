#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试本地通知系统
无需外部配置，开箱即用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
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

def test_local_notification_system():
    """测试本地通知系统"""
    print_separator("开始本地通知系统测试")
    
    # 1. 测试用户登录
    print("1. 测试用户登录")
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
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    token_data = response.json()
    access_token = token_data["access_token"]
    print("✅ 用户登录成功!")
    
    # 2. 创建测试任务
    print("\n2. 创建测试任务")
    task_data = {
        "title": "本地通知测试任务",
        "description": "这是一个用于测试本地通知系统的任务",
        "priority": "high",
        "estimated_duration": 60
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
        print(f"❌ 任务创建失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    task = response.json()
    task_id = task["id"]
    print(f"✅ 任务创建成功! ID: {task_id}")
    
    # 3. 创建带本地通知的提醒
    print("\n3. 创建带本地通知的提醒")
    reminder_time = datetime.now() + timedelta(minutes=1)  # 1分钟后提醒
    
    reminder_data = {
        "reminder_in": {
            "task_id": task_id,
            "message": "这是一个测试提醒，用于验证本地通知系统是否正常工作。",
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
        print(f"❌ 提醒创建失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    reminder = response.json()
    reminder_id = reminder["id"]
    print(f"✅ 提醒创建成功! ID: {reminder_id}")
    
    # 4. 测试标记提醒已发送（触发本地通知）
    print("\n4. 测试标记提醒已发送（触发本地通知）")
    response = requests.post(
        f"{BASE_URL}/reminders/{reminder_id}/mark-sent",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ 标记提醒已发送失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    print("✅ 提醒已标记为已发送，本地通知已触发!")
    
    # 5. 检查通知历史文件
    print("\n5. 检查通知历史文件")
    import pathlib
    notifications_dir = pathlib.Path("notifications")
    
    if notifications_dir.exists():
        history_file = notifications_dir / "notification_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            print(f"✅ 通知历史文件存在，包含 {len(history)} 条记录")
            
            # 显示最新的通知
            if history:
                latest = history[-1]
                print(f"最新通知: {latest.get('task_title', 'N/A')}")
                print(f"消息: {latest.get('message', 'N/A')}")
        else:
            print("⚠️ 通知历史文件不存在")
    else:
        print("⚠️ 通知目录不存在")
    
    # 6. 测试AI提醒生成
    print("\n6. 测试AI提醒生成")
    ai_data = {
        "task_info": {
            "title": "AI提醒测试任务",
            "description": "这是一个用于测试AI提醒生成的任务",
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "pending",
            "estimated_duration": 120
        },
        "strategy": "motivational"
    }
    
    response = requests.post(
        f"{BASE_URL}/reminders/generate",
        json=ai_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    if response.status_code == 200:
        ai_result = response.json()
        print("✅ AI提醒生成成功!")
        print(f"标题: {ai_result.get('title', 'N/A')}")
        print(f"消息: {ai_result.get('message', 'N/A')[:100]}...")
    else:
        print(f"⚠️ AI提醒生成失败: {response.status_code}")
        print(f"响应: {response.text}")
    
    print("\n" + "="*60)
    print("🎉 本地通知系统测试完成!")
    print("="*60)
    print("📋 功能说明:")
    print("1. 本地通知: 无需配置SMTP，直接在控制台显示")
    print("2. 通知历史: 自动保存到 notifications/ 目录")
    print("3. WebSocket: 支持实时通知（如果用户在线）")
    print("4. AI生成: 支持智能提醒内容生成")
    print("5. 开箱即用: 无需任何外部配置")
    
    return True

if __name__ == "__main__":
    try:
        test_local_notification_system()
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 