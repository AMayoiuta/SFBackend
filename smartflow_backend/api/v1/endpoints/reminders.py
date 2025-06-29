"""
提醒服务API端点

主要功能:
1. 创建智能提醒
2. 查询待处理提醒
3. 更新提醒状态
4. 实现多轮提醒策略

API端点:
- POST /reminders/: 创建新提醒
- GET /reminders/: 获取用户所有提醒
- GET /reminders/pending: 获取待处理提醒
- GET /reminders/{reminder_id}: 获取特定提醒详情
- PUT /reminders/{reminder_id}: 更新提醒信息
- DELETE /reminders/{reminder_id}: 删除提醒
- POST /reminders/{reminder_id}/mark-sent: 标记提醒已发送

智能提醒功能:
- 根据任务优先级和截止日期自动计算最佳提醒时间
- 支持多轮提醒策略(首次提醒、临近提醒、最终提醒)
- 集成外部通知服务(如Firebase)发送推送通知
- 分析用户响应模式，优化提醒策略

数据关联:
- 与任务模块紧密集成
- 记录提醒发送历史和用户响应
""" 