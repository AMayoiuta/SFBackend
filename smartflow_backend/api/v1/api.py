from fastapi import APIRouter

from api.v1.endpoints import tasks, users, auth, reminders, reports, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["提醒"])
api_router.include_router(reports.router, prefix="/reports", tags=["日报"])
api_router.include_router(chat.router, prefix="/chat", tags=["社群聊天"]) 