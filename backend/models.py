"""
PenPen Launcher 数据模型定义

这个模块定义了所有与前端 TypeScript 类型匹配的 Pydantic 模型。
确保前后端数据结构的一致性。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class GamePlatform(str, Enum):
    """游戏平台枚举"""
    STEAM = "steam"
    EPIC = "epic"
    BATTLENET = "battlenet"
    HOYOVERSE = "hoyoverse"
    CUSTOM = "custom"


class GameCategory(str, Enum):
    """游戏分类枚举"""
    ACTION = "action"
    ADVENTURE = "adventure"
    RPG = "rpg"
    STRATEGY = "strategy"
    SIMULATION = "simulation"
    SPORTS = "sports"
    OTHER = "other"


class GameInfo(BaseModel):
    """游戏信息模型 - 与前端 TypeScript GameInfo 接口匹配"""
    id: str = Field(..., description="游戏唯一标识符")
    name: str = Field(..., description="游戏名称")
    description: Optional[str] = Field(None, description="游戏描述")
    developer: Optional[str] = Field(None, description="开发商")
    publisher: Optional[str] = Field(None, description="发行商")
    release_date: Optional[str] = Field(None, description="发布日期")
    image_url: Optional[str] = Field(None, description="游戏封面图片URL")
    executable_path: str = Field(..., description="游戏可执行文件路径")
    platform: GamePlatform = Field(..., description="游戏平台")
    category: GameCategory = Field(..., description="游戏分类")
    is_installed: bool = Field(..., description="是否已安装")
    last_played: Optional[datetime] = Field(None, description="最后游玩时间")
    play_time: Optional[int] = Field(None, description="游戏时长（分钟）")
    rating: Optional[int] = Field(None, ge=1, le=5, description="游戏评分 (1-5)，None表示无评分")
    tags: List[str] = Field(default_factory=list, description="游戏标签")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LaunchOptions(BaseModel):
    """游戏启动选项"""
    launcher_preference: Optional[GamePlatform] = Field(None, description="首选启动器")
    additional_args: Optional[List[str]] = Field(None, description="额外启动参数")
    fullscreen: Optional[bool] = Field(None, description="是否全屏启动")


class LaunchRequest(BaseModel):
    """游戏启动请求"""
    game_id: str = Field(..., description="游戏ID")
    launch_options: Optional[LaunchOptions] = Field(None, description="启动选项")


class LaunchResult(BaseModel):
    """游戏启动结果"""
    success: bool = Field(..., description="是否启动成功")
    process_id: Optional[int] = Field(None, description="进程ID")
    error: Optional[str] = Field(None, description="错误信息")


class SystemCPU(BaseModel):
    """CPU 状态"""
    usage: float = Field(..., description="CPU 使用率 (%)")
    temperature: Optional[float] = Field(None, description="CPU 温度 (°C)")


class SystemMemory(BaseModel):
    """内存状态"""
    used: float = Field(..., description="已使用内存 (GB)")
    total: float = Field(..., description="总内存 (GB)")
    percentage: float = Field(..., description="内存使用率 (%)")


class SystemStorage(BaseModel):
    """存储状态"""
    used: float = Field(..., description="已使用存储 (GB)")
    total: float = Field(..., description="总存储 (GB)")
    percentage: float = Field(..., description="存储使用率 (%)")


class SystemNetwork(BaseModel):
    """网络状态"""
    connected: bool = Field(..., description="是否连接到网络")
    type: Optional[str] = Field(None, description="连接类型 (wifi/ethernet)")
    speed: Optional[float] = Field(None, description="网络速度 (Mbps)")


class ActiveGame(BaseModel):
    """当前运行的游戏"""
    name: str = Field(..., description="游戏名称")
    pid: int = Field(..., description="进程ID")
    start_time: datetime = Field(..., description="启动时间")


class SystemStatus(BaseModel):
    """系统状态 - 与前端 TypeScript SystemStatus 接口匹配"""
    cpu: SystemCPU
    memory: SystemMemory
    storage: SystemStorage
    network: SystemNetwork
    active_game: Optional[ActiveGame] = Field(None, description="当前运行的游戏")


class WebSocketMessage(BaseModel):
    """WebSocket 消息格式"""
    type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    timestamp: str = Field(..., description="时间戳")


class ApiResponse(BaseModel):
    """通用 API 响应格式"""
    status: str = Field(..., description="响应状态 (success/error)")
    data: Optional[Any] = Field(None, description="响应数据")
    error_message: Optional[str] = Field(None, description="错误信息")
    timestamp: str = Field(..., description="响应时间戳")

    @classmethod
    def success(cls, data: Any = None) -> "ApiResponse":
        """创建成功响应"""
        return cls(
            status="success",
            data=data,
            error_message=None,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def error(cls, error_message: str) -> "ApiResponse":
        """创建错误响应"""
        return cls(
            status="error",
            data=None,
            error_message=error_message,
            timestamp=datetime.now().isoformat()
        )


class UpdateInfo(BaseModel):
    """系统更新信息"""
    available: bool = Field(..., description="是否有可用更新")
    current_version: str = Field(..., description="当前版本")
    latest_version: Optional[str] = Field(None, description="最新版本")
    download_url: Optional[str] = Field(None, description="下载链接")
    changelog: Optional[str] = Field(None, description="更新日志")


# Steam 特定模型
class SteamAppInfo(BaseModel):
    """Steam 应用信息"""
    app_id: str = Field(..., description="Steam App ID")
    name: str = Field(..., description="应用名称")
    install_dir: str = Field(..., description="安装目录")
    state_flags: int = Field(..., description="状态标志")
    last_updated: int = Field(..., description="最后更新时间戳")


class SteamLibraryFolder(BaseModel):
    """Steam 库文件夹"""
    path: str = Field(..., description="库文件夹路径")
    label: str = Field(..., description="库标签")
    mounted: bool = Field(..., description="是否挂载")
    apps: Dict[str, str] = Field(default_factory=dict, description="应用列表")


# Epic Games 特定模型
class EpicGameInfo(BaseModel):
    """Epic Games 游戏信息"""
    app_name: str = Field(..., description="应用名称")
    display_name: str = Field(..., description="显示名称")
    install_location: str = Field(..., description="安装位置")
    executable_name: str = Field(..., description="可执行文件名")


# 配置模型
class LauncherConfig(BaseModel):
    """启动器配置"""
    name: str = Field(default="PenPen Launcher", description="启动器名称")
    version: str = Field(default="1.0.0", description="版本号")
    auto_scan: bool = Field(default=True, description="自动扫描游戏")
    scan_interval: int = Field(default=300, description="扫描间隔（秒）")


class PlatformConfig(BaseModel):
    """平台配置"""
    enabled: bool = Field(default=True, description="是否启用")
    auto_detect: bool = Field(default=True, description="自动检测")


class SystemConfig(BaseModel):
    """系统配置"""
    monitoring_enabled: bool = Field(default=True, description="是否启用监控")
    update_interval: int = Field(default=5, description="更新间隔（秒）")
    log_level: str = Field(default="INFO", description="日志级别")