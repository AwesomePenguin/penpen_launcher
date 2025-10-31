"""
PenPen Launcher 进程管理器

负责安全地启动、监控和管理游戏进程。
支持不同平台的游戏启动机制和进程生命周期管理。
"""

import asyncio
import logging
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Optional, List
import psutil

from models import GameInfo, LaunchRequest, LaunchResult, GamePlatform


logger = logging.getLogger("penpen_launcher.process_manager")


class GameProcess:
    """游戏进程信息"""
    
    def __init__(self, game_info: GameInfo, process: subprocess.Popen):
        self.game_info = game_info
        self.process = process
        self.start_time = time.time()
        self.last_check = time.time()
    
    @property
    def is_running(self) -> bool:
        """检查进程是否仍在运行"""
        return self.process.poll() is None
    
    @property
    def pid(self) -> Optional[int]:
        """获取进程 ID"""
        return self.process.pid
    
    @property
    def runtime_seconds(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time
    
    def terminate(self) -> bool:
        """终止游戏进程"""
        try:
            if self.is_running:
                self.process.terminate()
                # 等待进程优雅退出
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 强制杀死进程
                    self.process.kill()
                    self.process.wait()
                
                logger.info(f"游戏进程已终止: {self.game_info.name} (PID: {self.pid})")
                return True
            return False
        except Exception as e:
            logger.error(f"终止进程失败: {e}")
            return False


class SteamLauncher:
    """Steam 游戏启动器"""
    
    @staticmethod
    def extract_app_id(game_id: str) -> Optional[str]:
        """从游戏 ID 提取 Steam App ID"""
        if game_id.startswith("steam_"):
            return game_id[6:]  # 移除 "steam_" 前缀
        return None
    
    @staticmethod
    async def launch_steam_game(game_info: GameInfo) -> subprocess.Popen:
        """启动 Steam 游戏"""
        app_id = SteamLauncher.extract_app_id(game_info.id)
        if not app_id:
            raise ValueError(f"无效的 Steam 游戏 ID: {game_info.id}")
        
        # 使用 Steam 协议启动游戏
        steam_url = f"steam://rungameid/{app_id}"
        
        logger.info(f"通过 Steam 启动游戏: {game_info.name} (App ID: {app_id})")
        
        # 在 Windows 上启动 Steam URL
        process = subprocess.Popen(
            ["cmd", "/c", "start", steam_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 等待一下确保启动命令被执行
        await asyncio.sleep(2)
        
        return process


class EpicLauncher:
    """Epic Games 游戏启动器"""
    
    @staticmethod
    async def launch_epic_game(game_info: GameInfo) -> subprocess.Popen:
        """启动 Epic Games 游戏"""
        # Epic Games 启动 URL 格式
        epic_url = f"com.epicgames.launcher://apps/{game_info.id}?action=launch"
        
        logger.info(f"通过 Epic Games 启动游戏: {game_info.name}")
        
        process = subprocess.Popen(
            ["cmd", "/c", "start", epic_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        await asyncio.sleep(2)
        return process


class CustomLauncher:
    """自定义游戏启动器"""
    
    @staticmethod
    async def launch_custom_game(game_info: GameInfo, launch_request: LaunchRequest) -> subprocess.Popen:
        """启动自定义游戏"""
        executable_path = Path(game_info.executable_path)
        
        if not executable_path.exists():
            raise FileNotFoundError(f"游戏可执行文件不存在: {executable_path}")
        
        # 构建启动命令
        cmd = [str(executable_path)]
        
        # 添加额外的启动参数
        if launch_request.launch_options and launch_request.launch_options.additional_args:
            cmd.extend(launch_request.launch_options.additional_args)
        
        # 设置工作目录为游戏目录
        working_dir = executable_path.parent
        
        logger.info(f"启动自定义游戏: {game_info.name}")
        logger.debug(f"启动命令: {' '.join(cmd)}")
        logger.debug(f"工作目录: {working_dir}")
        
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return process


class ProcessManager:
    """游戏进程管理器"""
    
    def __init__(self):
        self.active_processes: Dict[str, GameProcess] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def start_monitoring(self):
        """开始进程监控任务"""
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitor_processes())
            logger.info("进程监控已启动")
    
    async def stop_monitoring(self):
        """停止进程监控"""
        self._shutdown_event.set()
        if self.monitoring_task:
            await self.monitoring_task
        logger.info("进程监控已停止")
    
    async def launch_game(self, game_info: GameInfo, launch_request: LaunchRequest) -> LaunchResult:
        """启动游戏"""
        try:
            # 检查游戏是否已经在运行
            if game_info.id in self.active_processes:
                existing_process = self.active_processes[game_info.id]
                if existing_process.is_running:
                    return LaunchResult(
                        success=False,
                        error=f"游戏 {game_info.name} 已在运行中",
                        process_id=existing_process.pid
                    )
                else:
                    # 清理已结束的进程
                    del self.active_processes[game_info.id]
            
            if not game_info.is_installed:
                return LaunchResult(
                    success=False,
                    error=f"游戏 {game_info.name} 未安装",
                    process_id=None
                )
            
            # 根据平台选择启动器
            process = await self._launch_by_platform(game_info, launch_request)
            
            # 创建游戏进程对象
            game_process = GameProcess(game_info, process)
            self.active_processes[game_info.id] = game_process
            
            logger.info(f"游戏启动成功: {game_info.name} (PID: {process.pid})")
            
            return LaunchResult(
                success=True,
                process_id=process.pid,
                error=None
            )
        except Exception as e:
            logger.error(f"启动游戏失败: {game_info.name}, 错误: {e}")
            return LaunchResult(
                success=False,
                error=str(e),
                process_id=None
            )
    
    async def _launch_by_platform(self, game_info: GameInfo, launch_request: LaunchRequest) -> subprocess.Popen:
        """根据平台启动游戏"""
        if game_info.platform == GamePlatform.STEAM:
            return await SteamLauncher.launch_steam_game(game_info)
        elif game_info.platform == GamePlatform.EPIC:
            return await EpicLauncher.launch_epic_game(game_info)
        elif game_info.platform == GamePlatform.CUSTOM:
            return await CustomLauncher.launch_custom_game(game_info, launch_request)
        else:
            # 对于其他平台，尝试直接启动可执行文件
            return await CustomLauncher.launch_custom_game(game_info, launch_request)
    
    async def terminate_game(self, game_id: str) -> bool:
        """终止指定游戏"""
        if game_id not in self.active_processes:
            logger.warning(f"未找到运行中的游戏: {game_id}")
            return False
        
        game_process = self.active_processes[game_id]
        success = game_process.terminate()
        
        if success:
            del self.active_processes[game_id]
        
        return success
    
    async def terminate_all_games(self) -> int:
        """终止所有运行中的游戏"""
        terminated_count = 0
        
        for game_id in list(self.active_processes.keys()):
            if await self.terminate_game(game_id):
                terminated_count += 1
        
        logger.info(f"已终止 {terminated_count} 个游戏进程")
        return terminated_count
    
    def get_active_games(self) -> List[Dict]:
        """获取当前运行的游戏列表"""
        active_games = []
        
        for game_id, game_process in self.active_processes.items():
            if game_process.is_running:
                active_games.append({
                    "game_id": game_id,
                    "name": game_process.game_info.name,
                    "pid": game_process.pid,
                    "runtime_seconds": game_process.runtime_seconds,
                    "platform": game_process.game_info.platform
                })
        
        return active_games
    
    def get_system_resource_usage(self) -> Dict:
        """获取系统资源使用情况"""
        try:
            # 获取 CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 获取内存使用情况
            memory = psutil.virtual_memory()
            
            # 获取磁盘使用情况
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage": cpu_percent,
                    "temperature": None  # 需要额外的库来获取温度
                },
                "memory": {
                    "used": round(memory.used / 1024**3, 2),  # GB
                    "total": round(memory.total / 1024**3, 2),  # GB
                    "percentage": memory.percent
                },
                "storage": {
                    "used": round(disk.used / 1024**3, 2),  # GB
                    "total": round(disk.total / 1024**3, 2),  # GB
                    "percentage": round((disk.used / disk.total) * 100, 2)
                }
            }
        except Exception as e:
            logger.error(f"获取系统资源信息失败: {e}")
            return {}
    
    async def _monitor_processes(self):
        """监控游戏进程状态"""
        logger.info("开始监控游戏进程...")
        
        while not self._shutdown_event.is_set():
            try:
                # 检查所有活跃进程
                dead_processes = []
                
                for game_id, game_process in self.active_processes.items():
                    if not game_process.is_running:
                        # 进程已结束
                        runtime = game_process.runtime_seconds
                        logger.info(f"游戏进程已结束: {game_process.game_info.name}, 运行时长: {runtime:.1f}秒")
                        dead_processes.append(game_id)
                
                # 清理已结束的进程
                for game_id in dead_processes:
                    del self.active_processes[game_id]
                
                # 每 5 秒检查一次
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"进程监控错误: {e}")
                await asyncio.sleep(5)
        
        logger.info("进程监控已停止")
    
    async def cleanup(self):
        """清理资源"""
        await self.stop_monitoring()
        await self.terminate_all_games()


# 全局进程管理器实例
process_manager = ProcessManager()