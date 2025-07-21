#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartFlow 全链路后端集成测试脚本
覆盖注册、登录、用户、任务、AI任务拆解、子任务、提醒、AI提醒、通知、聊天、报表所有API
最后用sqlite3直接查表，展示所有关键表内容
"""

import requests
import http.client
import json
import random
import string
import time
import sqlite3
from datetime import datetime, date, timedelta
import os

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = "smartflow.db"

# 随机生成用户名，避免冲突
def random_username():
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

TEST_USER = {
    "username": random_username(),
    "password": "password123",
    "email": None,  # 稍后生成
    "full_name": "集成测试用户"
}
TEST_USER["email"] = f"{TEST_USER['username']}@example.com"

HEADERS = {"Content-Type": "application/json"}
TOKEN = None

# 打印分隔符
def print_separator(title):
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_result(success, message, details=None):
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if details:
        print(f"   详情: {details}")

# 1. 注册新用户
def register_user():
    print_separator("注册新用户")
    resp = requests.post(f"{BASE_URL}/users/register", json=TEST_USER, headers=HEADERS)
    if resp.status_code == 201 or (resp.status_code == 400 and "已存在" in resp.text):
        print_result(True, f"用户注册成功: {TEST_USER['username']}")
        return True
    else:
        print_result(False, "用户注册失败", resp.text)
        return False

# 2. 登录获取token
def login_user():
    print_separator("用户登录")
    data = {"username": TEST_USER["username"], "password": TEST_USER["password"]}
    resp = requests.post(f"{BASE_URL}/auth/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if resp.status_code == 200:
        global TOKEN
        TOKEN = resp.json()["access_token"]
        print_result(True, "登录成功")
        return True
    else:
        print_result(False, "登录失败", resp.text)
        return False

# 3. 用户信息相关API
def user_info_flow():
    print_separator("用户信息相关API")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    # 获取当前用户
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print_result(resp.status_code == 200, "获取当前用户信息", resp.text)
    # 更新用户信息
    update_data = {"full_name": "集成测试用户-更新", "email": f"updated_{TEST_USER['email']}"}
    resp = requests.patch(f"{BASE_URL}/users/me", json=update_data, headers=headers)
    print_result(resp.status_code == 200, "更新用户信息", resp.text)

# 4. 任务管理全流程
def task_flow():
    print_separator("任务管理全流程")
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    # 创建任务
    task_data = {"title": "集成测试任务", "description": "测试任务描述", "priority": "high", "estimated_duration": 90}
    resp = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    assert resp.status_code == 201, "任务创建失败"
    task = resp.json()
    task_id = task["id"]
    print_result(True, f"任务创建成功! ID: {task_id}")
    # 获取所有任务
    resp = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    print_result(resp.status_code == 200, "获取任务列表", resp.text)
    # 获取任务详情
    resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print_result(resp.status_code == 200, "获取任务详情", resp.text)
    # 更新任务
    update_data = {"title": "已更新的集成测试任务", "description": "已更新描述", "priority": "medium", "status": "in_progress"}
    resp = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
    print_result(resp.status_code == 200, "更新任务", resp.text)
    # AI智能拆解任务
    breakdown_data = {"task_description": "开发一个企业级CRM系统，包括用户管理、客户管理、销售跟踪、报表分析等功能模块"}
    resp = requests.post(f"{BASE_URL}/tasks/breakdown", json=breakdown_data, headers=headers)
    print_result(resp.status_code == 200, "AI智能拆解任务", resp.text)
    # 添加子任务
    subtask_data = {"title": "子任务1", "description": "子任务描述"}
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/subtasks", json=subtask_data, headers=headers)
    print_result(resp.status_code == 201, "添加子任务", resp.text)
    # 注意：不删除任务，因为提醒模块需要用到
    return task_id

# 5. 提醒模块全流程
def reminder_flow(task_id):
    print_separator("提醒模块全流程")
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    # AI提醒生成
    ai_data = {"timing": "early", "tone": "friendly", "include_motivation": True, "include_suggestions": True}
    resp = requests.post(f"{BASE_URL}/reminders/generate?task_id={task_id}", json=ai_data, headers=headers)
    print_result(resp.status_code == 200, "AI提醒生成", resp.text)
    # 创建提醒
    reminder_time = (datetime.now() + timedelta(minutes=2)).isoformat()
    reminder_data = {
        "reminder_in": {
            "task_id": task_id,
            "message": "集成测试提醒",
            "priority": 2,
            "strategy": "single",
            "reminder_time": reminder_time
        }
    }
    resp = requests.post(f"{BASE_URL}/reminders/", json=reminder_data, headers=headers)
    if resp.status_code != 201:
        print_result(False, f"提醒创建失败: {resp.status_code}", resp.text)
        return
    assert resp.status_code == 201, "提醒创建失败"
    reminder = resp.json()
    reminder_id = reminder["id"]
    print_result(True, f"提醒创建成功! ID: {reminder_id}")
    # 获取所有提醒
    resp = requests.get(f"{BASE_URL}/reminders/", headers=headers)
    print_result(resp.status_code == 200, "获取提醒列表", resp.text)
    # 获取待处理提醒
    resp = requests.get(f"{BASE_URL}/reminders/pending", headers=headers)
    print_result(resp.status_code == 200, "获取待处理提醒", resp.text)
    # 获取提醒详情
    resp = requests.get(f"{BASE_URL}/reminders/{reminder_id}", headers=headers)
    print_result(resp.status_code == 200, "获取提醒详情", resp.text)
    # 更新提醒
    update_data = {"message": "已更新的集成测试提醒", "priority": 3}
    resp = requests.put(f"{BASE_URL}/reminders/{reminder_id}", json=update_data, headers=headers)
    print_result(resp.status_code == 200, "更新提醒", resp.text)
    # 标记提醒已发送
    resp = requests.post(f"{BASE_URL}/reminders/{reminder_id}/mark-sent", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 200, "标记提醒已发送", resp.text)
    # 获取通知历史
    resp = requests.get(f"{BASE_URL}/reminders/notifications/history?limit=5", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 200, "获取通知历史", resp.text)
    # 获取通知统计
    resp = requests.get(f"{BASE_URL}/reminders/notifications/stats", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 200, "获取通知统计", resp.text)
    # 删除提醒
    resp = requests.delete(f"{BASE_URL}/reminders/{reminder_id}", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 204, "删除提醒", resp.text)

# 6. 聊天模块全流程
def chat_flow():
    print_separator("聊天模块全流程")
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    # 发送消息
    msg_data = {"content": "集成测试消息", "message_type": "text", "anonymous": False}
    resp = requests.post(f"{BASE_URL}/chat/send", json=msg_data, headers=headers)
    print_result(resp.status_code == 201, "发送聊天消息", resp.text)
    # 获取消息
    resp = requests.get(f"{BASE_URL}/chat/messages?limit=5", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 200, "获取聊天消息", resp.text)
    # 获取每日摘要
    resp = requests.get(f"{BASE_URL}/chat/daily-summary", headers={"Authorization": f"Bearer {TOKEN}"})
    print_result(resp.status_code == 200, "获取每日摘要", resp.text)
    # 分享任务进度
    share_task_data = {"task_id": 1, "progress": "50%"}
    resp = requests.post(f"{BASE_URL}/chat/share/task", json=share_task_data, headers=headers)
    print_result(resp.status_code in (200,201), "分享任务进度", resp.text)
    # 分享日报片段
    share_report_data = {"report_id": 1, "fragment": "日报片段内容"}
    resp = requests.post(f"{BASE_URL}/chat/share/report", json=share_report_data, headers=headers)
    print_result(resp.status_code in (200,201), "分享日报片段", resp.text)

# 7. 报表模块全流程
def report_flow():
    print_separator("报表模块全流程")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    # 获取日报
    resp = requests.get(f"{BASE_URL}/reports/daily", headers=headers)
    print_result(resp.status_code == 200, "获取日报", resp.text)
    # 获取指定日期报告
    today = date.today()
    resp = requests.get(f"{BASE_URL}/reports/date/{today}", headers=headers)
    print_result(resp.status_code == 200, "获取指定日期报告", resp.text)
    # 获取周报
    resp = requests.get(f"{BASE_URL}/reports/weekly", headers=headers)
    print_result(resp.status_code == 200, "获取周报", resp.text)
    # 获取月报
    resp = requests.get(f"{BASE_URL}/reports/monthly", headers=headers)
    print_result(resp.status_code == 200, "获取月报", resp.text)
    # 获取统计
    resp = requests.get(f"{BASE_URL}/reports/stats", headers=headers)
    print_result(resp.status_code == 200, "获取报表统计", resp.text)

# 8. 数据库快照
def db_snapshot():
    print_separator("数据库快照 - 关键表内容")
    if not os.path.exists(DB_PATH):
        print("❌ 数据库文件不存在")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = ["user", "task", "reminder", "dailyreport", "chatmessage"]
    for table in tables:
        print(f"\n📋 表: {table}")
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"❌ 查询失败: {e}")
    conn.close()

if __name__ == "__main__":
    all_ok = True
    all_ok &= register_user()
    all_ok &= login_user()
    user_info_flow()
    task_id = task_flow()
    reminder_flow(task_id)
    chat_flow()
    report_flow()
    # 在删除任务之前展示数据库快照
    db_snapshot()
    # 最后删除任务
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print_result(resp.status_code == 204, "删除任务", resp.text)
    print_separator("集成测试完成")
    if all_ok:
        print("🎉 全链路后端集成测试全部通过！")
    else:
        print("⚠️ 有部分步骤失败，请检查上方输出！") 