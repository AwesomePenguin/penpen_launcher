"""
PenPen Launcher 核心 API 服务

基于 FastAPI 的异步 Web 服务，提供游戏管理、系统监控和实时通信功能。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    GameInfo, LaunchRequest, LaunchResult, SystemStatus, 
    ApiResponse, GamePlatform, GameCategory
)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("penpen_launcher")


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 连接已建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket 连接已断开，当前连接数: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接的客户端"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"发送消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)


# 全局变量
websocket_manager = WebSocketManager()
game_scanner = None
process_manager = None
system_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("PenPen Launcher 后端服务启动中...")
    
    # 这里可以初始化游戏扫描器、进程管理器等
    # await initialize_services()
    
    yield
    
    # 关闭时清理
    logger.info("PenPen Launcher 后端服务关闭中...")
    # await cleanup_services()


# 创建 FastAPI 应用
app = FastAPI(
    title="PenPen Launcher API",
    description="PenPen 游戏启动器后端 API 服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 健康检查端点 =====

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return ApiResponse.success({"status": "healthy", "service": "PenPen Launcher"})


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "PenPen Launcher API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ===== 游戏管理端点 =====

@app.get("/api/games", response_model=List[GameInfo])
async def get_games(
    platform: Optional[GamePlatform] = None,
    category: Optional[GameCategory] = None,
    installed_only: bool = True
):
    """
    获取游戏列表
    
    Args:
        platform: 筛选指定平台的游戏
        category: 筛选指定分类的游戏  
        installed_only: 仅显示已安装的游戏
    """
    try:
        # 临时返回模拟数据，稍后替换为真实游戏扫描
        from datetime import datetime
        mock_games = [
            GameInfo(
                id="steam_271590",
                name="Grand Theft Auto V",
                description="洛圣都和布莱恩郡的世界比以往任何时候都更加广阔、丰富和多样",
                developer="Rockstar North",
                publisher="Rockstar Games",
                executable_path="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Grand Theft Auto V\\GTA5.exe",
                platform=GamePlatform.STEAM,
                category=GameCategory.ACTION,
                is_installed=True,
                play_time=1200,
                rating=5,
                tags=["开放世界", "动作", "犯罪"],
                release_date="2015-04-14",
                image_url="https://steamcdn-a.akamaihd.net/steam/apps/271590/header.jpg",
                last_played=datetime.fromisoformat("2023-10-30T15:30:00")
            ),
            GameInfo(
                id="steam_1091500",
                name="Cyberpunk 2077",
                description="在这个开放世界的动作冒险故事中，成为一个拥有高科技增强器的都市雇佣兵",
                developer="CD Projekt RED",
                publisher="CD Projekt",
                executable_path="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Cyberpunk 2077\\bin\\x64\\Cyberpunk2077.exe",
                platform=GamePlatform.STEAM,
                category=GameCategory.RPG,
                is_installed=True,
                play_time=4560,
                rating=4,
                tags=["RPG", "开放世界", "未来科幻"],
                release_date="2020-12-10",
                image_url="https://steamcdn-a.akamaihd.net/steam/apps/1091500/header.jpg",
                last_played=datetime.fromisoformat("2023-11-01T20:15:00")
            )
        ]
        
        # 应用筛选条件
        filtered_games = mock_games
        if platform:
            filtered_games = [game for game in filtered_games if game.platform == platform]
        if category:
            filtered_games = [game for game in filtered_games if game.category == category]
        if installed_only:
            filtered_games = [game for game in filtered_games if game.is_installed]
        
        logger.info(f"返回 {len(filtered_games)} 个游戏，筛选条件: platform={platform}, category={category}")
        return filtered_games
        
    except Exception as e:
        logger.error(f"获取游戏列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取游戏列表失败")

@app.post("/api/games/{game_id}/launch", response_model=LaunchResult)
async def launch_game(game_id: str, request: LaunchRequest):
    """启动指定游戏"""
    try:
        logger.info(f"尝试启动游戏: {game_id}")
        
        # 这里应该调用进程管理器启动游戏
        # 临时返回模拟启动结果
        
        # 模拟启动延迟
        await asyncio.sleep(1)
        
        # 广播游戏状态变化
        await websocket_manager.broadcast({
            "type": "gameStatusChange",
            "data": {
                "game_id": game_id,
                "status": "launching"
            },
            "timestamp": "2025-10-31T10:30:00Z"
        })
        
        return LaunchResult(
            success=True,
            process_id=12345,
            error=None
        )
        
    except Exception as e:
        logger.error(f"启动游戏失败: {e}")
        return LaunchResult(
            success=False,
            process_id=None,
            error=f"启动失败: {str(e)}"
        )


# ===== 系统状态端点 =====

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态信息"""
    try:
        # 这里应该从系统监控器获取真实状态
        # 临时返回模拟数据
        from models import SystemCPU, SystemMemory, SystemStorage, SystemNetwork
        
        return SystemStatus(
            cpu=SystemCPU(usage=45.2, temperature=65.0),
            memory=SystemMemory(used=8.2, total=16.0, percentage=51.25),
            storage=SystemStorage(used=500.0, total=1000.0, percentage=50.0),
            network=SystemNetwork(connected=True, type="wifi", speed=100.0),
            active_game=None
        )
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统状态失败")


@app.post("/api/system/restart")
async def restart_system():
    """重启启动器系统"""
    try:
        logger.info("收到系统重启请求")
        # 这里实现系统重启逻辑
        return ApiResponse.success({"message": "系统重启中..."})
    except Exception as e:
        logger.error(f"系统重启失败: {e}")
        raise HTTPException(status_code=500, detail="系统重启失败")


# ===== WebSocket 端点 =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接端点，用于实时通信"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            logger.debug(f"收到 WebSocket 消息: {data}")
            
            # 这里可以处理客户端发送的消息
            # 例如客户端请求特定的状态更新
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


# ===== 异常处理 =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content=ApiResponse.error("服务器内部错误").dict()
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动 PenPen Launcher API 服务...")
    uvicorn.run(
        "core_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )