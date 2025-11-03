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
from process_manager import ProcessManager


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
    
    # 初始化服务组件
    global process_manager, game_scanner
    from game_scanner import GameScanner
    
    game_scanner = GameScanner()
    logger.info("游戏扫描器已初始化")
    
    process_manager = ProcessManager()
    await process_manager.start_monitoring()
    logger.info("进程管理器已初始化")
    
    yield
    
    # 关闭时清理
    logger.info("PenPen Launcher 后端服务关闭中...")
    if process_manager:
        await process_manager.stop_monitoring()
        logger.info("进程管理器已停止")


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
        # 使用游戏扫描器获取真实游戏数据
        if not game_scanner:
            raise HTTPException(status_code=500, detail="游戏扫描器未初始化")
        
        logger.info("获取游戏列表请求")
        all_games = await game_scanner.scan_all_games(force_refresh=False)
        
        # 应用筛选条件
        filtered_games = all_games
        if platform:
            filtered_games = [game for game in filtered_games if game.platform == platform]
        if category:
            filtered_games = [game for game in filtered_games if game.category == category]
        if installed_only:
            filtered_games = [game for game in filtered_games if game.is_installed]
        
        logger.info(f"返回 {len(filtered_games)} 个游戏，筛选条件: platform={platform}, category={category}, installed_only={installed_only}")
        logger.info(f"找到的游戏: {[game.name for game in filtered_games]}")
        
        return filtered_games
        
    except Exception as e:
        logger.error(f"获取游戏列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取游戏列表失败")

@app.post("/api/games/{game_id}/launch", response_model=LaunchResult)
async def launch_game(game_id: str):
    """启动指定游戏"""
    try:
        logger.info(f"尝试启动游戏: {game_id}")
        
        # 检查进程管理器是否已初始化
        if not process_manager:
            raise HTTPException(status_code=500, detail="进程管理器未初始化")
        
        # 检查游戏扫描器是否已初始化
        if not game_scanner:
            raise HTTPException(status_code=500, detail="游戏扫描器未初始化")
        
        # 获取游戏信息
        games = await game_scanner.scan_all_games()
        game_info = None
        for game in games:
            if game.id == game_id:
                game_info = game
                break
        
        if not game_info:
            raise HTTPException(status_code=404, detail=f"未找到游戏: {game_id}")
        
        # 创建默认的启动请求
        request = LaunchRequest(game_id=game_id, launch_options=None)
        
        # 使用进程管理器启动游戏
        result = await process_manager.launch_game(game_info, request)
        
        # 广播游戏状态变化
        if result.success:
            await websocket_manager.broadcast({
                "type": "gameStatusChange",
                "data": {
                    "game_id": game_id,
                    "status": "launched",
                    "process_id": result.process_id
                },
                "timestamp": "2025-11-03T" + "".join(str(asyncio.get_event_loop().time()).split('.')[0]) + "Z"
            })
        
        return result
        
    except HTTPException:
        raise  # 重新抛出HTTP异常
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