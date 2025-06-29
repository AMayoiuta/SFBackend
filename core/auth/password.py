"""
密码处理工具模块

主要功能:
1. 密码哈希生成
2. 密码验证
3. 安全密码处理

关键函数:
- verify_password(): 验证明文密码与哈希值是否匹配
- get_password_hash(): 生成密码的安全哈希值
- generate_reset_token(): 生成密码重置令牌
- verify_reset_token(): 验证密码重置令牌

安全特性:
- 使用bcrypt算法进行密码哈希
- 自动生成和验证salt
- 防止时序攻击

依赖模块:
- passlib: 密码哈希库
- bcrypt: 密码加密算法实现
""" 