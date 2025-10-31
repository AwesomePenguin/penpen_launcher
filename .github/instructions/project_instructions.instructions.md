---
applyTo: '**'
---

# PenPen Launcher 项目指导说明

## 目录

1. [项目概述](#项目概述)
2. [项目架构](#项目架构)
3. [编程规范](#编程规范)
   - [语言支持](#语言支持)
   - [命名规范](#命名规范)
   - [Python后端规范](#python后端规范)
   - [前端规范](#前端规范)
   - [API设计规范](#api设计规范)
   - [配置管理](#配置管理)
4. [开发指南](#开发指南)
5. [特殊要求](#特殊要求)
6. [兼容性要求](#兼容性要求)
7. [开发环境](#开发环境)
8. [部署和更新策略](#部署和更新策略)
9. [开发注意事项](#开发注意事项)

---

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

#### 代码风格和PEP合规性

##### PEP 8 - 代码风格指南
- **行长度**: 最大79字符，文档字符串和注释72字符
- **缩进**: 使用4个空格，禁用制表符
- **空行**: 顶级函数和类定义前后两个空行，方法定义前后一个空行
- **导入**: 每行一个导入，标准库→第三方→本地模块顺序
- **引号**: 优先使用双引号，保持一致性

```python
# ✅ 正确的导入和类定义示例
import asyncio
import logging
from typing import Optional, Dict, List

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

from .process_manager import ProcessManager

class SystemManager:
    """Manages system state and game processes."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.active_game_pid: Optional[int] = None
        self.system_state: str = "booting"
    
    async def launch_game(self, request: GameLaunchRequest) -> Dict[str, str]:
        """Launch a game with given parameters."""
        try:
            process_info = await self._start_game_process(request)
            return {"status": "success", "pid": str(process_info.pid)}
        except Exception as e:
            self.logger.error(f"游戏启动失败: {e}")
            raise GameLaunchError(f"启动失败: {str(e)}") from e
```

##### PEP 484/526 - 类型提示
- **所有公共函数**: 必须包含类型提示
- **复杂返回值**: 使用 Union, Optional, Dict, List 等
- **异步函数**: 明确 Coroutine 返回类型
- **类属性**: 使用变量注解

```python
# 类型提示示例
from typing import Optional, Dict, List, Protocol

class GameProcessProtocol(Protocol):
    async def start(self, executable: Path) -> int: ...
    async def terminate(self, pid: int) -> bool: ...

class ProcessManager:
    active_processes: Dict[str, int] = {}
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = config_path or Path("config.yml")
    
    async def register_callback(
        self, 
        callback: Callable[[str], Coroutine[Any, Any, None]]
    ) -> None:
        """Register process event callback."""
        self._callbacks.append(callback)
```

##### PEP 257 - 文档字符串规范
- **所有公共模块、类、函数**: 必须有docstring
- **格式**: 使用Google风格或NumPy风格
- **内容**: 简要描述、参数、返回值、异常

```python
class WebSocketManager:
    """Manages WebSocket connections for real-time communication.
    
    Attributes:
        clients: Set of active WebSocket connections
        message_queue: Queue for outbound messages
    """
    
    async def broadcast_message(
        self, 
        message: Dict[str, Any], 
        exclude_client: Optional[WebSocket] = None
    ) -> int:
        """Broadcast message to all connected clients.
        
        Args:
            message: JSON-serializable message to broadcast
            exclude_client: Optional client to exclude from broadcast
            
        Returns:
            Number of clients that received the message
            
        Raises:
            BroadcastError: If message serialization fails
        """
        pass
```

##### PEP 585/604 - 现代类型注解（Python 3.9+）
- **内置容器**: 使用 `list[str]` 替代 `List[str]`
- **联合类型**: 使用 `str | None` 替代 `Union[str, None]`
- **向后兼容**: 项目支持Python 3.8+，继续使用typing模块

##### 代码质量工具配置
```python
# pyproject.toml 配置示例
[tool.black]
line-length = 79
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 79
multi_line_output = 3

[tool.flake8]
max-line-length = 79
extend-ignore = ["E203", "W503"]
per-file-ignores = [
    "__init__.py:F401",
]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
```

#### 异步编程最佳实践
- **优先使用 `asyncio`**: 所有I/O操作使用async/await
- **异步客户端**: aiohttp用于HTTP，websockets用于WebSocket
- **资源管理**: 使用async context managers
- **错误传播**: 正确处理async异常

```python
# 异步编程示例
import aiohttp
from contextlib import asynccontextmanager

class ApiClient:
    @asynccontextmanager
    async def session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession()
        try:
            yield session
        finally:
            await session.close()
    
    async def get_game_info(self, game_id: str) -> Dict[str, Any]:
        async with self.session() as session:
            async with session.get(f"{self.base_url}/games/{game_id}") as response:
                response.raise_for_status()
                return await response.json()
```

#### 日志处理
- **结构化日志**: 使用dictConfig或logging.config
- **日志级别**: 正确使用DEBUG、INFO、WARNING、ERROR、CRITICAL
- **日志格式**: 包含时间戳、模块名、级别、消息
- **日志轮转**: 防止日志文件过大

**配置要点:**
- Console handler (INFO级别) + File handler (DEBUG级别)
- RotatingFileHandler with 10MB maxBytes, 5 backup files
- 统一格式: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

#### 错误处理和异常设计
- **自定义异常**: 为不同错误类型创建专门的异常类
- **异常链**: 使用 `raise ... from ...` 保留原始异常
- **异常文档**: 在docstring中记录可能的异常

```python
# 异常设计示例
class LauncherError(Exception):
    """Base exception for launcher errors."""
    pass

class GameLaunchError(LauncherError):
    """Raised when game launch fails."""
    
    def __init__(self, message: str, game_id: str, exit_code: Optional[int] = None):
        super().__init__(message)
        self.game_id = game_id
        self.exit_code = exit_code

# 异常处理模式
async def launch_game_safe(game_id: str) -> None:
    try:
        await launch_game(game_id)
    except subprocess.SubprocessError as e:
        raise GameLaunchError(f"游戏启动失败: {e}", game_id=game_id) from e
```

#### 进程管理
- **subprocess 最佳实践**: 使用 asyncio.create_subprocess_*
- **资源清理**: 确保进程正确终止
- **信号处理**: 优雅关闭机制
- **进程监控**: 使用 psutil 进行高级进程管理

```python
# 进程管理模式
class ProcessManager:
    def __init__(self) -> None:
        self.managed_processes: Dict[str, asyncio.subprocess.Process] = {}
    
    async def start_managed_process(
        self, name: str, cmd: List[str]
    ) -> asyncio.subprocess.Process:
        process = await asyncio.create_subprocess_exec(*cmd)
        self.managed_processes[name] = process
        return process
    
    async def shutdown_all(self) -> None:
        """Gracefully shutdown all managed processes."""
        for name, process in self.managed_processes.items():
            if process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
```

### 前端规范

#### 技术栈
- NextJS 框架（Pages Router）
- TypeScript + React + Tailwind CSS
- 支持手柄导航的UI组件
- 响应式设计，适配电视屏幕
- **构建策略**: 推送源码到仓库，在目标机器上构建

#### TypeScript/TSX 编程规范

##### 严格类型检查
- **启用严格模式**: 确保 `tsconfig.json` 中 `"strict": true`
- **禁用 any 类型**: 避免使用 `any`，优先使用具体类型或 `unknown`
- **强制参数类型**: 所有函数参数必须明确指定类型
- **返回值类型**: 复杂函数应明确指定返回值类型

```typescript
// ✅ 正确示例
interface GameLaunchProps {
  game: GameInfo;
  onLaunch: (gameId: string) => Promise<void>;
  isLaunching?: boolean;
}

const GameCard: React.FC<GameLaunchProps> = ({ game, onLaunch, isLaunching = false }) => {
  const handleLaunch = async (): Promise<void> => {
    try {
      await onLaunch(game.id);
    } catch (error: unknown) {
      console.error('启动游戏失败:', error);
    }
  };

  return <div className="game-card">{/* JSX 内容 */}</div>;
};

// ❌ 错误示例 - 避免 any
const BadComponent = ({ game, onLaunch }: any) => { /* 缺少类型检查 */ };
```

##### 接口和类型定义
- **自定义接口**: 为复杂数据结构定义明确的接口
- **Props 接口**: 每个组件的 props 都应有对应的接口定义
- **API 响应类型**: 为后端 API 响应定义类型接口
- **事件处理器类型**: 明确指定事件处理器的参数类型

```typescript
// API 响应类型
interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
  timestamp: string;
}

// 事件处理器类型
interface GameLibraryProps {
  games: GameInfo[];
  onGameSelect: (game: GameInfo) => void;
  onGameLaunch: (gameId: string) => Promise<void>;
}

// React Hook 返回值类型
interface UseGameLibraryReturn {
  games: GameInfo[];
  loading: boolean;
  error: string | null;
  refreshGames: () => Promise<void>;
}
```

##### React 组件规范
- **函数组件**: 优先使用函数组件 + Hooks
- **React.FC 类型**: 使用 `React.FC<PropsInterface>` 明确组件类型
- **useState 泛型**: 为复杂状态指定泛型类型
- **useEffect 依赖**: 明确指定依赖数组，避免无限重渲染

```typescript
// 组件状态类型
interface GameLibraryState {
  games: GameInfo[];
  selectedGame: GameInfo | null;
  loading: boolean;
  error: string | null;
}

const GameLibrary: React.FC<GameLibraryProps> = ({ 
  onGameSelect, 
  onGameLaunch 
}) => {
  const [state, setState] = useState<GameLibraryState>({
    games: [],
    selectedGame: null,
    loading: true,
    error: null
  });

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === 'Enter' && state.selectedGame) {
      onGameSelect(state.selectedGame);
    }
  };

  return <div onKeyDown={handleKeyDown}>{/* 组件内容 */}</div>;
};
```

##### 手柄导航类型定义
```typescript
// 手柄输入类型
interface GamepadButton {
  pressed: boolean;
  touched: boolean;
  value: number;
}

interface GamepadState {
  connected: boolean;
  index: number;
  buttons: GamepadButton[];
  axes: number[];
  timestamp: number;
}

interface NavigationHandler {
  onUp: () => void;
  onDown: () => void;
  onLeft: () => void;
  onRight: () => void;
  onConfirm: () => void;
  onCancel: () => void;
  onMenu: () => void;
}

// 导航上下文类型
interface GamepadContextType {
  gamepadState: GamepadState | null;
  isConnected: boolean;
  registerNavigationHandler: (handler: NavigationHandler) => void;
  unregisterNavigationHandler: () => void;
}
```

##### ESLint 配置强化
```javascript
// 推荐的 ESLint 规则补充
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // TypeScript 严格规则
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/prefer-interface': 'error',
      
      // React 规则
      'react/prop-types': 'off', // TypeScript 已提供类型检查
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error',
      
      // 一般代码质量
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error'
    }
  }
]);
```

##### 代码组织规范
- **文件命名**: 组件文件使用 PascalCase（`GameCard.tsx`）
- **目录结构**: 
  ```
  src/
  ├── components/          # 可复用组件
  │   ├── GameCard/
  │   │   ├── GameCard.tsx
  │   │   ├── GameCard.module.css
  │   │   └── index.ts
  ├── pages/              # 页面组件
  ├── hooks/              # 自定义 Hooks
  ├── types/              # 类型定义文件
  ├── utils/              # 工具函数
  ├── contexts/           # React Context
  └── services/           # API 服务
  ```
- **导入顺序**: React → 第三方库 → 项目内部模块
- **接口命名**: 使用 `Interface` 或描述性名称，避免 `I` 前缀

##### 性能优化
- **React.memo**: 对重渲染频繁的组件使用 memo
- **useCallback**: 为传递给子组件的函数使用 useCallback
- **useMemo**: 为计算密集型操作使用 useMemo
- **懒加载**: 大型组件使用 React.lazy + Suspense

```typescript
// 性能优化示例
const GameCard = React.memo<GameCardProps>(({ game, onLaunch }) => {
  const handleLaunch = useCallback(async () => {
    await onLaunch(game.id);
  }, [game.id, onLaunch]);

  const gameImage = useMemo(() => {
    return game.image_url || '/default-game-image.png';
  }, [game.image_url]);

  return (
    <div onClick={handleLaunch}>
      <img src={gameImage} alt={game.name} />
    </div>
  );
});
```

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
- **可访问性**: 支持键盘和手柄导航，合理的焦点管理
- **响应式设计**: 适配不同电视分辨率（1080p, 1440p, 4K）

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
**关键步骤**:
1. 停止当前运行的Python进程
2. 备份当前版本到backup目录
3. Git pull拉取最新代码
4. 检查并更新Python依赖 (`pip install -r requirements.txt`)
5. 构建前端 (`npm install && npm run build`)
6. 重启launcher服务
7. 失败时自动调用rollback.bat

#### install.bat - 初始安装脚本
**关键步骤**:
1. 检查Git、Python、Node.js安装状态
2. 创建Python虚拟环境 (`python -m venv venv`)
3. 安装Python依赖
4. 创建必要目录 (logs, screenshots, backup)
5. 构建前端项目
6. 复制.env.example为.env

#### rollback.bat - 回滚脚本
**关键步骤**:
1. 停止服务
2. 从backup目录恢复文件
3. 重启服务

### 版本控制策略
- **Git标签**: 使用语义化版本标签 (v1.0.0, v1.1.0)
- **发布分支**: main分支保持稳定，开发用feature分支
- **本地版本检查**: 实现简单的版本比较机制

### 应用内更新功能设计
在core_api.py中添加更新检查和执行端点:
- `/api/system/check-update`: 检查GitHub是否有新版本
- `/api/system/update`: 执行系统更新 (调用update.bat)

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