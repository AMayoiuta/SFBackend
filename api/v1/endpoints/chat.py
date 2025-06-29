"""
社群聊天室API端点

主要功能:
1. 实时社群聊天消息
2. 任务进度分享
3. 日报片段分享
4. 系统总结消息推送

API端点:
- GET /chat/messages: 获取聊天消息历史
- POST /chat/messages: 发送新聊天消息
- DELETE /chat/messages/{message_id}: 删除聊天消息
- GET /chat/daily-summary: 获取每日社群总结
- POST /chat/share-task: 分享任务进度到聊天室
- POST /chat/share-report: 分享日报片段到聊天室

WebSocket:
- /chat/ws: WebSocket连接点，用于实时消息推送
- 支持消息广播和用户在线状态

安全与隐私:
- 匿名聊天选项
- 消息内容审核
- 用户可选择隐藏特定任务详情
- 系统定时清理敏感信息

社群激励功能:
- 自动识别和表扬积极分享的用户
- 每日/每周荣誉榜
- 用户进度可视化对比
- 系统智能鼓励消息
""" 