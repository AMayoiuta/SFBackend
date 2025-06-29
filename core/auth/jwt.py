"""
JWT认证实现模块

主要功能:
1. 创建访问令牌(access token)
2. 验证令牌有效性
3. 提取令牌中的用户信息
4. 处理令牌过期和刷新

关键组件:
- 令牌生成: create_access_token()
- 令牌解码: decode_access_token()
- 令牌验证: verify_token()
- 安全配置: SECRET_KEY, ALGORITHM

依赖模块:
- jose: JWT编码和解码
- datetime: 处理令牌过期时间
- core.config: 获取安全配置
""" 