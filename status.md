============================================================
🚀 注册新用户
============================================================
✅ 用户注册成功: testuser_4wohq0

============================================================
🚀 用户登录
============================================================
✅ 登录成功

============================================================
🚀 用户信息相关API
============================================================
✅ 获取当前用户信息
   详情: {"username":"testuser_4wohq0","email":"testuser_4wohq0@example.com","full_name":"集成测试用户","id":21,"is_active":true,"settings":{}}
✅ 更新用户信息
   详情: {"username":"testuser_4wohq0","email":"updated_testuser_4wohq0@example.com","full_name":"集成测试用户-更新","id":21,"is_active":true,"settings":{}}

============================================================
🚀 任务管理全流程
============================================================
✅ 任务创建成功! ID: 16
✅ 获取任务列表
   详情: [{"title":"集成测试任务","description":"测试任务描述","due_date":null,"priority":"high","estimated_duration":90,"id":16,"owner_id":21,"status":"pending","created_at":"2025-07-05T05:38:27.885012","updated_at":"2025-07-05T05:38:27.885012","sub_tasks":[]}]
✅ 获取任务详情
   详情: {"title":"集成测试任务","description":"测试任务描述","due_date":null,"priority":"high","estimated_duration":90,"id":16,"owner_id":21,"status":"pending","created_at":"2025-07-05T05:38:27.885012","updated_at":"2025-07-05T05:38:27.885012","sub_tasks":[]}
✅ 更新任务
   详情: {"title":"已更新的集成测试任务","description":"已更新描述","due_date":null,"priority":"medium","estimated_duration":90,"id":16,"owner_id":21,"status":"in_progress","created_at":"2025-07-05T05:38:27.885012","updated_at":"2025-07-05T05:38:34.026857","sub_tasks":[]}
✅ AI智能拆解任务
   详情: {"main_task":"需求分析和规划","description":"确定系统的功能需求，包括用户管理、客户管理、销售跟踪和报表分析等模块，并制定开发计划。","estimated_duration":120,"priority":7.0,"subtasks":[{"title":"需求分析和规划","description":"确定系统的功能需求，包括用户管理、客户管理、销 售跟踪和报表分析等模块，并制定开发计划。","order":1},{"title":"系统设计","description":"根据需求分析结果，设计系统的架构、数据库结构、界面设计和功能模块等。","order":2},{"title":"编码实现","description":"根据系统设计，编写代码实现各个功能模块，并进行单元测试。","order":3},{"title":"集成测试","description":"将各个功能模块进行集成，进行系统测试，确保各个模块之间的协同工作。","order":4},{"title":"用户培训和上线","description":"对用户进行系统培训，确保用户能够熟练使用系统，并将系统正式上线运行。","order":5},{"title":"维护和升级","description":"根据用户反馈和系统运行情况，对系统进行维护和升级，不断优化系统功能和性能。","order":6}]}
✅ 添加子任务
   详情: {"title":"子任务1","description":"子任务描述","order":0,"id":4,"parent_task_id":16,"status":"pending","created_at":"2025-07-05T05:38:50.311110","updated_at":"2025-07-05T05:38:50.311110"}

============================================================
🚀 提醒模块全流程
============================================================
✅ AI提醒生成
   详情: {"success":true,"reminder_content":{"title":"继续进行集成测试任务","message":"您已经 开始进行'已更新的集成测试任务'，预计需要90分钟。请继续工作，确保任务顺利完成。","urgency_level":"low","suggested_action":"建议先完成测试用例的编写，然后逐步执行测试并记录结果","motivation_quote":"持之以恒是成功的关键。"},"task_info":{"title":"已更新的集成测试任务","description":"已更新描述","priority":"medium","due_date":null,"status":"in_progress","estimated_duration":90}}
✅ 提醒创建成功! ID: 4
✅ 获取提醒列表
   详情: [{"task_id":16,"reminder_time":"2025-07-05T11:39:00.858028","message":"集成测试提醒","priority":2,"status":"pending","strategy":"single","id":4,"created_at":"2025-07-05T05:39:00.861902","updated_at":"2025-07-05T05:39:00.861902","is_sent":false,"user_id":21}]
✅ 获取待处理提醒
   详情: []
✅ 获取提醒详情
   详情: {"task_id":16,"reminder_time":"2025-07-05T11:39:00.858028","message":"集成测试提醒","priority":2,"status":"pending","strategy":"single","id":4,"created_at":"2025-07-05T05:39:00.861902","updated_at":"2025-07-05T05:39:00.861902","is_sent":false,"user_id":21}
✅ 更新提醒
   详情: {"task_id":16,"reminder_time":"2025-07-05T11:39:00.858028","message":"已更新的集成测 试提醒","priority":3,"status":"pending","strategy":"single","id":4,"created_at":"2025-07-05T05:39:00.861902","updated_at":"2025-07-05T05:39:09.117769","is_sent":false,"user_id":21}        
✅ 标记提醒已发送
   详情: {"task_id":16,"reminder_time":"2025-07-05T11:39:00.858028","message":"已更新的集成测 试提醒","priority":3,"status":"sent","strategy":"single","id":4,"created_at":"2025-07-05T05:39:00.861902","updated_at":"2025-07-05T05:39:11.173285","is_sent":true,"user_id":21}
✅ 获取通知历史
   详情: [{"id":4,"user_id":21,"username":"testuser_4wohq0","type":"reminder","task_title":"已更新的集成测试任务","message":"已更新的集成测试提醒","reminder_time":"2025-07-05T11:39:00.858028","created_at":"2025-07-05T13:39:11.223402","status":"sent"}]
✅ 获取通知统计
   详情: {"total":1,"reminders":1,"system":0,"today":1}
✅ 删除提醒

============================================================
🚀 聊天模块全流程
============================================================
✅ 发送聊天消息
   详情: {"content":"集成测试消息","message_type":"text","shared_task_id":null,"shared_report_id":null,"anonymous":false,"id":46,"user_id":21,"username":"testuser_4wohq0","created_at":"2025-07-05T05:39:19.418382","is_system":false}
✅ 获取聊天消息
   详情: [{"content":"集成测试消息","message_type":"text","shared_task_id":null,"shared_report_id":null,"anonymous":false,"id":46,"user_id":21,"username":"testuser_4wohq0","created_at":"2025-07-05T05:39:19.418382","is_system":false},{"content":"分享日报：daily","message_type":"report_share","shared_task_id":null,"shared_report_id":1,"anonymous":false,"id":45,"user_id":20,"username":"testuser_g6xxba","created_at":"2025-07-05T05:30:47.824092","is_system":false},{"content":"分享任务：AI提醒测试任务","message_type":"task_share","shared_task_id":1,"shared_report_id":null,"anonymous":false,"id":44,"user_id":20,"username":"testuser_g6xxba","created_at":"2025-07-05T05:30:45.757104","is_system":false},{"content":"集成测试消息","message_type":"text","shared_task_id":null,"shared_report_id":null,"anonymous":false,"id":43,"user_id":20,"username":"testuser_g6xxba","created_at":"2025-07-05T05:30:39.580560","is_system":false},{"content":"分 享日报：daily","message_type":"report_share","shared_task_id":null,"shared_report_id":1,"anonymous":false,"id":42,"user_id":19,"username":"testuser_mkb131","created_at":"2025-07-05T05:27:37.528894","is_system":false}]
✅ 获取每日摘要
   详情: {"date":"2025-07-05","summary":"今日共发送 46 条消息，最活跃用户：testuser_3dafa2, testuser_hf8k23, testuser_bjjy5z, testuser_bny0lw, testuser_d5c0yb","top_users":["testuser_3dafa2","testuser_hf8k23","testuser_bjjy5z","testuser_bny0lw","testuser_d5c0yb"],"progress_analysis":"今日社群交流活跃，成员参与度良好。","optimization_suggestions":"建议继续鼓励成员分享任务进 度和心得体会。"}
✅ 分享任务进度
   详情: {"message":"任务分享成功","message_id":47}
✅ 分享日报片段
   详情: {"message":"报告分享成功","message_id":48}

============================================================
🚀 报表模块全流程
============================================================
✅ 获取日报
   详情: {"id":55,"user_id":21,"report_type":"daily","report_date":"2025-07-05T00:00:00","summary":"在2025-07-05完成了0个任务，用时0分钟。","tasks_completed":0,"tasks_pending":1,"total_time_spent":0,"avg_task_duration":0.0,"progress_analysis":"整体进度良好，但部分任务耗时较长。","deviation_analysis":"有3个任务未按计划完成。","optimization_suggestions":"建议优先处理重要任务 并合理分配时间。","ai_insights":"您在上午时段工作效率最高。","next_steps":["审查未完成任务"," 规划明日优先级","优化时间分配"],"top_tasks":[],"created_at":"2025-07-05T05:39:32.257567","task_details":[]}
✅ 获取指定日期报告
   详情: {"id":56,"user_id":21,"report_type":"daily","report_date":"2025-07-05T00:00:00","summary":"在2025-07-05完成了0个任务，用时0分钟。","tasks_completed":0,"tasks_pending":1,"total_time_spent":0,"avg_task_duration":0.0,"progress_analysis":"整体进度良好，但部分任务耗时较长。","deviation_analysis":"有3个任务未按计划完成。","optimization_suggestions":"建议优先处理重要任务 并合理分配时间。","ai_insights":"您在上午时段工作效率最高。","next_steps":["审查未完成任务"," 规划明日优先级","优化时间分配"],"top_tasks":[],"created_at":"2025-07-05T05:39:34.417826","task_details":[]}
✅ 获取周报
   详情: {"id":57,"user_id":21,"report_type":"weekly","report_date":"2025-06-30T00:00:00","summary":"在2025-06-30完成了0个任务，用时0分钟。","tasks_completed":0,"tasks_pending":1,"total_time_spent":0,"avg_task_duration":0.0,"progress_analysis":"整体进度良好，但部分任务耗时较长。","deviation_analysis":"有3个任务未按计划完成。","optimization_suggestions":"建议优先处理重要任务并合理分配时间。","ai_insights":"您在上午时段工作效率最高。","next_steps":["审查未完成任务"," 规划明日优先级","优化时间分配"],"top_tasks":[],"created_at":"2025-07-05T05:39:39.268823","task_details":[]}
✅ 获取月报
   详情: {"id":58,"user_id":21,"report_type":"monthly","report_date":"2025-07-01T00:00:00","summary":"在2025-07-01完成了0个任务，用时0分钟。","tasks_completed":0,"tasks_pending":1,"total_time_spent":0,"avg_task_duration":0.0,"progress_analysis":"整体进度良好，但部分任务耗时较长。","deviation_analysis":"有3个任务未按计划完成。","optimization_suggestions":"建议优先处理重要任 务并合理分配时间。","ai_insights":"您在上午时段工作效率最高。","next_steps":["审查未完成任务","规划明日优先级","优化时间分配"],"top_tasks":[],"created_at":"2025-07-05T05:39:41.418084","task_details":[]}
✅ 获取报表统计
   详情: {"total_reports":4,"avg_completion_rate":0.0,"best_day":null,"worst_day":"2025-07-05","most_productive_time":null,"task_distribution":{"medium":1.0},"weekly_trend":{},"monthly_comparison":{}}

============================================================
🚀 数据库快照 - 关键表内容
============================================================

📋 表: user
('testuser', 'updated_testuser@example.com', '$2b$12$Z7HB5flLHqkGRm0g.Eht1.qRar66pzM7IjsWvoYQAQtlL1c9d1a9a', '更新后的测试用户', 1, '{}', 0, 0, 1, '2025-07-05 03:22:05.265836', '2025-07-05 03:36:35.085378')
('testuser_axw9gy', 'updated_testuser_axw9gy@example.com', '$2b$12$PptoFlaHylV5F18NodXureP69e2Y4hg0FK.bJmej4vgWvmhMiRuKi', '集成测试用户-更新', 1, '{}', 0, 0, 2, '2025-07-05 04:22:08.949080', '2025-07-05 04:22:15.336976')
('testuser_qi4p8p', 'updated_testuser_qi4p8p@example.com', '$2b$12$v60Fbkz3vBVxqJfGWtoYD.tDoIwqi0pXUoqRcqj595QzSZIf9APs2', '集成测试用户-更新', 1, '{}', 0, 0, 3, '2025-07-05 04:25:00.313592', '2025-07-05 04:25:06.678027')
('testuser_5r3gsv', 'updated_testuser_5r3gsv@example.com', '$2b$12$XKVLZmBcZLrfwDq2.wJfQ.87MBhmr3iPyHubLei4dAiBd0/03zy4y', '集成测试用户-更新', 1, '{}', 0, 0, 4, '2025-07-05 04:25:57.464957', '2025-07-05 04:26:03.837277')
('testuser_3dafa2', 'updated_testuser_3dafa2@example.com', '$2b$12$96YqeQSK90oJM/XVFK0qH.nk2mP3sx4obnFdCm6pfr2a8FCar1.SC', '集成测试用户-更新', 1, '{}', 0, 0, 5, '2025-07-05 04:29:00.628548', '2025-07-05 04:29:07.008078')

📋 表: task
('AI提醒测试任务', '这是一个用于测试AI提醒功能的任务', None, 'HIGH', 'PENDING', 120, 0.0, None, 1, 1, '2025-07-05 03:22:24.472444', '2025-07-05 03:22:24.472444')
('AI提醒测试任务', '这是一个用于测试AI提醒功能的任务', None, 'HIGH', 'PENDING', 120, 0.0, None, 1, 2, '2025-07-05 03:23:27.586986', '2025-07-05 03:23:27.586986')
('AI提醒测试任务', '这是一个用于测试AI提醒功能的任务', None, 'HIGH', 'PENDING', 120, 0.0, None, 1, 3, '2025-07-05 03:24:51.754970', '2025-07-05 03:24:51.754970')
('通知系统测试任务', '这是一个用于测试通知系统的任务', None, 'HIGH', 'PENDING', 60, 0.0, None, 1, 4, '2025-07-05 03:32:08.662510', '2025-07-05 03:32:08.662510')
('测试任务 2840', '这是一个通过API测试创建的任务', None, 'MEDIUM', 'PENDING', 60, 0.0, None, 1, 5, '2025-07-05 03:36:37.179519', '2025-07-05 03:36:37.179519')

📋 表: reminder
('2025-07-05 05:25:04.014735', "AI提醒测试任务即将开始\n\n您好！根据您的日程安排，现在是进行'AI提醒测试任务'的最佳时机。预计需要120分钟完成。\n\n建议行动: 建议您先阅读任务描述，然后开始执 行\n\n💪 行动是治愈恐惧的良药，犹豫将不断滋养恐惧。", 0, 3, 'multi_round', 3, 1, 1, '2025-07-05 03:25:04.017698', '2025-07-05 03:25:04.017698', 'pending')
('2025-07-05 05:38:32.232220', '这是一个测试提醒，用于验证本地通知系统是否正常工作。', 1, 3, 'single', 6, 1, 2, '2025-07-05 03:38:32.232220', '2025-07-05 03:38:34.286925', 'pending')      
('2025-07-05 11:22:08.917633', '集成测试提醒', 0, 2, 'single', 15, 17, 3, '2025-07-05 05:22:08.923120', '2025-07-05 05:22:08.923120', 'pending')

📋 表: dailyreport
('2025-07-05 00:00:00.000000', 'daily', '在2025-07-05完成了0个任务，用时0分钟。', '整体进度良 好，但部分任务耗时较长。', '有3个任务未按计划完成。', '建议优先处理重要任务并合理分配时间。', '您在上午时段工作效率最高。', '["\\u5ba1\\u67e5\\u672a\\u5b8c\\u6210\\u4efb\\u52a1", "\\u89c4\\u5212\\u660e\\u65e5\\u4f18\\u5148\\u7ea7", "\\u4f18\\u5316\\u65f6\\u95f4\\u5206\\u914d"]', 0, 12, 0, 0.0, '[]', '{"date": "2025-07-05", "tasks_completed": 0, "tasks_pending": 12, "total_time_spent": 0, "avg_task_duration": 0, "important_tasks": [], "task_logs": []}', '2025-07-05 04:15:52.243693', 1, 1, '2025-07-05 04:15:52.243693')
('2025-07-05 00:00:00.000000', 'daily', '在2025-07-05完成了0个任务，用时0分钟。', '整体进度良 好，但部分任务耗时较长。', '有3个任务未按计划完成。', '建议优先处理重要任务并合理分配时间。', '您在上午时段工作效率最高。', '["\\u5ba1\\u67e5\\u672a\\u5b8c\\u6210\\u4efb\\u52a1", "\\u89c4\\u5212\\u660e\\u65e5\\u4f18\\u5148\\u7ea7", "\\u4f18\\u5316\\u65f6\\u95f4\\u5206\\u914d"]', 0, 12, 0, 0.0, '[]', '{"date": "2025-07-05", "tasks_completed": 0, "tasks_pending": 12, "total_time_spent": 0, "avg_task_duration": 0, "important_tasks": [], "task_logs": []}', '2025-07-05 04:15:54.380487', 1, 2, '2025-07-05 04:15:54.380487')
('2025-07-05 00:00:00.000000', 'daily', '在2025-07-05完成了0个任务，用时0分钟。', '整体进度良 好，但部分任务耗时较长。', '有3个任务未按计划完成。', '建议优先处理重要任务并合理分配时间。', '您在上午时段工作效率最高。', '["\\u5ba1\\u67e5\\u672a\\u5b8c\\u6210\\u4efb\\u52a1", "\\u89c4\\u5212\\u660e\\u65e5\\u4f18\\u5148\\u7ea7", "\\u4f18\\u5316\\u65f6\\u95f4\\u5206\\u914d"]', 0, 1, 0, 0.0, '[]', '{"date": "2025-07-05", "tasks_completed": 0, "tasks_pending": 1, "total_time_spent": 0, "avg_task_duration": 0, "important_tasks": [], "task_logs": []}', '2025-07-05 04:29:54.234189', 5, 3, '2025-07-05 04:29:54.234189')
('2025-07-05 00:00:00.000000', 'daily', '在2025-07-05完成了0个任务，用时0分钟。', '整体进度良 好，但部分任务耗时较长。', '有3个任务未按计划完成。', '建议优先处理重要任务并合理分配时间。', '您在上午时段工作效率最高。', '["\\u5ba1\\u67e5\\u672a\\u5b8c\\u6210\\u4efb\\u52a1", "\\u89c4\\u5212\\u660e\\u65e5\\u4f18\\u5148\\u7ea7", "\\u4f18\\u5316\\u65f6\\u95f4\\u5206\\u914d"]', 0, 1, 0, 0.0, '[]', '{"date": "2025-07-05", "tasks_completed": 0, "tasks_pending": 1, "total_time_spent": 0, "avg_task_duration": 0, "important_tasks": [], "task_logs": []}', '2025-07-05 04:29:56.373474', 5, 4, '2025-07-05 04:29:56.373474')
('2025-07-05 00:00:00.000000', 'daily', '在2025-07-05完成了0个任务，用时0分钟。', '整体进度良 好，但部分任务耗时较长。', '有3个任务未按计划完成。', '建议优先处理重要任务并合理分配时间。', '您在上午时段工作效率最高。', '["\\u5ba1\\u67e5\\u672a\\u5b8c\\u6210\\u4efb\\u52a1", "\\u89c4\\u5212\\u660e\\u65e5\\u4f18\\u5148\\u7ea7", "\\u4f18\\u5316\\u65f6\\u95f4\\u5206\\u914d"]', 0, 1, 0, 0.0, '[]', '{"date": "2025-07-05", "tasks_completed": 0, "tasks_pending": 1, "total_time_spent": 0, "avg_task_duration": 0, "important_tasks": [], "task_logs": []}', '2025-07-05 04:31:32.224260', 6, 5, '2025-07-05 04:31:32.224260')

📋 表: chatmessage
('集成测试消息', 'text', 0, 0, 5, None, None, '2025-07-05 04:29:41.584200', '2025-07-05 04:29:41.584200', 1)
('分享任务：AI提醒测试任务', 'task_share', 0, 0, 5, 1, None, '2025-07-05 04:29:47.745960', '2025-07-05 04:29:47.745960', 2)
('分享日报：daily', 'report_share', 0, 0, 5, None, 1, '2025-07-05 04:29:49.814076', '2025-07-05 04:29:49.814076', 3)
('集成测试消息', 'text', 0, 0, 6, None, None, '2025-07-05 04:31:19.042358', '2025-07-05 04:31:19.042358', 4)
('分享任务：AI提醒测试任务', 'task_share', 0, 0, 6, 1, None, '2025-07-05 04:31:25.234887', '2025-07-05 04:31:25.234887', 5)
✅ 删除任务

============================================================
🚀 集成测试完成
============================================================
🎉 全链路后端集成测试全部通过！