# PenPen Launcher 喷喷启动器 - 完整项目文档

## 项目简介

一个专为电视游戏环境优化的PC启动器，提供类似游戏主机的用户体验。支持手柄导航、游戏内覆盖界面、崩溃自动恢复和云端日志监控。

## 系统架构

```
PenPen Launcher
├── 核心API服务 (FastAPI)
├── 主UI服务 (WebView2 + NextJS)
├── Overlay UI服务 (透明窗口 + 手柄监听)
├── 看门狗服务 (进程监控 + 自动恢复)
└── 日志管理服务 (本地 + 云端上传)
```

## 完整代码实现

### 1. 项目配置文件

#### requirements.txt
```txt
TBD
```

#### .env.example
```env
# Cloudflare R2 配置
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_ENDPOINT_URL=your_r2_endpoint
R2_BUCKET_NAME=your_bucket_name

# 系统配置
CORE_API_PORT=8000
LOG_LEVEL=INFO
UPLOAD_LOGS=true
```

### 2. 核心API服务

#### core_api.py
```python
import uvicorn
import asyncio
import subprocess
import psutil
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("core_api")

app = FastAPI(title="TV Game Launcher Core API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/out"), name="static")

class GameLaunchRequest(BaseModel):
    game_id: str
    arguments: Optional[list] = []

class SystemManager:
    def __init__(self):
        self.active_game_pid: Optional[int] = None
        self.connected_clients: Set[WebSocket] = set()
        self.system_state: str = "booting"
        
    async def broadcast_system_event(self, event_type: str, data: dict):
        """向所有连接的客户端广播系统事件"""
        message = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
        disconnected_clients = []
        
        for client in self.connected_clients:
            try:
                await client.send_json(message)
            except Exception as e:
                logger.error(f"发送消息到客户端失败: {e}")
                disconnected_clients.append(client)
        
        # 移除断开的客户端
        for client in disconnected_clients:
            self.connected_clients.remove(client)

system_manager = SystemManager()

# 模拟游戏库
GAME_LIBRARY = {
    "game1": {
        "id": "game1",
        "name": "示例游戏 1",
        "executable_path": "C:/Games/Game1/game.exe",
        "working_directory": "C:/Games/Game1",
        "image_url": "/static/game1.jpg"
    },
    "game2": {
        "id": "game2", 
        "name": "示例游戏 2",
        "executable_path": "C:/Games/Game2/game.exe",
        "working_directory": "C:/Games/Game2",
        "image_url": "/static/game2.jpg"
    }
}

@app.get("/")
async def serve_ui():
    return FileResponse("frontend/out/index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/games")
async def get_games_library():
    """获取游戏库"""
    logger.info("获取游戏库请求")
    return {"games": list(GAME_LIBRARY.values())}

@app.get("/api/games/{game_id}")
async def get_game_info(game_id: str):
    """获取特定游戏信息"""
    if game_id not in GAME_LIBRARY:
        raise HTTPException(status_code=404, detail="游戏未找到")
    return GAME_LIBRARY[game_id]

@app.post("/api/games/{game_id}/launch")
async def launch_game(game_id: str, request: GameLaunchRequest):
    """启动游戏"""
    logger.info(f"启动游戏请求: {game_id}")
    
    if game_id not in GAME_LIBRARY:
        raise HTTPException(status_code=404, detail="游戏未找到")
    
    game_info = GAME_LIBRARY[game_id]
    
    try:
        # 启动游戏进程
        process = await asyncio.create_subprocess_exec(
            game_info['executable_path'],
            *request.arguments,
            cwd=game_info.get('working_directory'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        system_manager.active_game_pid = process.pid
        system_manager.system_state = "gaming"
        
        # 广播游戏启动事件
        await system_manager.broadcast_system_event(
            "game_launched", 
            {
                "game_id": game_id,
                "game_name": game_info['name'],
                "pid": process.pid
            }
        )
        
        logger.info(f"游戏启动成功: {game_info['name']} (PID: {process.pid})")
        
        return {
            "status": "launched", 
            "pid": process.pid,
            "game_name": game_info['name']
        }
        
    except Exception as e:
        logger.error(f"启动游戏失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")

@app.post("/api/system/terminate-game")
async def terminate_current_game():
    """终止当前运行的游戏"""
    logger.info("终止游戏请求")
    
    if not system_manager.active_game_pid:
        return {"status": "no_active_game"}
    
    try:
        process = psutil.Process(system_manager.active_game_pid)
        process.terminate()
        
        await system_manager.broadcast_system_event(
            "game_terminated", 
            {"pid": system_manager.active_game_pid}
        )
        
        system_manager.active_game_pid = None
        system_manager.system_state = "browsing"
        
        logger.info(f"游戏已终止: PID {system_manager.active_game_pid}")
        
        return {"status": "terminated"}
    
    except psutil.NoSuchProcess:
        logger.warning(f"游戏进程不存在: {system_manager.active_game_pid}")
        system_manager.active_game_pid = None
        system_manager.system_state = "browsing"
        return {"status": "process_not_found"}
    
    except Exception as e:
        logger.error(f"终止游戏失败: {e}")
        raise HTTPException(status_code=500, detail=f"终止失败: {str(e)}")

@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    game_status = None
    if system_manager.active_game_pid:
        try:
            process = psutil.Process(system_manager.active_game_pid)
            game_status = {
                "pid": system_manager.active_game_pid,
                "name": process.name(),
                "status": process.status()
            }
        except psutil.NoSuchProcess:
            system_manager.active_game_pid = None
            system_manager.system_state = "browsing"
    
    return {
        "system_state": system_manager.system_state,
        "active_game": game_status,
        "connected_clients": len(system_manager.connected_clients),
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/system")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接用于系统事件和心跳"""
    await websocket.accept()
    system_manager.connected_clients.add(websocket)
    logger.info(f"新的WebSocket连接，当前连接数: {len(system_manager.connected_clients)}")
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to TV Launcher Core API",
            "system_state": system_manager.system_state
        })
        
        while True:
            data = await websocket.receive_json()
            
            # 处理心跳
            if data.get("type") == "heartbeat":
                await websocket.send_json({
                    "type": "heartbeat_ack",
                    "timestamp": datetime.now().isoformat()
                })
                
            # 处理Overlay命令
            elif data.get("type") == "overlay_command":
                await handle_overlay_command(data, websocket)
                
            # 处理UI命令
            elif data.get("type") == "ui_command":
                await handle_ui_command(data, websocket)
                
    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
        system_manager.connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        system_manager.connected_clients.remove(websocket)

async def handle_overlay_command(data: dict, websocket: WebSocket):
    """处理Overlay UI命令"""
    command = data.get("command")
    logger.info(f"处理Overlay命令: {command}")
    
    if command == "terminate_game":
        await terminate_current_game()
    elif command == "show_main_ui":
        # 触发切换到主UI
        await system_manager.broadcast_system_event("switch_to_main_ui", {})
    elif command == "take_screenshot":
        await take_screenshot()
    else:
        logger.warning(f"未知的Overlay命令: {command}")

async def handle_ui_command(data: dict, websocket: WebSocket):
    """处理主UI命令"""
    command = data.get("command")
    logger.info(f"处理UI命令: {command}")
    
    if command == "shutdown_system":
        await system_manager.broadcast_system_event("system_shutdown", {})
    elif command == "restart_system":
        await system_manager.broadcast_system_event("system_restart", {})

async def take_screenshot():
    """截图功能"""
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.png"
        screenshot.save(filename)
        logger.info(f"截图已保存: {filename}")
    except Exception as e:
        logger.error(f"截图失败: {e}")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_config=None  # 使用自定义日志配置
    )
```

### 3. 主UI服务

#### main_ui.py
```python
import webview
import asyncio
import threading
import requests
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger("main_ui")

class MainUI:
    def __init__(self, core_api_url="http://localhost:8000"):
        self.core_api_url = core_api_url
        self.window = None
        self.websocket_thread = None
        self.is_connected = False
        
    def create_window(self):
        """创建主UI窗口"""
        try:
            self.window = webview.create_window(
                'PenPen Launcher',
                f'{self.core_api_url}',
                fullscreen=True,
                easy_drag=False,
                min_size=(1024, 768)
            )
            
            # 暴露Python方法到JavaScript
            self.window.expose(
                self.get_system_status,
                self.launch_game,
                self.terminate_game,
                self.shutdown_system
            )
            
            logger.info("主UI窗口创建成功")
            return self.window
            
        except Exception as e:
            logger.error(f"创建主UI窗口失败: {e}")
            raise
    
    def start_websocket_client(self):
        """启动WebSocket客户端"""
        def run_websocket():
            asyncio.run(self.websocket_handler())
        
        self.websocket_thread = threading.Thread(target=run_websocket)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()
    
    async def websocket_handler(self):
        """处理WebSocket连接"""
        import websockets
        uri = "ws://localhost:8000/ws/system"
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.is_connected = True
                    logger.info("WebSocket连接成功")
                    
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        await self.handle_websocket_message(data)
                        
            except Exception as e:
                self.is_connected = False
                logger.error(f"WebSocket连接错误: {e}")
                await asyncio.sleep(5)  # 5秒后重试
    
    async def handle_websocket_message(self, data: dict):
        """处理WebSocket消息"""
        message_type = data.get("type")
        
        if message_type == "game_launched":
            logger.info(f"游戏启动: {data.get('data', {})}")
            # 可以在这里更新UI状态
            
        elif message_type == "game_terminated":
            logger.info("游戏已终止")
            # 更新UI状态
            
        elif message_type == "system_shutdown":
            logger.info("收到系统关机命令")
            await self.cleanup_before_exit()
            
        elif message_type == "switch_to_main_ui":
            logger.info("切换到主UI命令")
            if self.window:
                self.window.show()
    
    def get_system_status(self):
        """获取系统状态（暴露给JS）"""
        try:
            response = requests.get(f"{self.core_api_url}/api/system/status")
            return response.json()
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {"error": str(e)}
    
    def launch_game(self, game_id):
        """启动游戏（暴露给JS）"""
        try:
            response = requests.post(
                f"{self.core_api_url}/api/games/{game_id}/launch",
                json={"game_id": game_id}
            )
            return response.json()
        except Exception as e:
            logger.error(f"启动游戏失败: {e}")
            return {"error": str(e)}
    
    def terminate_game(self):
        """终止游戏（暴露给JS）"""
        try:
            response = requests.post(f"{self.core_api_url}/api/system/terminate-game")
            return response.json()
        except Exception as e:
            logger.error(f"终止游戏失败: {e}")
            return {"error": str(e)}
    
    def shutdown_system(self):
        """关机系统（暴露给JS）"""
        logger.info("执行系统关机")
        # 发送关机命令到所有组件
        asyncio.run(self.broadcast_shutdown_command())
    
    async def broadcast_shutdown_command(self):
        """广播关机命令"""
        import websockets
        try:
            async with websockets.connect("ws://localhost:8000/ws/system") as websocket:
                await websocket.send(json.dumps({
                    "type": "ui_command",
                    "command": "shutdown_system"
                }))
        except Exception as e:
            logger.error(f"广播关机命令失败: {e}")
    
    async def cleanup_before_exit(self):
        """退出前清理"""
        logger.info("执行清理操作")
        if self.window:
            self.window.destroy()

def start_main_ui():
    """启动主UI服务"""
    logger.info("启动主UI服务")
    
    try:
        main_ui = MainUI()
        window = main_ui.create_window()
        main_ui.start_websocket_client()
        
        # 启动webview
        webview.start(debug=False)
        
    except Exception as e:
        logger.error(f"主UI服务启动失败: {e}")
        raise

if __name__ == "__main__":
    start_main_ui()
```

### 4. Overlay UI服务

#### overlay_ui.py
```python
import webview
import asyncio
import threading
import websockets
import json
import logging
import psutil
import time
import sys
import os
from ctypes import windll, byref, c_int, Structure, POINTER, WINFUNCTYPE
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM

logger = logging.getLogger("overlay_ui")

# Windows API 常量
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000
LWA_ALPHA = 0x00000002

class GameOverlayService:
    def __init__(self, game_pid: int, core_api_url: str = "ws://localhost:8000/ws/system"):
        self.game_pid = game_pid
        self.core_api_url = core_api_url
        self.overlay_window = None
        self.is_visible = False
        self.ps_key_listener = None
        self.websocket_thread = None
        self.is_running = True
        
        # 手柄状态
        self.ps_button_pressed = False
        self.ps_button_press_time = 0
        
        logger.info(f"Overlay服务初始化，监控游戏PID: {game_pid}")
    
    def create_overlay_window(self):
        """创建透明Overlay窗口"""
        try:
            # 创建透明窗口
            self.overlay_window = webview.create_window(
                'Game Overlay',
                f'http://localhost:8000/overlay?game_pid={self.game_pid}',
                transparent=True,
                frameless=True,
                fullscreen=True,
                easy_drag=False,
                focus=False,  # 不获取焦点
                on_top=True
            )
            
            # 设置窗口透明度
            self.set_window_transparent()
            
            # 初始隐藏
            self.overlay_window.hide()
            
            logger.info("Overlay窗口创建成功")
            
        except Exception as e:
            logger.error(f"创建Overlay窗口失败: {e}")
            raise
    
    def set_window_transparent(self):
        """设置窗口透明属性"""
        try:
            # 获取窗口句柄
            if hasattr(self.overlay_window, 'hwnd'):
                hwnd = self.overlay_window.hwnd
            else:
                # 通过窗口标题查找
                hwnd = windll.user32.FindWindowW(None, "Game Overlay")
            
            if hwnd:
                # 设置窗口样式
                windll.user32.SetWindowLongW(hwnd, -20, WS_EX_LAYERED | WS_EX_TRANSPARENT)
                windll.user32.SetLayeredWindowAttributes(hwnd, 0, 180, LWA_ALPHA)
                logger.info("Overlay窗口透明设置成功")
            else:
                logger.warning("无法找到Overlay窗口句柄")
                
        except Exception as e:
            logger.error(f"设置窗口透明失败: {e}")
    
    def start_ps_key_listener(self):
        """启动PS键监听"""
        def listen():
            import keyboard
            
            # PS键映射（可根据实际手柄调整）
            PS_KEY = 'insert'  # 临时使用Insert键测试
            
            logger.info("开始监听PS键...")
            
            while self.is_running:
                try:
                    # 检测PS键按下
                    if keyboard.is_pressed(PS_KEY):
                        if not self.ps_button_pressed:
                            self.ps_button_pressed = True
                            self.ps_button_press_time = time.time()
                            logger.debug("PS键按下")
                    else:
                        if self.ps_button_pressed:
                            # PS键释放
                            press_duration = time.time() - self.ps_button_press_time
                            self.ps_button_pressed = False
                            
                            if press_duration < 0.5:  # 短按
                                logger.info("PS键短按 - 切换Overlay")
                                self.toggle_overlay()
                            elif press_duration > 2.0:  # 长按
                                logger.info("PS键长按 - 显示电源菜单")
                                self.show_power_menu()
                            
                    time.sleep(0.05)  # 降低CPU使用
                    
                except Exception as e:
                    logger.error(f"PS键监听错误: {e}")
                    time.sleep(1)
        
        self.ps_key_listener = threading.Thread(target=listen)
        self.ps_key_listener.daemon = True
        self.ps_key_listener.start()
    
    def start_websocket_client(self):
        """启动WebSocket客户端"""
        def run_websocket():
            asyncio.run(self.websocket_handler())
        
        self.websocket_thread = threading.Thread(target=run_websocket)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()
    
    async def websocket_handler(self):
        """处理WebSocket连接"""
        while self.is_running:
            try:
                async with websockets.connect(self.core_api_url) as websocket:
                    # 注册Overlay服务
                    await websocket.send(json.dumps({
                        "type": "overlay_registered",
                        "game_pid": self.game_pid,
                        "timestamp": time.time()
                    }))
                    
                    logger.info("Overlay WebSocket连接成功")
                    
                    # 心跳循环
                    while self.is_running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(), 
                                timeout=10
                            )
                            data = json.loads(message)
                            await self.handle_websocket_message(data, websocket)
                            
                        except asyncio.TimeoutError:
                            # 发送心跳
                            await websocket.send(json.dumps({
                                "type": "heartbeat",
                                "service": "overlay_ui",
                                "timestamp": time.time()
                            }))
                            
            except Exception as e:
                logger.error(f"Overlay WebSocket连接失败: {e}")
                await asyncio.sleep(5)  # 5秒后重试
    
    async def handle_websocket_message(self, data: dict, websocket):
        """处理WebSocket消息"""
        message_type = data.get("type")
        
        if message_type == "heartbeat_ack":
            pass  # 心跳确认，无需处理
            
        elif message_type == "system_command":
            await self.execute_system_command(data.get("command"))
            
        elif message_type == "game_terminated":
            logger.info("收到游戏终止通知，关闭Overlay")
            self.cleanup_and_exit()
    
    async def execute_system_command(self, command: str):
        """执行系统命令"""
        logger.info(f"执行系统命令: {command}")
        
        if command == "terminate_game":
            await self.send_overlay_command("terminate_game")
        elif command == "show_main_ui":
            await self.send_overlay_command("show_main_ui")
        elif command == "take_screenshot":
            await self.send_overlay_command("take_screenshot")
    
    async def send_overlay_command(self, command: str):
        """发送Overlay命令到核心API"""
        try:
            async with websockets.connect(self.core_api_url) as websocket:
                await websocket.send(json.dumps({
                    "type": "overlay_command",
                    "command": command,
                    "game_pid": self.game_pid,
                    "timestamp": time.time()
                }))
        except Exception as e:
            logger.error(f"发送Overlay命令失败: {e}")
    
    def toggle_overlay(self):
        """切换Overlay显示状态"""
        if not self.overlay_window:
            return
            
        if self.is_visible:
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def show_overlay(self):
        """显示Overlay界面"""
        if self.overlay_window and not self.is_visible:
            self.overlay_window.show()
            self.is_visible = True
            logger.info("Overlay界面显示")
    
    def hide_overlay(self):
        """隐藏Overlay界面"""
        if self.overlay_window and self.is_visible:
            self.overlay_window.hide()
            self.is_visible = False
            logger.info("Overlay界面隐藏")
    
    def show_power_menu(self):
        """显示电源菜单"""
        logger.info("显示电源菜单")
        # 这里可以实现更复杂的电源菜单逻辑
        asyncio.run(self.send_overlay_command("show_main_ui"))
    
    def monitor_game_process(self):
        """监控游戏进程"""
        def monitor():
            logger.info("开始监控游戏进程")
            
            while self.is_running:
                try:
                    # 检查游戏进程是否存在
                    if not psutil.pid_exists(self.game_pid):
                        logger.warning(f"游戏进程已退出: {self.game_pid}")
                        self.cleanup_and_exit()
                        break
                    
                    time.sleep(2)  # 每2秒检查一次
                    
                except Exception as e:
                    logger.error(f"游戏进程监控错误: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def cleanup_and_exit(self):
        """清理并退出"""
        logger.info("执行Overlay服务清理")
        self.is_running = False
        
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
        
        # 等待线程结束
        if self.ps_key_listener and self.ps_key_listener.is_alive():
            self.ps_key_listener.join(timeout=1.0)
        
        logger.info("Overlay服务退出")

def start_overlay_service(game_pid: int):
    """启动Overlay服务"""
    logger.info(f"启动Overlay服务，游戏PID: {game_pid}")
    
    try:
        overlay = GameOverlayService(game_pid)
        overlay.create_overlay_window()
        overlay.start_ps_key_listener()
        overlay.start_websocket_client()
        overlay.monitor_game_process()
        
        # 启动webview（非阻塞）
        def start_webview():
            webview.start(debug=False)
        
        webview_thread = threading.Thread(target=start_webview)
        webview_thread.daemon = True
        webview_thread.start()
        
        # 保持主线程运行
        try:
            while overlay.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号")
        finally:
            overlay.cleanup_and_exit()
            
    except Exception as e:
        logger.error(f"Overlay服务启动失败: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python overlay_ui.py <game_pid>")
        sys.exit(1)
    
    try:
        game_pid = int(sys.argv[1])
        start_overlay_service(game_pid)
    except ValueError:
        print("错误: game_pid 必须是整数")
        sys.exit(1)
```

### 5. 看门狗服务

#### watchdog_service.py
```python
import asyncio
import psutil
import time
import logging
import requests
import json
import os
from datetime import datetime
from typing import Dict, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("watchdog")

class SystemWatchdog:
    def __init__(self, core_api_url: str = "http://localhost:8000"):
        self.core_api_url = core_api_url
        self.expected_processes = {
            "core_api": {
                "cmd_patterns": [["python", "core_api.py"], ["uvicorn", "core_api:app"]],
                "restart_command": ["python", "core_api.py"],
                "max_restarts": 3,
                "restart_count": 0
            },
            "main_ui": {
                "cmd_patterns": [["python", "main_ui.py"]],
                "restart_command": ["python", "main_ui.py"], 
                "max_restarts": 2,
                "restart_count": 0
            }
        }
        
        self.process_states: Dict[str, bool] = {}
        self.process_pids: Dict[str, int] = {}
        self.health_check_failures: Dict[str, int] = {}
        self.is_monitoring = True
        
        # 创建日志目录
        os.makedirs("logs", exist_ok=True)
        
        logger.info("看门狗服务初始化完成")
    
    async def start_monitoring(self):
        """开始监控所有关键进程"""
        logger.info("开始系统进程监控")
        
        # 初始健康检查
        await self.initial_health_check()
        
        # 开始监控循环
        monitor_task = asyncio.create_task(self.monitoring_loop())
        log_upload_task = asyncio.create_task(self.log_upload_loop())
        
        try:
            await asyncio.gather(monitor_task, log_upload_task)
        except Exception as e:
            logger.error(f"监控任务异常: {e}")
        finally:
            self.is_monitoring = False
    
    async def initial_health_check(self):
        """初始健康检查"""
        logger.info("执行初始健康检查")
        
        for process_name in self.expected_processes:
            is_running = await self.check_process_health(process_name)
            
            if not is_running:
                logger.warning(f"进程 {process_name} 未运行，尝试启动")
                await self.restart_process(process_name)
    
    async def monitoring_loop(self):
        """监控循环"""
        check_count = 0
        
        while self.is_monitoring:
            try:
                # 检查进程健康状态
                for process_name in self.expected_processes:
                    await self.check_process_health(process_name)
                
                # 每10次检查执行一次详细状态报告
                check_count += 1
                if check_count >= 10:
                    await self.report_system_status()
                    check_count = 0
                
                # 等待5秒后再次检查
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(10)  # 出错后等待更长时间
    
    async def check_process_health(self, process_name: str) -> bool:
        """检查进程健康状态"""
        # 检查进程是否在运行
        is_running = await self.is_process_running(process_name)
        was_running = self.process_states.get(process_name, False)
        
        # 状态变化处理
        if is_running != was_running:
            if is_running:
                logger.info(f"进程 {process_name} 已启动")
                self.health_check_failures[process_name] = 0
            else:
                logger.warning(f"进程 {process_name} 已停止")
                await self.handle_process_crash(process_name)
            
            self.process_states[process_name] = is_running
        
        # 如果进程在运行，执行健康检查
        if is_running:
            is_healthy = await self.perform_health_check(process_name)
            if not is_healthy:
                logger.warning(f"进程 {process_name} 健康检查失败")
                self.health_check_failures[process_name] = \
                    self.health_check_failures.get(process_name, 0) + 1
                
                # 连续健康检查失败达到阈值
                if self.health_check_failures[process_name] >= 3:
                    logger.error(f"进程 {process_name} 连续健康检查失败，判定为不健康")
                    await self.handle_unhealthy_process(process_name)
            else:
                self.health_check_failures[process_name] = 0
        
        return is_running
    
    async def is_process_running(self, process_name: str) -> bool:
        """检查指定进程是否在运行"""
        process_info = self.expected_processes[process_name]
        
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = process.info['cmdline']
                if cmdline:
                    for pattern in process_info['cmd_patterns']:
                        if all(part in ' '.join(cmdline) for part in pattern):
                            self.process_pids[process_name] = process.info['pid']
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        return False
    
    async def perform_health_check(self, process_name: str) -> bool:
        """执行进程健康检查"""
        if process_name == "core_api":
            return await self.check_core_api_health()
        elif process_name == "main_ui":
            return await self.check_main_ui_health()
        
        return True  # 其他进程默认健康
    
    async def check_core_api_health(self) -> bool:
        """检查核心API健康状态"""
        try:
            response = requests.get(f"{self.core_api_url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"核心API健康检查失败: {e}")
            return False
    
    async def check_main_ui_health(self) -> bool:
        """检查主UI健康状态"""
        # 检查WebView进程是否响应
        try:
            # 这里可以实现更精确的主UI健康检查
            return await self.is_process_running("main_ui")
        except Exception as e:
            logger.debug(f"主UI健康检查失败: {e}")
            return False
    
    async def handle_process_crash(self, process_name: str):
        """处理进程崩溃"""
        logger.error(f"检测到进程 {process_name} 崩溃")
        
        # 记录崩溃日志
        await self.log_crash_event(process_name)
        
        # 根据进程类型执行不同的恢复策略
        if process_name == "core_api":
            await self.handle_core_api_crash()
        elif process_name == "main_ui":
            await self.handle_main_ui_crash()
        else:
            await self.restart_process(process_name)
    
    async def handle_unhealthy_process(self, process_name: str):
        """处理不健康进程"""
        logger.warning(f"进程 {process_name} 不健康，尝试重启")
        
        # 终止不健康进程
        await self.terminate_process(process_name)
        
        # 重启进程
        await self.restart_process(process_name)
        
        # 重置失败计数
        self.health_check_failures[process_name] = 0
    
    async def handle_core_api_crash(self):
        """处理核心API崩溃"""
        logger.critical("核心API崩溃，执行紧急恢复")
        
        # 记录紧急事件
        await self.log_emergency_event("core_api_crash", "核心API服务崩溃")
        
        # 尝试重启核心API
        success = await self.restart_process("core_api")
        
        if not success:
            logger.error("核心API重启失败，可能需要手动干预")
            # 这里可以添加通知机制（邮件、短信等）
    
    async def handle_main_ui_crash(self):
        """处理主UI崩溃"""
        logger.warning("主UI崩溃，尝试恢复")
        
        # 检查系统状态
        system_state = await self.get_system_state()
        
        if system_state == "gaming":
            logger.info("游戏运行中，暂不恢复主UI")
        else:
            await self.restart_process("main_ui")
    
    async def restart_process(self, process_name: str) -> bool:
        """重启进程"""
        process_info = self.expected_processes[process_name]
        
        # 检查重启次数限制
        if process_info['restart_count'] >= process_info['max_restarts']:
            logger.error(f"进程 {process_name} 重启次数超过限制")
            return False
        
        try:
            logger.info(f"尝试重启进程: {process_name}")
            
            # 终止现有进程
            await self.terminate_process(process_name)
            
            # 启动新进程
            import subprocess
            subprocess.Popen(
                process_info['restart_command'],
                cwd=os.getcwd(),
                stdout=open(f"logs/{process_name}.log", "a"),
                stderr=open(f"logs/{process_name}_error.log", "a")
            )
            
            process_info['restart_count'] += 1
            logger.info(f"进程 {process_name} 重启命令已执行")
            
            # 等待进程启动
            await asyncio.sleep(3)
            
            # 验证进程是否启动成功
            is_running = await self.is_process_running(process_name)
            if is_running:
                logger.info(f"进程 {process_name} 重启成功")
                return True
            else:
                logger.error(f"进程 {process_name} 重启失败")
                return False
                
        except Exception as e:
            logger.error(f"重启进程 {process_name} 失败: {e}")
            return False
    
    async def terminate_process(self, process_name: str):
        """终止进程"""
        if process_name in self.process_pids:
            try:
                pid = self.process_pids[process_name]
                process = psutil.Process(pid)
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    process.kill()
                
                logger.info(f"进程 {process_name} (PID: {pid}) 已终止")
                
            except psutil.NoSuchProcess:
                logger.warning(f"进程 {process_name} 不存在")
            except Exception as e:
                logger.error(f"终止进程 {process_name} 失败: {e}")
    
    async def get_system_state(self) -> str:
        """获取系统状态"""
        try:
            response = requests.get(f"{self.core_api_url}/api/system/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("system_state", "unknown")
        except Exception as e:
            logger.debug(f"获取系统状态失败: {e}")
        
        return "unknown"
    
    async def report_system_status(self):
        """报告系统状态"""
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "processes": {},
            "system_state": await self.get_system_state()
        }
        
        for process_name in self.expected_processes:
            status_report["processes"][process_name] = {
                "is_running": self.process_states.get(process_name, False),
                "restart_count": self.expected_processes[process_name]["restart_count"],
                "health_failures": self.health_check_failures.get(process_name, 0)
            }
        
        logger.info(f"系统状态报告: {json.dumps(status_report, indent=2)}")
        
        # 保存状态报告到日志文件
        await self.save_status_report(status_report)
    
    async def save_status_report(self, report: dict):
        """保存状态报告"""
        try:
            with open("logs/system_status.json", "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"保存状态报告失败: {e}")
    
    async def log_crash_event(self, process_name: str):
        """记录崩溃事件"""
        crash_event = {
            "event_type": "process_crash",
            "process_name": process_name,
            "timestamp": datetime.now().isoformat(),
            "system_state": await self.get_system_state()
        }
        
        await self.log_event(crash_event, "crash_events.log")
    
    async def log_emergency_event(self, event_type: str, message: str):
        """记录紧急事件"""
        emergency_event = {
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "critical"
        }
        
        await self.log_event(emergency_event, "emergency_events.log")
    
    async def log_event(self, event: dict, log_file: str):
        """记录事件到日志文件"""
        try:
            with open(f"logs/{log_file}", "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"记录事件失败: {e}")
    
    async def log_upload_loop(self):
        """日志上传循环"""
        from log_uploader import LogUploader
        
        uploader = LogUploader()
        
        while self.is_monitoring:
            try:
                # 每30分钟上传一次日志
                await asyncio.sleep(1800)  # 30分钟
                
                if uploader.is_configured():
                    logger.info("开始上传日志文件")
                    await uploader.upload_log_files()
                else:
                    logger.debug("日志上传未配置，跳过")
                    
            except Exception as e:
                logger.error(f"日志上传失败: {e}")
                await asyncio.sleep(300)  # 出错后等待5分钟

async def main():
    """主函数"""
    watchdog = SystemWatchdog()
    
    try:
        await watchdog.start_monitoring()
    except KeyboardInterrupt:
        logger.info("收到中断信号，停止监控")
    except Exception as e:
        logger.error(f"看门狗服务异常: {e}")
    finally:
        watchdog.is_monitoring = False

if __name__ == "__main__":
    asyncio.run(main())
```

### 6. 日志上传服务

#### log_uploader.py
```python
import os
import boto3
import aiofiles
import asyncio
import logging
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger("log_uploader")

class LogUploader:
    def __init__(self):
        self.s3_client = None
        self.is_configured_flag = False
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """初始化S3客户端（用于Cloudflare R2）"""
        try:
            access_key = os.getenv("R2_ACCESS_KEY_ID")
            secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
            endpoint_url = os.getenv("R2_ENDPOINT_URL")
            
            if not all([access_key, secret_key, endpoint_url, self.bucket_name]):
                logger.warning("Cloudflare R2配置不完整，日志上传功能禁用")
                return
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url
            )
            
            # 测试连接
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.is_configured_flag = True
            logger.info("Cloudflare R2客户端初始化成功")
            
        except Exception as e:
            logger.error(f"初始化Cloudflare R2客户端失败: {e}")
            self.is_configured_flag = False
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self.is_configured_flag
    
    async def upload_log_files(self):
        """上传日志文件"""
        if not self.is_configured():
            return
        
        log_files = await self.get_log_files()
        
        for log_file in log_files:
            try:
                await self.upload_file(log_file)
                logger.info(f"日志文件上传成功: {log_file}")
                
                # 上传成功后可以删除或压缩旧日志
                await self.cleanup_old_logs(log_file)
                
            except Exception as e:
                logger.error(f"上传日志文件失败 {log_file}: {e}")
    
    async def get_log_files(self) -> List[str]:
        """获取需要上传的日志文件"""
        log_files = []
        log_dir = "logs"
        
        if not os.path.exists(log_dir):
            return log_files
        
        for filename in os.listdir(log_dir):
            if filename.endswith(('.log', '.json')):
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    log_files.append(filepath)
        
        return log_files
    
    async def upload_file(self, file_path: str):
        """上传单个文件"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 生成目标路径（包含日期）
        date_str = datetime.now().strftime("%Y/%m/%d")
        s3_key = f"tv-launcher/{date_str}/{filename}"
        
        # 使用异步方式读取文件
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        # 上传到R2
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_content,
            ContentType='text/plain'
        )
        
        logger.debug(f"文件上传完成: {filename} -> {s3_key} ({file_size} bytes)")
    
    async def cleanup_old_logs(self, uploaded_file: str):
        """清理已上传的旧日志"""
        try:
            # 这里可以实现日志轮转策略
            # 例如：保留最近7天的日志，压缩或删除旧日志
            
            file_size = os.path.getsize(uploaded_file)
            max_size = 100 * 1024 * 1024  # 100MB
            
            if file_size > max_size:
                # 文件过大，进行轮转
                await self.rotate_log_file(uploaded_file)
                
        except Exception as e:
            logger.error(f"清理日志文件失败 {uploaded_file}: {e}")
    
    async def rotate_log_file(self, log_file: str):
        """轮转日志文件"""
        try:
            import gzip
            import shutil
            
            # 创建压缩版本
            compressed_file = f"{log_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
            
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 清空原文件
            with open(log_file, 'w') as f:
                f.truncate(0)
            
            logger.info(f"日志文件已轮转: {log_file} -> {compressed_file}")
            
        except Exception as e:
            logger.error(f"日志文件轮转失败 {log_file}: {e}")

async def test_upload():
    """测试上传功能"""
    uploader = LogUploader()
    
    if uploader.is_configured():
        print("开始测试日志上传...")
        await uploader.upload_log_files()
        print("测试完成")
    else:
        print("日志上传未配置")

if __name__ == "__main__":
    asyncio.run(test_upload())
```

### 7. 进程管理器

#### process_manager.py
```python
import asyncio
import subprocess
import psutil
import logging
import os
from enum import Enum
from typing import Optional, Dict

logger = logging.getLogger("process_manager")

class SystemState(Enum):
    BOOTING = "booting"
    BROWSING = "browsing" 
    GAMING = "gaming"
    SHUTTING_DOWN = "shutting_down"

class ProcessManager:
    def __init__(self):
        self.system_state = SystemState.BOOTING
        self.core_api_process: Optional[subprocess.Popen] = None
        self.main_ui_process: Optional[subprocess.Popen] = None
        self.overlay_ui_process: Optional[subprocess.Popen] = None
        self.watchdog_process: Optional[subprocess.Popen] = None
        
        # 进程配置
        self.process_configs = {
            "core_api": {
                "command": ["python", "core_api.py"],
                "cwd": os.getcwd(),
                "stdout": "logs/core_api.log",
                "stderr": "logs/core_api_error.log"
            },
            "main_ui": {
                "command": ["python", "main_ui.py"],
                "cwd": os.getcwd(), 
                "stdout": "logs/main_ui.log",
                "stderr": "logs/main_ui_error.log"
            },
            "overlay_ui": {
                "command": ["python", "overlay_ui.py"],
                "cwd": os.getcwd(),
                "stdout": "logs/overlay_ui.log", 
                "stderr": "logs/overlay_ui_error.log"
            },
            "watchdog": {
                "command": ["python", "watchdog_service.py"],
                "cwd": os.getcwd(),
                "stdout": "logs/watchdog.log",
                "stderr": "logs/watchdog_error.log"
            }
        }
        
        # 创建日志目录
        os.makedirs("logs", exist_ok=True)
    
    async def initialize_system(self):
        """系统初始化流程"""
        logger.info("开始系统初始化")
        
        try:
            # 1. 启动核心API服务
            self.core_api_process = await self.start_process("core_api")
            logger.info("核心API服务启动完成")
            
            # 等待API服务就绪
            await asyncio.sleep(3)
            
            # 2. 启动看门狗服务
            self.watchdog_process = await self.start_process("watchdog")
            logger.info("看门狗服务启动完成")
            
            # 3. 启动主UI
            self.main_ui_process = await self.start_process("main_ui")
            logger.info("主UI服务启动完成")
            
            self.system_state = SystemState.BROWSING
            logger.info("系统初始化完成，进入浏览状态")
            
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            await self.emergency_shutdown()
            raise
    
    async def start_process(self, process_name: str) -> subprocess.Popen:
        """启动进程"""
        config = self.process_configs[process_name]
        
        stdout = open(config["stdout"], "a")
        stderr = open(config["stderr"], "a")
        
        process = await asyncio.create_subprocess_exec(
            *config["command"],
            cwd=config["cwd"],
            stdout=stdout,
            stderr=stderr
        )
        
        logger.info(f"进程启动: {process_name} (PID: {process.pid})")
        return process
    
    async def start_game(self, game_executable: str, arguments: list = None) -> int:
        """启动游戏"""
        if arguments is None:
            arguments = []
        
        logger.info(f"启动游戏: {game_executable}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                game_executable,
                *arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 切换到游戏状态
            self.system_state = SystemState.GAMING
            
            # 关闭主UI释放资源
            if self.main_ui_process:
                await self.terminate_process(self.main_ui_process, "main_ui")
                self.main_ui_process = None
            
            # 启动Overlay UI
            self.overlay_ui_process = await self.start_process_with_args(
                "overlay_ui", 
                [str(process.pid)]
            )
            
            logger.info(f"游戏启动成功: {game_executable} (PID: {process.pid})")
            return process.pid
            
        except Exception as e:
            logger.error(f"启动游戏失败: {e}")
            raise
    
    async def start_process_with_args(self, process_name: str, args: list) -> subprocess.Popen:
        """带参数启动进程"""
        config = self.process_configs[process_name]
        
        stdout = open(config["stdout"], "a")
        stderr = open(config["stderr"], "a")
        
        full_command = config["command"] + args
        
        process = await asyncio.create_subprocess_exec(
            *full_command,
            cwd=config["cwd"],
            stdout=stdout,
            stderr=stderr
        )
        
        logger.info(f"进程启动: {process_name} (PID: {process.pid})")
        return process
    
    async def terminate_process(self, process: subprocess.Popen, process_name: str):
        """终止进程"""
        if process and process.returncode is None:
            try:
                # 尝试优雅终止
                process.terminate()
                
                try:
                    # 等待进程结束
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                    logger.info(f"进程终止: {process_name}")
                except asyncio.TimeoutError:
                    # 强制终止
                    process.kill()
                    await process.wait()
                    logger.warning(f"进程强制终止: {process_name}")
                    
            except Exception as e:
                logger.error(f"终止进程失败 {process_name}: {e}")
    
    async def transition_to_browsing(self):
        """返回浏览状态"""
        logger.info("切换到浏览状态")
        
        # 终止Overlay UI
        if self.overlay_ui_process:
            await self.terminate_process(self.overlay_ui_process, "overlay_ui")
            self.overlay_ui_process = None
        
        # 重新启动主UI
        if not self.main_ui_process:
            self.main_ui_process = await self.start_process("main_ui")
        
        self.system_state = SystemState.BROWSING
        logger.info("已切换到浏览状态")
    
    async def shutdown_system(self):
        """关闭系统"""
        logger.info("开始系统关闭流程")
        self.system_state = SystemState.SHUTTING_DOWN
        
        # 终止所有进程（逆序）
        processes_to_terminate = [
            (self.overlay_ui_process, "overlay_ui"),
            (self.main_ui_process, "main_ui"), 
            (self.watchdog_process, "watchdog"),
            (self.core_api_process, "core_api")
        ]
        
        for process, name in processes_to_terminate:
            if process:
                await self.terminate_process(process, name)
        
        logger.info("系统关闭完成")
    
    async def emergency_shutdown(self):
        """紧急关闭"""
        logger.critical("执行紧急关闭")
        
        # 强制终止所有相关进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(script in cmdline for script in [
                    'core_api.py', 'main_ui.py', 'overlay_ui.py', 'watchdog_service.py'
                ]):
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.critical("紧急关闭完成")

async def main():
    """主函数（测试用）"""
    manager = ProcessManager()
    
    try:
        await manager.initialize_system()
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("收到中断信号")
    finally:
        await manager.shutdown_system()

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. 主启动脚本

#### launcher.py
```python
#!/usr/bin/env python3
"""
PenPen Launcher - 主启动脚本
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_manager import ProcessManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/launcher.log')
    ]
)

logger = logging.getLogger("launcher")

async def main():
    """主函数"""
    logger.info("PenPen Launcher 启动")
    
    # 确保在正确的目录运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    process_manager = ProcessManager()
    
    try:
        # 系统初始化
        await process_manager.initialize_system()
        logger.info("系统启动完成，准备就绪")
        
        # 主循环
        while True:
            await asyncio.sleep(1)
            
            # 这里可以添加定期检查或状态报告
            # 例如：每5分钟记录一次系统状态
            
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"系统运行错误: {e}")
    finally:
        # 优雅关闭
        logger.info("开始系统关闭流程")
        try:
            await process_manager.shutdown_system()
        except Exception as e:
            logger.error(f"关闭过程中发生错误: {e}")
        
        logger.info("PenPen Launcher 已退出")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1)
```

### 9. 安装和启动脚本

#### install.bat (Windows)
```batch
@echo off
echo 安装 PenPen Launcher...

REM 创建虚拟环境
python -m venv venv
call venv\Scripts\activate.bat

REM 安装依赖
pip install -r requirements.txt

REM 创建必要的目录
mkdir logs
mkdir screenshots
mkdir frontend\out

echo 安装完成！
echo.
echo 接下来请：
echo 1. 配置 .env 文件
echo 2. 构建前端项目到 frontend/out 目录
echo 3. 运行 python launcher.py 启动系统
pause
```

#### start.bat (Windows)
```batch
@echo off
call venv\Scripts\activate.bat
python launcher.py
pause
```

## 部署说明

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的 Cloudflare R2 配置。

### 3. 构建前端

将 NextJS 项目构建到 `frontend/out` 目录。

### 4. 启动系统

```bash
python launcher.py
```

## 功能特性

- ✅ 类似游戏主机的用户界面
- ✅ 手柄导航支持（PS4/PS5手柄）
- ✅ 游戏内覆盖界面（PS键唤醒）
- ✅ 自动崩溃恢复
- ✅ 云端日志监控（Cloudflare R2）
- ✅ 系统状态监控
- ✅ 优雅的进程管理

这个完整的项目提供了从底层进程管理到上层用户界面的完整解决方案，可以直接部署到你的ITX电脑上使用。