# PenPen Launcher Backend Overview

## 项目概述

PenPen Launcher 后端是一个基于 Python 和 FastAPI 的微服务架构系统，专为电视游戏环境设计。后端负责游戏发现、启动管理、系统监控和与前端的实时通信。

## 技术栈

- **框架**: FastAPI (异步 Web 框架)
- **语言**: Python 3.8+ (严格类型检查)
- **进程管理**: asyncio + subprocess
- **系统监控**: psutil
- **WebSocket**: FastAPI WebSocket 支持
- **游戏平台集成**: Steam、Epic Games、Battle.net、自定义游戏
- **配置管理**: python-dotenv + YAML

## 核心功能模块

### 1. 游戏发现系统 (Game Discovery)
**主要功能:**
- 扫描已安装的游戏平台和游戏
- 提取游戏元数据（名称、图标、描述）
- 检测游戏安装状态和路径
- 支持多平台游戏库合并

**支持的平台:**
- **Steam**: 通过注册表和 `libraryfolders.vdf` 扫描
- **Epic Games**: 扫描 Epic Games Launcher 安装目录
- **Battle.net**: 检测暴雪游戏安装
- **Hoyoverse**: 原神、崩坏等游戏检测
- **自定义游戏**: 用户手动添加的可执行文件

### 2. 游戏启动管理 (Game Launch Management)
**主要功能:**
- 安全的游戏进程启动和监控
- 平台特定的启动逻辑（Steam、Epic、Battle.net）
- 游戏进程状态跟踪
- 启动前检查和验证

**启动流程:**
1. 验证游戏安装状态
2. 选择合适的启动器（Steam、Epic 等）
3. 构建启动命令和参数
4. 异步启动游戏进程
5. 监控进程状态和性能

### 3. 系统状态监控 (System Monitoring)
**主要功能:**
- 实时 CPU、内存、存储使用率
- 运行中游戏的资源监控
- 网络连接状态检测
- 系统温度和性能指标

### 4. REST API 接口
**核心端点:**
```python
# 游戏库管理
GET    /api/games                    # 获取游戏列表
GET    /api/games/{id}               # 获取游戏详情
POST   /api/games/{id}/launch        # 启动游戏
GET    /api/games/{id}/image         # 获取游戏图标

# 系统状态
GET    /api/system/status            # 系统状态信息
GET    /api/system/health            # 健康检查
POST   /api/system/restart           # 重启系统

# 配置管理
GET    /api/settings                 # 获取系统设置
PUT    /api/settings                 # 更新系统设置
```

### 5. WebSocket 实时通信
**消息类型:**
- `gameStatusChange`: 游戏启动/退出状态变化
- `systemStatusUpdate`: 系统性能指标更新
- `gameLibraryUpdate`: 游戏库变化通知

## 最小可行产品 (MVP) 架构

### 阶段 1: 核心基础设施
```
backend/
├── launcher.py              # 主启动脚本
├── core_api.py             # FastAPI 应用和路由
├── game_scanner.py         # 游戏发现和扫描
├── process_manager.py      # 进程启动和管理
├── system_monitor.py       # 系统状态监控
├── config.py               # 配置管理
├── models.py               # 数据模型定义
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量模板
└── README.md              # 后端文档
```

### 阶段 2: 平台集成
```
backend/platforms/
├── __init__.py
├── steam.py               # Steam 平台集成
├── epic.py                # Epic Games 集成
├── battlenet.py           # Battle.net 集成
├── hoyoverse.py           # Hoyoverse 游戏集成
└── custom.py              # 自定义游戏管理
```

### 阶段 3: 高级功能
```
backend/services/
├── websocket_manager.py   # WebSocket 连接管理
├── image_service.py       # 游戏图标处理
├── config_service.py      # 配置文件管理
└── logging_service.py     # 日志管理
```

## 数据模型设计

### 游戏信息模型
```python
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class GamePlatform(str, Enum):
    STEAM = "steam"
    EPIC = "epic"
    BATTLENET = "battlenet"
    HOYOVERSE = "hoyoverse"
    CUSTOM = "custom"

class GameCategory(str, Enum):
    ACTION = "action"
    ADVENTURE = "adventure"
    RPG = "rpg"
    STRATEGY = "strategy"
    SIMULATION = "simulation"
    SPORTS = "sports"
    OTHER = "other"

class GameInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[str] = None
    image_url: Optional[str] = None
    executable_path: str
    platform: GamePlatform
    category: GameCategory
    is_installed: bool
    last_played: Optional[str] = None
    play_time: Optional[int] = None  # 分钟
    rating: Optional[int] = None
    tags: List[str] = []

class LaunchRequest(BaseModel):
    game_id: str
    launch_options: Optional[dict] = None

class LaunchResult(BaseModel):
    success: bool
    process_id: Optional[int] = None
    error: Optional[str] = None
```

### 系统状态模型
```python
class SystemStatus(BaseModel):
    cpu: dict  # {"usage": 45.2, "temperature": 65}
    memory: dict  # {"used": 8.2, "total": 16.0, "percentage": 51.25}
    storage: dict  # {"used": 500, "total": 1000, "percentage": 50.0}
    network: dict  # {"connected": True, "type": "wifi"}
    active_game: Optional[dict] = None
```

## 游戏平台集成策略

### Steam 集成
```python
# Steam 游戏发现策略
class SteamScanner:
    def scan_steam_games(self) -> List[GameInfo]:
        # 1. 读取 Steam 注册表路径
        # 2. 解析 libraryfolders.vdf 文件
        # 3. 扫描每个库文件夹的 appmanifest_*.acf 文件
        # 4. 提取游戏名称、路径、状态
        # 5. 获取 Steam Web API 的额外元数据
        pass
    
    def launch_steam_game(self, app_id: str) -> subprocess.Popen:
        # steam://rungameid/{app_id} 协议启动
        pass
```

### Epic Games 集成
```python
class EpicScanner:
    def scan_epic_games(self) -> List[GameInfo]:
        # 1. 扫描 Epic Games Launcher 数据文件
        # 2. 读取已安装游戏的 .item 文件
        # 3. 提取游戏路径和元数据
        pass
    
    def launch_epic_game(self, game_id: str) -> subprocess.Popen:
        # com.epicgames.launcher://apps/{game_id}?action=launch
        pass
```

### 自定义游戏支持
```python
class CustomGameManager:
    def add_custom_game(self, game_info: GameInfo) -> bool:
        # 允许用户手动添加任意可执行文件
        pass
    
    def validate_executable(self, path: str) -> bool:
        # 验证可执行文件的有效性
        pass
```

## API 设计规范

### RESTful API 设计
```python
@app.get("/api/games", response_model=List[GameInfo])
async def get_games(
    platform: Optional[GamePlatform] = None,
    category: Optional[GameCategory] = None,
    installed_only: bool = True
):
    """获取游戏列表，支持平台和分类筛选"""
    pass

@app.post("/api/games/{game_id}/launch", response_model=LaunchResult)
async def launch_game(game_id: str, request: LaunchRequest):
    """启动指定游戏"""
    pass

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    """获取当前系统状态"""
    pass
```

### WebSocket 消息格式
```python
class WebSocketMessage(BaseModel):
    type: str  # "gameStatusChange", "systemStatusUpdate"
    data: dict
    timestamp: str

# 示例消息
{
    "type": "gameStatusChange",
    "data": {
        "game_id": "steam_12345",
        "status": "launched",
        "process_id": 8432
    },
    "timestamp": "2025-10-31T10:30:00Z"
}
```

## 配置管理

### 环境变量配置
```bash
# .env 文件示例
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
LOG_LEVEL=INFO
ENABLE_WEBSOCKET=true

# Steam 配置
STEAM_API_KEY=your_steam_api_key
STEAM_USER_ID=your_steam_id

# Epic Games 配置
EPIC_LAUNCHER_PATH=C:\Program Files (x86)\Epic Games\Launcher

# 自定义设置
SCAN_INTERVAL=300  # 游戏库扫描间隔（秒）
ENABLE_AUTO_LAUNCH=true
DEFAULT_LAUNCH_TIMEOUT=30
```

### YAML 配置文件
```yaml
# config.yml
launcher:
  name: "PenPen Launcher"
  version: "1.0.0"
  auto_scan: true
  scan_interval: 300

platforms:
  steam:
    enabled: true
    auto_detect: true
    api_key: "${STEAM_API_KEY}"
  
  epic:
    enabled: true
    launcher_path: "C:\\Program Files (x86)\\Epic Games\\Launcher"
  
  custom:
    enabled: true
    allow_user_add: true

system:
  monitoring:
    enabled: true
    update_interval: 5  # 秒
    
  logging:
    level: "INFO"
    file: "logs/launcher.log"
    max_size: "10MB"
    backup_count: 5
```

## 进程管理和安全

### 安全启动策略
```python
class SecureProcessManager:
    async def launch_game_secure(self, game_info: GameInfo) -> LaunchResult:
        # 1. 验证可执行文件存在性和权限
        # 2. 检查文件签名（可选）
        # 3. 构建安全的启动参数
        # 4. 设置进程隔离和资源限制
        # 5. 启动进程并监控
        pass
    
    def validate_executable_safety(self, exe_path: str) -> bool:
        # 基础安全检查
        pass
```

### 进程监控
```python
class ProcessMonitor:
    def monitor_game_process(self, process_id: int) -> None:
        # 监控游戏进程的 CPU、内存使用
        # 检测进程崩溃和异常退出
        # 记录游戏时长和性能数据
        pass
```

## 错误处理和日志

### 异常处理策略
```python
class LauncherException(Exception):
    """启动器基础异常类"""
    pass

class GameNotFound(LauncherException):
    """游戏未找到异常"""
    pass

class LaunchFailed(LauncherException):
    """游戏启动失败异常"""
    pass

class PlatformNotSupported(LauncherException):
    """平台不支持异常"""
    pass
```

### 结构化日志
```python
import structlog

logger = structlog.get_logger("penpen_launcher")

# 日志示例
logger.info(
    "游戏启动成功",
    game_id="steam_12345",
    game_name="Cyberpunk 2077",
    platform="steam",
    process_id=8432,
    launch_time=2.34
)
```

## 性能优化

### 异步处理
- **游戏扫描**: 异步并发扫描多个平台
- **系统监控**: 非阻塞的系统状态收集
- **WebSocket**: 高效的实时通信

### 缓存策略
- **游戏列表缓存**: 减少重复扫描开销
- **图标缓存**: 本地存储游戏图标
- **元数据缓存**: API 请求结果缓存

### 资源管理
- **内存使用**: 控制游戏列表和图标的内存占用
- **文件句柄**: 及时关闭文件和进程句柄
- **网络连接**: WebSocket 连接池管理

## 部署和运行

### 开发环境启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python launcher.py

# 或使用 uvicorn
uvicorn core_api:app --reload --host 0.0.0.0 --port 8000
```

### 生产部署
```bash
# 使用 systemd 服务
sudo systemctl start penpen-launcher
sudo systemctl enable penpen-launcher

# 或使用 Docker
docker run -d --name penpen-launcher \
  -p 8000:8000 \
  -v /games:/games:ro \
  penpen/launcher:latest
```

## 测试策略

### 单元测试
- **游戏扫描**: 模拟不同平台的游戏安装
- **进程管理**: 测试游戏启动和监控逻辑
- **API 端点**: 测试所有 REST API 响应

### 集成测试
- **平台集成**: 实际测试 Steam、Epic 等平台
- **前后端通信**: 测试 API 和 WebSocket 集成
- **系统兼容性**: 不同 Windows 版本的兼容测试

### 性能测试
- **游戏库扫描**: 大量游戏的扫描性能
- **并发启动**: 多游戏同时启动的处理
- **长期运行**: 内存泄漏和稳定性测试

## 开发计划

### 第一阶段 (1-2 天)
- [x] 项目结构搭建
- [ ] FastAPI 基础设施
- [ ] 基础游戏扫描 (Steam)
- [ ] 简单的游戏启动功能
- [ ] REST API 核心端点

### 第二阶段 (2-3 天)
- [ ] 多平台支持 (Epic, Battle.net)
- [ ] 系统状态监控
- [ ] WebSocket 实时通信
- [ ] 图标和元数据处理

### 第三阶段 (1-2 天)
- [ ] 错误处理完善
- [ ] 配置管理系统
- [ ] 日志和监控优化
- [ ] 前后端集成测试

---

这个后端架构设计为 PenPen Launcher 提供了完整的游戏管理和系统监控功能，重点关注简单性、可靠性和与前端的无缝集成。所有组件都按照项目的编程规范进行设计，确保代码质量和可维护性。