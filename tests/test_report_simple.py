#!/usr/bin/env python3
"""
简单的report模块测试
检查是否有无限嵌套问题
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api/v1"

def test_report_simple():
    """简单测试report模块"""
    print("🔍 开始测试report模块...")
    
    # 1. 用户登录
    print("\n1. 用户登录")
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,  # 使用form data而不是JSON
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return False
    
    access_token = response.json()["access_token"]
    print("✅ 登录成功!")
    
    # 2. 测试获取日报
    print("\n2. 测试获取日报")
    try:
        response = requests.get(
            f"{BASE_URL}/reports/daily",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            report = response.json()
            print("✅ 日报获取成功!")
            print(f"   报告ID: {report.get('id')}")
            print(f"   总结: {report.get('summary', 'N/A')[:50]}...")
            print(f"   完成任务: {report.get('tasks_completed', 0)}")
            print(f"   待处理任务: {report.get('tasks_pending', 0)}")
        else:
            print(f"❌ 日报获取失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 日报测试异常: {str(e)}")
    
    # 3. 测试获取指定日期报告
    print("\n3. 测试获取指定日期报告")
    try:
        today = date.today()
        response = requests.get(
            f"{BASE_URL}/reports/date/{today}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            report = response.json()
            print("✅ 指定日期报告获取成功!")
            print(f"   报告日期: {report.get('report_date')}")
        else:
            print(f"❌ 指定日期报告获取失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 指定日期报告测试异常: {str(e)}")
    
    # 4. 测试报告统计
    print("\n4. 测试报告统计")
    try:
        response = requests.get(
            f"{BASE_URL}/reports/stats",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ 报告统计获取成功!")
            print(f"   总报告数: {stats.get('total_reports', 0)}")
        else:
            print(f"❌ 报告统计获取失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 报告统计测试异常: {str(e)}")
    
    print("\n✅ report模块测试完成!")

if __name__ == "__main__":
    test_report_simple() 