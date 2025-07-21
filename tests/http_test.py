#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用http.client测试SmartFlow API - 完整功能测试
测试所有4个模块：认证、用户管理、任务管理、聊天功能
"""

import http.client
import json
import time
import random
import string
import sys

# API主机和端口
HOST = "localhost"
PORT = 8000
BASE_PATH = "/api/v1"

# 测试用户凭据
TEST_USERNAME = "testuser"
TEST_PASSWORD = "password123"
TEST_EMAIL = "testuser@example.com"
TEST_FULL_NAME = "测试用户"

# 调试模式
DEBUG = True

def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 80 + "\n")

def debug_print(message):
    """打印调试信息"""
    if DEBUG:
        print(f"[DEBUG] {message}")

def print_response(conn, response, title="API响应"):
    """打印完整的响应信息"""
    print_separator()
    print(f"【{title}】")
    print(f"状态码: {response.status}")
    print(f"原因: {response.reason}")
    
    print("\n【响应头】")
    for header, value in response.getheaders():
        print(f"{header}: {value}")
    
    body = response.read().decode('utf-8')
    print("\n【响应体】")
    try:
        # 尝试解析为JSON
        json_data = json.loads(body)
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    except:
        # 如果不是JSON，打印原始文本
        print(body)
    print_separator()
    
    return body

def test_api_status():
    """测试API状态端点，获取可用路由信息"""
    print("1. 测试API状态端点")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/status")
        
        conn.request("GET", f"{BASE_PATH}/status")
        response = conn.getresponse()
        
        body = print_response(conn, response, "API状态响应")
        
        if response.status == 200:
            print("✅ 获取API状态成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取API状态失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_register_user():
    """测试用户注册"""
    print("2. 测试用户注册")
    
    user_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME
    }
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = json.dumps(user_data)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/users/register")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("POST", f"{BASE_PATH}/users/register", body=body, headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "用户注册响应")
        
        if response.status == 201:
            print("✅ 用户注册成功!")
            return json.loads(body)
        elif response.status in (400, 409):
            print(f"⚠️ 用户可能已存在，继续测试... (状态码: {response.status})")
            return {"message": "User may already exist"}
        else:
            print(f"❌ 用户注册失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_login(username=TEST_USERNAME, password=TEST_PASSWORD):
    """测试用户登录"""
    print("3. 测试用户登录")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        body = f"username={username}&password={password}"
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/auth/login")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("POST", f"{BASE_PATH}/auth/login", body=body, headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "用户登录响应")
        
        if response.status == 200:
            print("✅ 用户登录成功!")
            return json.loads(body).get("access_token")
        else:
            print(f"❌ 用户登录失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_get_current_user(token):
    """测试获取当前用户信息"""
    print("4. 测试获取当前用户信息")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/users/me")
        print(f"请求头: {headers}")
        
        conn.request("GET", f"{BASE_PATH}/users/me", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "获取当前用户信息响应")
        
        if response.status == 200:
            print("✅ 获取当前用户信息成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取当前用户信息失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_update_user(token):
    """测试更新用户信息"""
    print("5. 测试更新用户信息")
    
    update_data = {
        "full_name": f"更新后的{TEST_FULL_NAME}",
        "email": f"updated_{TEST_EMAIL}"
    }
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = json.dumps(update_data)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/users/me")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("PATCH", f"{BASE_PATH}/users/me", body=body, headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "更新用户信息响应")
        
        if response.status == 200:
            print("✅ 更新用户信息成功!")
            return json.loads(body)
        else:
            print(f"❌ 更新用户信息失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_create_task(token):
    """测试创建任务"""
    print("6. 测试创建任务")
    
    task_data = {
        "title": f"测试任务 {random.randint(1000, 9999)}",
        "description": "这是一个通过API测试创建的任务",
        "priority": "medium",
        "estimated_duration": 60
    }
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = json.dumps(task_data)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/tasks/")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("POST", f"{BASE_PATH}/tasks/", body=body, headers=headers)
        response = conn.getresponse()
        
        body_response = print_response(conn, response, "创建任务响应")
        
        if response.status == 201:
            print("✅ 任务创建成功!")
            return json.loads(body_response)
        else:
            print(f"❌ 任务创建失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_get_tasks(token):
    """测试获取任务列表"""
    print("7. 测试获取任务列表")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/tasks/")
        print(f"请求头: {headers}")
        
        conn.request("GET", f"{BASE_PATH}/tasks/", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "获取任务列表响应")
        
        if response.status == 200:
            print("✅ 获取任务列表成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取任务列表失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_get_task_detail(token, task_id):
    """测试获取单个任务详情"""
    print(f"8. 测试获取任务详情 (ID: {task_id})")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/tasks/{task_id}")
        print(f"请求头: {headers}")
        
        conn.request("GET", f"{BASE_PATH}/tasks/{task_id}", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "获取任务详情响应")
        
        if response.status == 200:
            print("✅ 获取任务详情成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取任务详情失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_update_task(token, task_id):
    """测试更新任务"""
    print(f"9. 测试更新任务 (ID: {task_id})")
    
    update_data = {
        "title": f"已更新的测试任务 {random.randint(1000, 9999)}",
        "description": "这是一个已更新的测试任务",
        "priority": "high",
        "status": "in_progress"
    }
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = json.dumps(update_data)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/tasks/{task_id}")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("PUT", f"{BASE_PATH}/tasks/{task_id}", body=body, headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "更新任务响应")
        
        if response.status == 200:
            print("✅ 任务更新成功!")
            return json.loads(body)
        else:
            print(f"❌ 任务更新失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_get_chat_messages(token):
    """测试获取聊天消息"""
    print("10. 测试获取聊天消息")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/chat/messages?limit=5")
        print(f"请求头: {headers}")
        
        conn.request("GET", f"{BASE_PATH}/chat/messages?limit=5", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "获取聊天消息响应")
        
        if response.status == 200:
            print("✅ 获取聊天消息成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取聊天消息失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_send_chat_message(token):
    """测试发送聊天消息"""
    print("11. 测试发送聊天消息")
    
    message_data = {
        "content": f"测试消息 {random.randint(1000, 9999)}",
        "message_type": "text",
        "anonymous": False
    }
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = json.dumps(message_data)
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/chat/send")
        print(f"请求头: {headers}")
        print(f"请求体: {body}")
        
        conn.request("POST", f"{BASE_PATH}/chat/send", body=body, headers=headers)
        response = conn.getresponse()
        
        body_response = print_response(conn, response, "发送聊天消息响应")
        
        if response.status == 201:
            print("✅ 聊天消息发送成功!")
            return json.loads(body_response)
        else:
            print(f"❌ 聊天消息发送失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_daily_summary(token):
    """测试获取每日摘要"""
    print("12. 测试获取每日摘要")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/chat/daily-summary")
        print(f"请求头: {headers}")
        
        conn.request("GET", f"{BASE_PATH}/chat/daily-summary", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "获取每日摘要响应")
        
        if response.status == 200:
            print("✅ 获取每日摘要成功!")
            return json.loads(body)
        else:
            print(f"❌ 获取每日摘要失败! 状态码: {response.status}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def test_delete_task(token, task_id):
    """测试删除任务"""
    print(f"13. 测试删除任务 (ID: {task_id})")
    
    try:
        conn = http.client.HTTPConnection(HOST, PORT)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"发送请求到: http://{HOST}:{PORT}{BASE_PATH}/tasks/{task_id}")
        print(f"请求头: {headers}")
        
        conn.request("DELETE", f"{BASE_PATH}/tasks/{task_id}", headers=headers)
        response = conn.getresponse()
        
        body = print_response(conn, response, "删除任务响应")
        
        if response.status == 204:
            print("✅ 任务删除成功!")
            return True
        else:
            print(f"❌ 任务删除失败! 状态码: {response.status}")
            return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False
    finally:
        conn.close()

def main():
    """主测试流程"""
    print_separator()
    print("🚀 开始 SmartFlow API 完整功能测试")
    print("测试模块：认证、用户管理、任务管理、聊天功能")
    print_separator()
    
    # 测试结果记录
    test_results = {}
    
    # 1. 测试API状态
    api_status = test_api_status()
    test_results["api_status"] = api_status is not None
    if api_status:
        print("API状态信息:")
        print(f"总路由数: {api_status.get('total_routes', 0)}")
        print("可用路由:")
        for route in api_status.get('routes', []):
            print(f"  - {route.get('path')} [{', '.join(route.get('methods', ['GET']))}]")
    
    # 2. 用户注册
    register_result = test_register_user()
    test_results["user_register"] = register_result is not None
    
    # 3. 用户登录
    token = test_login()
    test_results["user_login"] = token is not None
    if not token:
        print("❌ 测试终止：用户登录失败")
        return
    
    # 4. 获取当前用户信息
    user_info = test_get_current_user(token)
    test_results["get_user_info"] = user_info is not None
    
    # 5. 更新用户信息
    update_result = test_update_user(token)
    test_results["update_user"] = update_result is not None
    
    # 6. 创建任务
    task = test_create_task(token)
    test_results["create_task"] = task is not None
    if not task:
        print("⚠️ 任务创建失败，跳过任务相关测试")
        task_id = None
    else:
        task_id = task.get("id")
    
    # 7. 获取任务列表
    tasks = test_get_tasks(token)
    test_results["get_tasks"] = tasks is not None
    
    # 8. 获取任务详情
    if task_id:
        task_detail = test_get_task_detail(token, task_id)
        test_results["get_task_detail"] = task_detail is not None
    
    # 9. 更新任务
    if task_id:
        update_task_result = test_update_task(token, task_id)
        test_results["update_task"] = update_task_result is not None
    
    # 10. 获取聊天消息
    chat_messages = test_get_chat_messages(token)
    test_results["get_chat_messages"] = chat_messages is not None
    
    # 11. 发送聊天消息
    chat_message = test_send_chat_message(token)
    test_results["send_chat_message"] = chat_message is not None
    
    # 12. 获取每日摘要
    daily_summary = test_daily_summary(token)
    test_results["get_daily_summary"] = daily_summary is not None
    
    # 13. 删除任务
    if task_id:
        delete_task_result = test_delete_task(token, task_id)
        test_results["delete_task"] = delete_task_result
    
    # 输出测试总结
    print_separator()
    print("📊 测试结果总结")
    print_separator()
    
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
        print("\n🎉 所有测试通过! API功能正常")
    else:
        print(f"\n⚠️ 有 {failed_tests} 个测试失败，需要检查相关功能")
    
    print_separator()

if __name__ == "__main__":
    main()