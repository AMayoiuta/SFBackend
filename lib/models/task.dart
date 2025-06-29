/*
 * 任务模型类
 * 
 * 主要功能：
 * 1. 定义任务数据结构
 * 2. 提供序列化和反序列化方法
 * 3. 实现任务状态管理
 * 4. 支持子任务管理
 * 
 * 开发者需要实现：
 * - 完整的任务属性定义
 * - 从JSON解析和转换为JSON的方法
 * - 任务优先级和状态枚举
 * - 子任务关系处理
 */

// 任务优先级枚举
enum TaskPriority {
  low,
  medium,
  high,
  urgent,
}

// 任务状态枚举
enum TaskStatus {
  pending,
  inProgress,
  completed,
  delayed,
  cancelled,
}

// 任务模型类
class Task {
  final int? id;
  final String title;
  final String? description;
  final DateTime? dueDate;
  final TaskPriority priority;
  final TaskStatus status;
  final int? estimatedDuration; // 预计持续时间(分钟)
  final double? importanceScore;
  final List<SubTask> subTasks;

  Task({
    this.id,
    required this.title,
    this.description,
    this.dueDate,
    this.priority = TaskPriority.medium,
    this.status = TaskStatus.pending,
    this.estimatedDuration,
    this.importanceScore,
    this.subTasks = const [],
  });

  // 从JSON创建任务对象
  factory Task.fromJson(Map<String, dynamic> json) {
    // 实现从JSON解析的逻辑
    // 包括处理子任务列表
    return Task(
      title: "实现从JSON解析", // 占位符，需要开发者实现
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    // 实现转换为JSON的逻辑
    // 需要处理子任务列表的序列化
    return {
      'title': title,
      // 添加其他需要序列化的属性
    };
  }
}

// 子任务模型类
class SubTask {
  final int? id;
  final String title;
  final String? description;
  final TaskStatus status;
  final int order; // 子任务排序

  SubTask({
    this.id,
    required this.title,
    this.description,
    this.status = TaskStatus.pending,
    this.order = 0,
  });

  // 从JSON创建子任务对象
  factory SubTask.fromJson(Map<String, dynamic> json) {
    // 实现从JSON解析的逻辑
    return SubTask(
      title: "实现从JSON解析", // 占位符，需要开发者实现
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    // 实现转换为JSON的逻辑
    return {
      'title': title,
      // 添加其他需要序列化的属性
    };
  }
} 