"""
认证API端点

主要功能:
1. 用户登录和token生成
2. 令牌验证
3. 密码重置
4. 用户登出

API端点:
- POST /auth/login: 用户登录并获取访问令牌
- POST /auth/logout: 用户登出(可选黑名单令牌)
- POST /auth/password-reset: 请求密码重置
- POST /auth/password-reset/confirm: 确认密码重置
- POST /auth/refresh-token: 刷新访问令牌

认证流程:
1. 用户提交用户名/邮箱和密码
2. 验证凭据并生成JWT令牌
3. 返回访问令牌和令牌类型
4. 客户端在后续请求中使用令牌

安全考虑:
- 使用OAuth2密码流程
- 实现令牌过期机制
- 可选的刷新令牌机制
- 密码重置需要邮箱验证
""" 