"""
PenPen Launcher 主启动脚本

统一管理所有服务组件：
- 核心 API 服务 (FastAPI)
- 游戏扫描器 (Steam/Epic/自定义)
- 进程管理器 (游戏启动和监控)
- 系统监控器 (资源监控)

支持 CLI 参数控制和优雅关闭机制。
"""

import asyncio
import logging
import signal
import sys
import argparse
from pathlib import Path
import os
from typing import Optional, Dict, Any

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core_api import app
from game_scanner import game_scanner
from process_manager import process_manager
from system_monitor import system_monitor
import uvicorn


# 配置日志
# 确保日志目录存在
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'penpen_launcher.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("penpen_launcher.main")


class LauncherManager:
    """PenPen Launcher 主管理器"""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # 服务器配置
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 8000)
        self.debug = self.config.get("debug", False)
        
        # API 服务器
        self.server = None
        
        logger.info("PenPen Launcher 管理器已初始化")
    
    async def startup(self):
        """启动所有服务"""
        try:
            logger.info("正在启动 PenPen Launcher...")
            
            # 创建必要的目录
            self._ensure_directories()
            
            # 启动系统监控
            logger.info("启动系统监控器...")
            await system_monitor.start_monitoring()
            
            # 启动进程管理器
            logger.info("启动进程管理器...")
            await process_manager.start_monitoring()
            
            # 扫描已安装的游戏
            logger.info("扫描已安装的游戏...")
            await game_scanner.scan_all_games(force_refresh=True)
            
            # 启动 API 服务器
            logger.info(f"启动 API 服务器 (http://{self.host}:{self.port})...")
            server_config = uvicorn.Config(
                app,
                host=self.host,
                port=self.port,
                log_level="info" if not self.debug else "debug",
                access_log=self.debug
            )
            self.server = uvicorn.Server(server_config)
            
            # 在后台启动服务器
            server_task = asyncio.create_task(self.server.serve())
            
            self.is_running = True
            logger.info("PenPen Launcher 启动完成!")
            
            # 等待关闭信号
            await self.shutdown_event.wait()
            
            # 停止服务器
            if self.server:
                self.server.should_exit = True
                await server_task
            
        except Exception as e:
            logger.error(f"启动失败: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """优雅关闭所有服务"""
        if not self.is_running:
            return
        
        logger.info("正在关闭 PenPen Launcher...")
        
        try:
            # 关闭进程管理器（终止所有游戏）
            logger.info("关闭进程管理器...")
            await process_manager.cleanup()
            
            # 关闭系统监控器
            logger.info("关闭系统监控器...")
            await system_monitor.stop_monitoring()
            
            # 设置关闭事件
            self.shutdown_event.set()
            
            self.is_running = False
            logger.info("PenPen Launcher 已安全关闭")
        
        except Exception as e:
            logger.error(f"关闭过程中出错: {e}")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            "logs",
            "screenshots",
            "cache",
            "backups"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目录: {dir_path}")


# 全局启动器管理器实例
launcher_manager = LauncherManager()


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，准备关闭...")
    asyncio.create_task(launcher_manager.shutdown())


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="PenPen Launcher - 电视游戏启动器")
    parser.add_argument("--host", default="localhost", help="API 服务器地址")
    parser.add_argument("--port", type=int, default=8000, help="API 服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--scan-only", action="store_true", help="仅扫描游戏然后退出")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 配置启动器
    config = {
        "host": args.host,
        "port": args.port,
        "debug": args.debug
    }
    
    # 如果指定了配置文件，加载配置
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            # 这里可以添加配置文件加载逻辑
            logger.info(f"加载配置文件: {config_path}")
    
    # 更新启动器配置
    launcher_manager.config.update(config)
    
    # 设置调试日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("调试模式已启用")
    
    # 仅扫描模式
    if args.scan_only:
        logger.info("仅扫描模式：扫描游戏后退出")
        try:
            games = await game_scanner.scan_all_games(force_refresh=True)
            logger.info(f"扫描完成，找到 {len(games)} 个游戏")
            for game in games[:10]:  # 显示前 10 个游戏
                logger.info(f"  - {game.name} ({game.platform})")
            if len(games) > 10:
                logger.info(f"  ... 以及其他 {len(games) - 10} 个游戏")
        except Exception as e:
            logger.error(f"扫描失败: {e}")
            return 1
        return 0
    
    # 注册信号处理器
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 启动启动器
        await launcher_manager.startup()
        return 0
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭...")
        await launcher_manager.shutdown()
        return 0
    except Exception as e:
        logger.error(f"启动器运行错误: {e}")
        return 1


if __name__ == "__main__":
    try:
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 运行主函数
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)