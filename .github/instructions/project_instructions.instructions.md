---
applyTo: '**'
---

# PenPen Launcher 项目指导说明

## 项目概述

PenPen Launcher 是一个专为电视游戏环境优化的PC启动器，提供类似游戏主机的用户体验。系统包含多个微服务架构组件，支持手柄导航、游戏内覆盖界面、崩溃自动恢复和云端日志监控。

**GitHub Repository**: https://github.com/AwesomePenguin/penpen_launcher

详细的架构设计请参考：`copilot_docs/architecture_notes.md`  
技术实现细节请参考：`copilot_docs/implementation_details.md`  
开发上下文信息请参考：`copilot_docs/development_context.md`

## 项目架构

### 目录结构
```
penpen_launcher/
├── backend/                    # Python后端服务
│   ├── core_api.py            # 核心API服务 (FastAPI)
│   ├── main_ui.py             # 主UI服务 (WebView2)
│   ├── overlay_ui.py          # Overlay UI服务
│   ├── watchdog_service.py    # 看门狗服务
│   ├── log_uploader.py        # 日志上传服务
│   ├── process_manager.py     # 进程管理器
│   ├── launcher.py            # 主启动脚本
│   ├── requirements.txt       # Python依赖
│   ├── .env.example          # 环境变量模板
│   ├── install.bat           # Windows安装脚本
│   └── start.bat             # Windows启动脚本
├── frontend/                  # NextJS前端
│   ├── out/                  # 构建输出目录
│   └── [NextJS项目文件]
├── docs/                     # 项目文档
│   └── project_overview.md   # 项目总览文档
├── copilot_docs/            # AI助手扩展记忆
└── .github/
    └── instructions/         # AI编程指导
```

### 核心组件
1. **核心API服务** - FastAPI后端，提供REST API和WebSocket
2. **主UI服务** - WebView2 + NextJS，提供类主机界面
3. **Overlay UI服务** - 透明窗口 + 手柄监听，游戏内覆盖
4. **看门狗服务** - 进程监控和自动恢复
5. **日志管理服务** - 本地日志 + Cloudflare R2云端上传

> 详细架构说明参见 `copilot_docs/architecture_notes.md`

## 编程规范

### 语言支持
- **双语项目**: 支持中文和英文，无需强制翻译所有内容
- **函数文档字符串**: 优先使用英文（便于代码维护和国际化）
- **行内注释**: 中文或英文均可（以清晰表达为准）
- **扩展文档**: 中文优先（面向中文用户和开发者）

### 命名规范
- **Python代码**: 一律使用snake_case命名
- **变量和函数**: `user_name`, `get_game_info()`, `process_manager`
- **类名**: 使用PascalCase，如`SystemManager`, `GameOverlay`
- **常量**: 全大写加下划线，如`MAX_RESTART_COUNT`, `API_BASE_URL`
- **例外情况**: 仅在第三方API或包依赖要求时使用camelCase

```python
# 正确的命名示例
class ProcessManager:
    def __init__(self):
        self.active_game_pid = None
        self.system_state = "booting"
    
    def start_game_process(self, game_id: str):
        """Start a game process with given game ID."""
        pass  # 实现游戏启动逻辑
    
    def _internal_helper(self):
        # 私有方法使用下划线前缀
        pass

# 第三方API适配示例
webview.create_window(
    title="Game Launcher",  # 遵循第三方API的camelCase要求
    url="http://localhost:8000"
)
```

### 文档结构规范
```
penpen_launcher/
├── docs/                       # 面向人类的详细文档（中文）
│   ├── project_overview.md     # 项目总览
│   ├── installation_guide.md   # 安装指南
│   ├── user_manual.md         # 用户手册
│   ├── troubleshooting.md     # 故障排除
│   └── api_reference.md       # API参考文档
├── copilot_docs/              # AI助手的扩展记忆文件
│   ├── architecture_notes.md  # 架构设计笔记
│   ├── implementation_details.md # 实现细节
│   ├── known_issues.md        # AI任务期间的快速笔记
│   └── development_context.md # 开发上下文信息
└── .github/
    └── instructions/          # AI编程指导
```

### Python后端规范

#### 代码风格
- 使用 Python 3.8+ 特性
- 遵循 PEP 8 规范
- 使用 type hints 进行类型注解
- 函数和类使用 docstring 文档

#### 异步编程
- 优先使用 `asyncio` 和 `async/await`
- 网络请求使用异步客户端（aiohttp, websockets）
- 文件操作使用 `aiofiles`

#### 日志处理
- 使用 Python `logging` 模块
- 配置适当的日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 结构化日志，包含时间戳、组件名称、日志级别
- 支持日志轮转和云端上传

#### 错误处理
- 使用具体的异常类型
- 提供详细的错误消息（支持中文）
- 实现优雅降级和故障恢复
- 记录异常到日志系统

#### 进程管理
- 使用 `subprocess` 和 `psutil` 管理子进程
- 实现进程生命周期监控
- 支持优雅关闭和强制终止
- 进程间通信使用 WebSocket 或 IPC

### 前端规范

#### 技术栈
- NextJS 框架
- 支持手柄导航的UI组件
- 响应式设计，适配电视屏幕
- **构建策略**: 推送源码到仓库，在目标机器上构建

#### 前端部署流程
- **开发环境**: 使用 `npm run dev` 进行开发
- **代码推送**: 仅推送源码，不包含 `out/` 或 `dist/` 目录
- **目标机器构建**: 通过部署脚本自动执行 `npm run build`
- **构建输出**: 生成到 `frontend/out` 目录供后端服务使用

#### UI/UX设计
- 类似游戏主机的界面风格
- 大图标、易读字体，适合客厅环境
- 支持手柄方向键导航
- 流畅的动画和过渡效果

### API设计规范

#### REST API
- 使用 FastAPI 框架
- RESTful 路由设计：`/api/{resource}/{action}`
- 统一的响应格式
- 适当的HTTP状态码

#### WebSocket
- 实时系统状态广播
- 心跳检测机制
- 自动重连逻辑
- 结构化消息格式

### 配置管理

#### 环境变量
- 使用 `.env` 文件管理配置
- 敏感信息（API密钥）不提交到代码库
- 提供 `.env.example` 模板

#### 服务配置
- 可配置的端口和地址
- 日志级别可调整
- 功能开关（如云端上传）

## 开发指南

### 新功能开发
1. 在对应的服务组件中实现功能
2. 更新API文档和接口
3. 添加适当的错误处理和日志
4. 考虑进程间通信和状态同步
5. 更新相关配置和环境变量

### 调试和测试
- 使用 `logging` 进行调试输出
- 每个服务组件可独立运行和测试
- 模拟游戏进程进行集成测试
- 测试进程崩溃恢复机制

### 问题跟踪
- **GitHub Issues**: 使用GitHub原生Issue系统进行主要问题跟踪 (https://github.com/AwesomePenguin/penpen_launcher/issues)
- **Issue模板**: 预定义的Bug、Feature和Performance模板
- **快速笔记**: AI助手在执行任务时发现的问题可临时记录在 `copilot_docs/known_issues.md`
- **工作流程**: 
  - 任务执行中发现问题 → 快速记录到known_issues.md
  - 完成当前任务后 → 创建正式GitHub Issue
  - 定期清理已处理的快速笔记

### 部署考虑
- 目标平台：Windows ITX电脑
- 支持虚拟环境部署
- 提供自动化安装脚本
- 考虑系统资源占用优化

## 特殊要求

### 手柄支持
- PS4/PS5手柄驱动
- PS键长按/短按检测
- 手柄导航映射

### 透明窗口
- Windows API集成
- 窗口层级管理
- 游戏进程检测

### 云端集成
- Cloudflare R2对象存储
- 日志自动上传
- 网络连接状态检测

### 系统集成
- Windows服务或开机自启
- 系统关机/重启集成
- 崩溃转储收集

## 兼容性要求

### 操作系统
- **Windows 11**: 仅支持Windows 11，充分利用新特性
- **架构**: 支持x64架构

### 手柄支持
- **DualShock 4 (DS4)**: PS4手柄完整支持
- **DualSense (DS5)**: PS5手柄完整支持，包括触觉反馈
- **连接方式**: USB有线和蓝牙无线连接

### 游戏启动器兼容性
- **Steam**: 完整支持Steam游戏库
- **Epic Games Store**: 支持Epic平台游戏
- **Battle.net**: 支持暴雪游戏平台
- **自定义启动器**: 
  - Hoyoverse启动器（原神、崩坏：星穹铁道等）
  - 其他第三方游戏启动器
  - 独立游戏可执行文件

### 显示支持
- **分辨率**: 1080p, 1440p, 4K适配
- **刷新率**: 60Hz, 120Hz, 144Hz支持
- **HDR**: Windows 11 HDR支持

## 开发环境

### 开发平台
- **操作系统**: Windows 11 开发环境
- **Python**: 3.8+ 版本
- **Node.js**: 最新LTS版本（用于前端开发）

### 命令行工具
- **PowerShell**: 优先使用PowerShell语法
- **Windows CMD**: 兼容传统批处理脚本
- **示例命令格式**:
  ```powershell
  # PowerShell 语法
  Get-Process | Where-Object {$_.Name -eq "python"}
  
  # 批处理兼容
  tasklist | findstr python
  ```

## 部署和更新策略

### 目标部署
- **GitHub仓库**: 代码托管在GitHub，无远程服务器
- **本地拉取**: 在目标ITX电脑上手动git pull更新
- **一键更新脚本**: 简化本地更新流程

### 推荐的更新工作流程
```powershell
# 1. 开发机推送到GitHub
git add .
git commit -m "Update features"
git push origin main

# 2. 目标机器更新（手动或脚本）
.\update.bat
```

### 部署脚本设计

#### update.bat - 一键更新脚本
```batch
@echo off
echo 正在检查更新...

REM 保存当前运行状态
echo 停止服务...
taskkill /f /im python.exe 2>nul

REM 备份当前版本
if exist "backup" rd /s /q backup
mkdir backup
xcopy /s /e /y *.py backup\
if exist "frontend\out" xcopy /s /e /y frontend\out backup\frontend_out\

REM 拉取最新代码
echo 拉取最新代码...
git pull origin main

REM 检查是否有新的依赖
echo 检查依赖更新...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM 构建前端（在目标机器上）
if exist "frontend\package.json" (
    echo 构建前端...
    cd frontend
    
    REM 检查Node.js
    node --version >nul 2>&1
    if errorlevel 1 (
        echo 错误: Node.js未安装，无法构建前端
        cd ..
        goto :error
    )
    
    REM 安装/更新前端依赖
    echo 安装前端依赖...
    npm install
    
    REM 执行构建
    echo 执行前端构建...
    npm run build
    
    REM 检查构建是否成功
    if not exist "out\index.html" (
        echo 错误: 前端构建失败
        cd ..
        goto :error
    )
    
    echo 前端构建成功
    cd ..
) else (
    echo 警告: 未找到前端项目文件
)

REM 重启服务
echo 重启服务...
start "" python launcher.py

echo 更新完成！
pause
exit /b 0

:error
echo 更新失败，尝试回滚...
call rollback.bat
exit /b 1
```

#### install.bat - 初始安装脚本
```batch
@echo off
echo 安装 PenPen Launcher...

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 请先安装Git
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 请先安装Python 3.8+
    pause
    exit /b 1
)

REM 创建虚拟环境
echo 创建Python虚拟环境...
python -m venv venv
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 创建必要目录
mkdir logs 2>nul
mkdir screenshots 2>nul
mkdir backup 2>nul

REM 检查Node.js（如果需要构建前端）
if exist "frontend\package.json" (
    echo 检查Node.js...
    node --version >nul 2>&1
    if errorlevel 1 (
        echo 警告: Node.js未安装，前端需要手动构建
    ) else (
        echo 安装前端依赖...
        cd frontend
        npm install
        npm run build
        cd ..
    )
)

REM 复制环境变量模板
if not exist ".env" (
    copy .env.example .env
    echo 请编辑 .env 文件配置必要参数
)

echo.
echo 安装完成！
echo 下一步:
echo 1. 编辑 .env 文件
echo 2. 运行 start.bat 启动系统
pause
```

#### rollback.bat - 回滚脚本
```batch
@echo off
echo 回滚到上一版本...

if not exist "backup" (
    echo 错误: 没有找到备份文件
    pause
    exit /b 1
)

REM 停止服务
taskkill /f /im python.exe 2>nul

REM 恢复备份
echo 恢复文件...
xcopy /s /e /y backup\*.py .
if exist "backup\frontend_out" (
    if exist "frontend\out" rd /s /q frontend\out
    xcopy /s /e /y backup\frontend_out frontend\out\
)

REM 重启服务
echo 重启服务...
start "" python launcher.py

echo 回滚完成！
pause
```

### 版本控制策略
- **Git标签**: 使用语义化版本标签 (v1.0.0, v1.1.0)
- **发布分支**: main分支保持稳定，开发用feature分支
- **本地版本检查**: 实现简单的版本比较机制

### 应用内更新功能设计
```python
# 在core_api.py中添加更新检查端点
@app.get("/api/system/check-update")
async def check_for_updates():
    """检查GitHub是否有新版本"""
    try:
        # 获取本地Git信息
        local_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=".",
            text=True
        ).strip()
        
        # 获取远程最新commit（需要fetch）
        subprocess.run(["git", "fetch", "origin", "main"], cwd=".")
        remote_commit = subprocess.check_output(
            ["git", "rev-parse", "origin/main"],
            cwd=".",
            text=True
        ).strip()
        
        has_update = local_commit != remote_commit
        
        return {
            "has_update": has_update,
            "local_commit": local_commit[:7],
            "remote_commit": remote_commit[:7]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/system/update")
async def perform_update():
    """执行系统更新"""
    try:
        # 调用更新脚本
        subprocess.Popen(["update.bat"], shell=True)
        return {"status": "update_started"}
    except Exception as e:
        return {"error": str(e)}
```

### 部署最佳实践
1. **预部署检查**: 确保Git、Python、Node.js已安装
2. **自动备份**: 每次更新前自动备份当前版本
3. **依赖管理**: 检查requirements.txt变化并自动更新
4. **服务重启**: 优雅停止和重启launcher服务
5. **错误恢复**: 更新失败时自动回滚到备份版本

## 开发注意事项

1. **进程管理**: 确保所有子进程能够正确清理
2. **资源管理**: 注意内存和文件句柄泄漏
3. **异常恢复**: 实现robust的错误恢复机制
4. **用户体验**: 保持界面响应性，避免阻塞操作
5. **安全性**: 验证外部输入，防止命令注入
6. **可维护性**: 模块化设计，便于独立开发和调试
7. **Windows 11特性**: 充分利用Windows 11新API和功能
8. **手柄集成**: 深度集成DS4/DS5手柄特性（震动、LED等）