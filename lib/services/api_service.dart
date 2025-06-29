/*
 * API服务
 * 
 * 主要功能：
 * 1. 与后端API通信
 * 2. 处理身份验证
 * 3. 处理任务相关API请求
 * 4. 处理提醒和报告相关API请求
 * 
 * 开发者需要实现：
 * - 连接后端各API端点
 * - 处理请求错误和重试
 * - 管理认证令牌
 * - 序列化和反序列化数据
 */

import 'dart:convert';
import 'package:http/http.dart' as http;
// import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // API基础URL，后续需要配置为实际部署地址
  final String baseUrl = 'http://localhost:8000/api/v1';
  // 存储认证令牌
  String? _authToken;
  
  // 单例模式实现
  static final ApiService _instance = ApiService._internal();
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal();
  
  // 设置认证令牌
  void setToken(String token) {
    _authToken = token;
  }
  
  // 清除认证令牌
  void clearToken() {
    _authToken = null;
  }
  
  // 获取认证头
  Map<String, String> _getHeaders() {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }
  
  // 用户登录
  Future<Map<String, dynamic>> login(String username, String password) async {
    // 实现用户登录逻辑
    // 发送POST请求到/auth/login端点
    // 保存返回的令牌
    return {};
  }
  
  // 获取任务列表
  Future<List<dynamic>> getTasks() async {
    // 实现获取任务列表逻辑
    // 发送GET请求到/tasks端点
    return [];
  }
  
  // 创建新任务
  Future<Map<String, dynamic>> createTask(Map<String, dynamic> taskData) async {
    // 实现创建任务逻辑
    // 发送POST请求到/tasks端点
    return {};
  }
  
  // 使用AI拆解任务
  Future<Map<String, dynamic>> breakdownTask(String description) async {
    // 实现任务拆解逻辑
    // 发送POST请求到/tasks/breakdown端点
    return {};
  }
  
  // 获取每日报告
  Future<Map<String, dynamic>> getDailyReport() async {
    // 实现获取日报逻辑
    // 发送GET请求到/reports/daily端点
    return {};
  }
  
  // 通用GET请求方法
  Future<dynamic> get(String endpoint) async {
    // 实现GET请求逻辑
    return null;
  }
  
  // 通用POST请求方法
  Future<dynamic> post(String endpoint, Map<String, dynamic> data) async {
    // 实现POST请求逻辑
    return null;
  }
  
  // 通用PUT请求方法
  Future<dynamic> put(String endpoint, Map<String, dynamic> data) async {
    // 实现PUT请求逻辑
    return null;
  }
  
  // 通用DELETE请求方法
  Future<dynamic> delete(String endpoint) async {
    // 实现DELETE请求逻辑
    return null;
  }
} 