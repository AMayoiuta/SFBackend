# SmartFlow 项目 Git / GitHub 操作手册

## 目录
1. [核心概念](#核心概念)  
2. [环境准备](#环境准备)
3. [本地 Git 基础操作](#本地-git-基础操作)  
4. [分支管理工作流](#分支管理工作流)
5. [Pull Request 协作流程](#pull-request-协作流程)
6. [冲突解决指南](#冲突解决指南)
7. [Issue / Project Board 任务管理](#issue--project-board-任务管理)  
8. [角色-实战范例](#角色-实战范例)  
9. [常见报错速查](#常见报错速查)  

---

## 核心概念
| 关键词 | 详细解释 | SmartFlow 约定 |
|--------|-----------|----------------|
| **Git** | 分布式版本控制系统，跟踪文件改动，支持回滚/分支/合并 | 推荐安装 **Git 2.40+**，配置好用户名和邮箱 |
| **GitHub** | 云端代码托管 + 协作平台，提供PR、Issue、Actions等协作功能 | 所有仓库私有，仅团队成员可读写 |
| **仓库 (Repository)** | 项目代码的集中存储位置，包含所有文件和提交历史 | `smartflow-backend` / `smartflow-frontend` / `smartflow-docs` |
| **分支 (Branch)** | 独立开发线，使团队成员可以并行工作而不互相干扰 | `main`(稳定发布) `dev`(集成测试) `feature/*`(功能开发) `fix/*`(缺陷修复) |
| **提交 (Commit)** | 保存文件更改的快照，附带提交信息描述变更 | 遵循[约定式提交](https://www.conventionalcommits.org/zh-hans/)规范 |
| **PR (Pull Request)** | 请求将一个分支的更改合并到另一分支，提供代码审查机制 | **必须**经1名同学审查通过后才能合并 |
| **Issue** | 用于跟踪任务、Bug、功能请求和讨论 | 标题使用 `feat:` `fix:` `docs:` 等前缀 |
| **Project Board** | 看板视图任务管理（To-do / In-Progress / Done） | 面向全员公开进度，定期更新状态 |

### 开发流程概览

```
feature分支 → PR → dev(开发集成分支) → 周度测试通过 → PR → main(稳定发布分支) → 发布
```

---

## 环境准备

### Git 安装与配置

1. **安装 Git**
   - Windows: 下载并安装 [Git for Windows](https://git-scm.com/download/win)
   - macOS: 通过 Homebrew 安装 `brew install git`
   - Linux: `sudo apt install git` 或 `sudo yum install git`

2. **基本配置**
   ```bash
   # 设置用户名和邮箱(全局)
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱@example.com"
   
   # 配置默认编辑器
   git config --global core.editor "code --wait"  # VS Code
   
   # 配置默认分支名
   git config --global init.defaultBranch main
   ```

3. **SSH 密钥配置** (推荐)
   ```bash
   # 生成 SSH 密钥
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # 查看公钥并添加到 GitHub
   cat ~/.ssh/id_ed25519.pub
   # 复制输出内容到 GitHub -> Settings -> SSH and GPG keys -> New SSH key
   ```

### 仓库初始化

1. **克隆已有仓库**
   ```bash
   git clone https://github.com/YourOrg/smartflow-backend.git
   cd smartflow-backend
   ```

2. **初始化新仓库**
   ```bash
   mkdir my-project
   cd my-project
   git init
   git remote add origin https://github.com/YourOrg/new-repo.git
   ```

---

## 本地 Git 基础操作

### 日常工作流

| 操作 | 命令行 | VS Code / Cursor 操作 | 说明 |
|------|--------|-------------|------|
| **查看状态** | `git status` | 打开源代码管理面板 | 查看哪些文件被修改，哪些已暂存 |
| **拉取最新代码** | `git pull` | 点击状态栏同步按钮 | 获取远程仓库最新变更 |
| **查看分支** | `git branch -a` | 点击状态栏分支名 | 查看所有本地和远程分支 |
| **创建并切换分支** | `git checkout -b feature/login-api` | 状态栏点击分支名→新建分支 | 从当前分支创建新分支并切换 |
| **切换分支** | `git checkout dev` | 状态栏点击分支名→选择分支 | 切换到指定分支 |
| **暂存更改** | `git add file.js` 或 `git add .` | 点击更改旁的 `+` | 将更改标记为待提交 |
| **提交更改** | `git commit -m "feat: 添加登录API"` | 输入提交信息后点击提交按钮 | 将暂存的更改保存到历史 |
| **推送到远程** | `git push` 或<br>`git push -u origin feature/x` | 点击同步按钮 | 将本地提交发送到远程仓库 |
| **查看历史** | `git log` 或<br>`git log --oneline --graph` | 右键点击文件→查看文件历史 | 查看提交历史和分支关系 |
| **丢弃更改** | `git checkout -- file.js` | 右键点击文件→丢弃更改 | 撤销未暂存的修改 |
| **取消暂存** | `git reset HEAD file.js` | 点击已暂存文件旁的 `-` | 将文件从暂存区移除 |

### 提交信息规范

提交信息格式: `<类型>[可选作用域]: <描述>`

**类型前缀**:
- `feat:` - 新功能
- `fix:` - 修复Bug
- `docs:` - 文档更新
- `style:` - 代码样式/格式调整(不影响功能)
- `refactor:` - 代码重构(不增加功能也不修复bug)
- `perf:` - 性能优化
- `test:` - 添加/修改测试
- `chore:` - 构建过程或辅助工具变动

**示例**:
- `feat(auth): 实现JWT登录认证`
- `fix(task): 修复任务排序算法bug`
- `docs: 更新API文档和使用说明`
- `refactor(api): 重构任务管理模块`

### 临时保存工作区

```bash
# 保存当前工作进度
git stash save "正在开发登录功能"

# 查看保存的工作进度
git stash list

# 恢复最近的工作进度
git stash pop

# 恢复指定的工作进度
git stash apply stash@{1}
```

---

## 分支管理工作流

### 分支命名规范

- `main` - 稳定发布分支，随时可部署
- `dev` - 开发集成分支，集成已完成功能
- `feature/xxx` - 功能开发分支，如 `feature/task-breakdown`
- `fix/xxx` - 缺陷修复分支，如 `fix/login-error`
- `release/x.y.z` - 发布准备分支，如 `release/1.0.0`
- `hotfix/xxx` - 生产环境紧急修复，如 `hotfix/critical-auth-bug`

### 分支工作流程

1. **功能开发流程**:
   ```bash
   # 确保本地main/dev是最新的
   git checkout dev
   git pull
   
   # 创建功能分支
   git checkout -b feature/new-feature
   
   # 开发并提交
   # ... 编码工作 ...
   git add .
   git commit -m "feat: 实现新功能"
   
   # 推送到远程
   git push -u origin feature/new-feature
   
   # 在GitHub上创建PR，请求合并到dev分支
   ```

2. **Bug修复流程**:
   ```bash
   # 从dev创建修复分支
   git checkout dev
   git pull
   git checkout -b fix/specific-bug
   
   # 修复并提交
   # ... 修复工作 ...
   git add .
   git commit -m "fix: 修复特定bug"
   
   # 推送到远程
   git push -u origin fix/specific-bug
   
   # 在GitHub上创建PR，请求合并到dev分支
   ```

3. **发布流程**:
   ```bash
   # 从main创建发布分支
   git checkout main
   git pull
   git checkout -b release/1.0.0
   
   # 合并dev到发布分支
   git merge dev
   
   # 推送到远程
   git push -u origin release/1.0.0
   
   # 测试和准备发布
   # ... 测试和修复 ...
   
   # 在GitHub上创建PR，请求合并到main分支
   ```

---

## Pull Request 协作流程

### 创建Pull Request (PR)

1. 推送功能分支到GitHub后，访问仓库页面
2. 点击 "Compare & pull request" 按钮
3. 填写PR信息:
   - 标题: 简洁描述变更内容，保持与提交信息风格一致
   - 描述: 详细说明实现内容、测试情况、注意事项等
4. 选择目标分支 (通常是 `dev`)
5. 指定审阅者 (至少1名团队成员)
6. 点击 "Create pull request"

### PR 模板示例

```markdown
## 变更描述
<!-- 详细描述此PR的变更内容 -->

## 关联Issue
<!-- 链接相关Issue，如 #123 -->

## 测试情况
<!-- 描述如何测试此变更 -->

## 截图(如适用)
<!-- 添加相关截图 -->

## 检查项
- [ ] 代码遵循项目编码规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过所有CI检查
```

### 代码审查流程

1. **审阅者职责**:
   - 检查代码逻辑、性能、安全性
   - 确认测试覆盖率
   - 验证代码规范遵循情况
   - 提供建设性反馈

2. **作者响应**:
   - 回应每条审阅评论
   - 根据反馈进行必要修改
   - 推送更新到相同分支(PR会自动更新)

3. **合并条件**:
   - 至少1名审阅者批准
   - 所有请求的更改已完成
   - CI检查通过(如有)
   - 无合并冲突

4. **合并方式**:
   - 一般使用 "Squash and merge" 将所有提交压缩为一个
   - 在特殊情况下使用 "Merge commit" 或 "Rebase and merge"

---

## 冲突解决指南

当多人同时修改同一文件的同一部分时，可能产生合并冲突。

### 识别冲突

```bash
git pull
# 如果出现冲突，会显示如下信息:
# CONFLICT (content): Merge conflict in file.js
```

### 解决冲突步骤

1. **查看冲突文件**:
   ```bash
   git status
   ```

2. **打开冲突文件，找到冲突标记**:
   ```
   <<<<<<< HEAD
   这是当前分支的代码
   =======
   这是要合并进来的代码
   >>>>>>> feature/another-branch
   ```

3. **编辑文件解决冲突**:
   - 删除冲突标记
   - 保留需要的代码
   - 保存文件

4. **标记为已解决**:
   ```bash
   git add file.js
   ```

5. **完成合并**:
   ```bash
   git commit -m "Merge: 解决冲突"
   git push
   ```

### 使用VS Code解决冲突

VS Code提供图形化冲突解决工具:
1. 打开冲突文件
2. 点击 "Accept Current Change"、"Accept Incoming Change"、"Accept Both Changes" 或手动编辑
3. 保存文件
4. 在源代码管理面板中暂存解决的文件
5. 提交解决冲突的更改

### 避免冲突的最佳实践

1. 经常拉取和推送更改，保持分支最新
2. 划分明确的责任区域，避免多人同时修改同一文件
3. 分解大任务为小的独立任务
4. 保持功能分支生命周期短，快速合并

---

## Issue / Project Board 任务管理

### Issue 创建规范

1. **Issue 标题格式**:
   `<类型>: <简洁描述>`
   
   例如:
   - `feat: 实现任务自动分解功能`
   - `fix: 修复用户注册表单验证问题`

2. **Issue 内容模板**:
   ```markdown
   ## 需求/问题描述
   <!-- 详细描述 -->
   
   ## 验收标准
   - [ ] 标准1
   - [ ] 标准2
   
   ## 技术建议(可选)
   <!-- 实现思路 -->
   
   ## 相关资料
   <!-- 链接、截图等 -->
   ```

3. **标签使用**:
   - `priority-high/medium/low`: 优先级
   - `scope-frontend/backend/docs`: 范围
   - `type-feature/bug/docs`: 类型
   - `status-blocked`: 标记被阻塞的任务

### Project Board 使用

1. **列定义**:
   - `To Do`: 待处理任务
   - `In Progress`: 正在进行的任务
   - `Review`: 等待审查的任务
   - `Done`: 已完成的任务

2. **任务移动流程**:
   - 领取任务时将卡片移至 `In Progress`
   - 创建PR后移至 `Review`
   - PR合并后移至 `Done`

3. **关联Pull Request与Issue**:
   - 在PR描述中使用 `Fixes #123` 或 `Closes #123` 自动关联并在合并时关闭issue
   - 或使用 `Related to #123` 仅建立关联

---

## 角色-实战范例

### 前端开发者工作流

```bash
# 1. 克隆仓库并安装依赖
git clone https://github.com/YourOrg/smartflow-frontend.git
cd smartflow-frontend
npm install

# 2. 创建功能分支
git checkout -b feature/task-card-ui

# 3. 开发并提交
# ... 编码工作 ...
git add src/components/TaskCard.vue
git commit -m "feat(ui): 实现任务卡片组件"

# 4. 运行测试确保无误
npm run test

# 5. 推送到远程
git push -u origin feature/task-card-ui

# 6. 在GitHub上创建PR
# 7. 根据审阅反馈修改
git add src/components/TaskCard.vue
git commit -m "refactor: 根据PR反馈优化代码"
git push

# 8. PR获批并合并后，删除本地分支
git checkout dev
git pull
git branch -d feature/task-card-ui
```

### 后端开发者工作流

```bash
# 1. 克隆仓库并设置环境
git clone https://github.com/YourOrg/smartflow-backend.git
cd smartflow-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 创建功能分支
git checkout -b feature/task-api

# 3. 开发并提交
# ... 编码工作 ...
git add api/v1/endpoints/tasks.py
git commit -m "feat(api): 实现任务创建API"

# 4. 运行测试
pytest tests/api/test_tasks.py

# 5. 推送到远程
git push -u origin feature/task-api

# 6. 在GitHub上创建PR
# 7. 根据审阅反馈修改
git add api/v1/endpoints/tasks.py
git commit -m "fix: 修复参数验证逻辑"
git push

# 8. PR获批并合并后，清理本地分支
git checkout dev
git pull
git branch -d feature/task-api
```

---

## 常见报错速查

| 错误信息 | 可能原因 | 解决方法 |
|----------|----------|----------|
| `fatal: not a git repository` | 当前目录不是Git仓库 | 进入正确的仓库目录或使用`git init`初始化 |
| `fatal: remote origin already exists` | 远程仓库已存在 | 使用`git remote rm origin`删除后重新添加 |
| `error: failed to push some refs` | 远程有本地没有的提交 | 先`git pull`同步远程更改，解决冲突后再推送 |
| `fatal: Authentication failed` | 身份验证失败 | 检查用户名密码或SSH密钥，或使用token认证 |
| `error: Your local changes would be overwritten` | 本地有未提交的更改 | 先提交或暂存(stash)本地更改，再拉取 |
| `fatal: refusing to merge unrelated histories` | 尝试合并不相关的历史 | 使用`git pull --allow-unrelated-histories` |
| `fatal: unable to auto-detect email address` | 未配置用户邮箱 | 设置`git config user.email "your@email.com"` |
| `fatal: 'upstream' does not appear to be a git repository` | 未设置上游仓库 | 使用`git remote add upstream URL`添加上游仓库 |

### 重置和恢复

```bash
# 重置最近的提交(保留更改)
git reset --soft HEAD~1

# 完全撤销最近的提交(丢弃更改)
git reset --hard HEAD~1

# 恢复已删除的分支
git checkout -b branch-name SHA1

# 撤销已推送的提交(创建新的还原提交)
git revert HEAD
```

---

### 高级Git技巧

```bash
# 查看指定文件的变更历史
git log --follow -p -- filename

# 查找引入特定代码的提交
git log -S "searchterm"

# 交互式变基(合并/重排/删除提交)
git rebase -i HEAD~3

# 暂时将未完成更改移至一边
git worktree add ../temp-work feature/urgent-fix

# 二分查找定位引入bug的提交
git bisect start
git bisect bad  # 当前版本有问题
git bisect good <earlier-commit-hash>  # 指定一个好的版本
# Git会自动检出中间版本，你测试后标记:
git bisect good  # 或 git bisect bad
# 重复直至找到第一个引入问题的提交
git bisect reset  # 完成后重置