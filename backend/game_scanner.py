"""
PenPen Launcher 游戏扫描器

负责发现和扫描已安装的游戏，支持多个游戏平台：
- Steam: 通过注册表和 VDF 文件扫描
- Epic Games: 扫描 Epic Games Launcher 数据
- Battle.net: 检测暴雪游戏安装
- 自定义游戏: 用户手动添加的游戏
"""

import os
import json
import logging
import winreg
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

# 注意: 以下导入在安装依赖后才能正常工作
try:
    import vdf
except ImportError:
    vdf = None

from models import GameInfo, GamePlatform, GameCategory


logger = logging.getLogger("penpen_launcher.scanner")


class SteamScanner:
    """Steam 游戏扫描器"""
    
    def __init__(self):
        self.steam_path: Optional[str] = None
        self.library_folders: List[str] = []
    
    def get_steam_install_path(self) -> Optional[str]:
        """从注册表获取 Steam 安装路径"""
        try:
            # 尝试从注册表读取 Steam 路径
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                logger.info(f"找到 Steam 安装路径: {steam_path}")
                return steam_path
        except (OSError, FileNotFoundError):
            # 尝试备用注册表位置
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Valve\Steam") as key:
                    steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    logger.info(f"找到 Steam 安装路径 (备用): {steam_path}")
                    return steam_path
            except (OSError, FileNotFoundError):
                logger.warning("无法从注册表找到 Steam 安装路径")
                return None
    
    def parse_library_folders(self, steam_path: str) -> List[str]:
        """解析 Steam 库文件夹"""
        library_folders = []
        config_path = Path(steam_path) / "config" / "libraryfolders.vdf"
        
        if not config_path.exists():
            logger.warning(f"Steam 库配置文件不存在: {config_path}")
            return library_folders
        
        try:
            if vdf is None:
                logger.error("vdf 库未安装，无法解析 Steam 库文件夹")
                return library_folders
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            # 解析库文件夹数据
            if 'libraryfolders' in data:
                for key, folder_data in data['libraryfolders'].items():
                    if isinstance(folder_data, dict) and 'path' in folder_data:
                        folder_path = folder_data['path']
                        library_folders.append(folder_path)
                        logger.info(f"找到 Steam 库文件夹: {folder_path}")
            
        except Exception as e:
            logger.error(f"解析 Steam 库文件夹失败: {e}")
        
        return library_folders
    
    def scan_steam_games(self) -> List[GameInfo]:
        """扫描 Steam 游戏"""
        games = []
        
        # 获取 Steam 安装路径
        steam_path = self.get_steam_install_path()
        if not steam_path:
            logger.warning("无法找到 Steam 安装路径，跳过 Steam 游戏扫描")
            return games
        
        self.steam_path = steam_path
        self.library_folders = self.parse_library_folders(steam_path)
        
        # 扫描每个库文件夹
        for library_path in self.library_folders:
            steamapps_path = Path(library_path) / "steamapps"
            if not steamapps_path.exists():
                continue
            
            # 扫描 appmanifest 文件
            for manifest_file in steamapps_path.glob("appmanifest_*.acf"):
                try:
                    game_info = self.parse_steam_manifest(manifest_file, library_path)
                    if game_info:
                        games.append(game_info)
                except Exception as e:
                    logger.error(f"解析 Steam 清单文件失败 {manifest_file}: {e}")
        
        logger.info(f"Steam 扫描完成，找到 {len(games)} 个游戏")
        return games
    
    def parse_steam_manifest(self, manifest_path: Path, library_path: str) -> Optional[GameInfo]:
        """解析 Steam 应用清单文件"""
        try:
            if vdf is None:
                logger.error("vdf 库未安装，无法解析 Steam 清单文件")
                return None
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            app_state = data.get('AppState', {})
            app_id = app_state.get('appid')
            name = app_state.get('name')
            install_dir = app_state.get('installdir')
            state_flags = app_state.get('StateFlags', '0')
            
            if not all([app_id, name, install_dir]):
                return None
            
            # 检查游戏是否已安装 (StateFlags & 4 表示已安装)
            is_installed = (int(state_flags) & 4) != 0
            
            # 构建游戏路径
            game_path = Path(library_path) / "steamapps" / "common" / install_dir
            
            # 查找可执行文件（简化版，实际可能需要更复杂的逻辑）
            executable_path = self.find_game_executable(game_path, name)
            
            return GameInfo(
                id=f"steam_{app_id}",
                name=name,
                description=f"Steam 游戏 - {name}",
                developer="Unknown",  # 需要额外 API 调用获取
                publisher="Unknown",
                executable_path=str(executable_path) if executable_path else str(game_path),
                platform=GamePlatform.STEAM,
                category=GameCategory.OTHER,  # 需要额外信息确定分类
                is_installed=is_installed and game_path.exists(),
                tags=["Steam"],
                release_date="Unknown",  # 需要额外 API 调用获取
                image_url="",  # 需要额外 API 调用获取游戏封面
                last_played=None,  # 需要解析 Steam 用户数据
                play_time=0,  # 需要解析 Steam 用户数据
                rating=None  # 需要额外 API 调用获取评分
            )
            
        except Exception as e:
            logger.error(f"解析 Steam 清单失败: {e}")
            return None
    
    def find_game_executable(self, game_path: Path, game_name: str) -> Optional[Path]:
        """在游戏目录中查找可执行文件"""
        if not game_path.exists():
            return None
        
        # 常见的可执行文件扩展名
        exe_extensions = ['.exe']
        
        # 首先尝试查找与游戏名称相似的可执行文件
        for exe_file in game_path.rglob("*.exe"):
            if exe_file.name.lower().replace(' ', '').replace('_', '') in game_name.lower().replace(' ', '').replace('_', ''):
                return exe_file
        
        # 如果没找到，返回第一个可执行文件
        for exe_file in game_path.rglob("*.exe"):
            return exe_file
        
        return None


class EpicScanner:
    """Epic Games 游戏扫描器"""
    
    def __init__(self):
        self.epic_path = self.get_epic_install_path()
    
    def get_epic_install_path(self) -> Optional[str]:
        """获取 Epic Games Launcher 安装路径"""
        # Epic Games 通常安装在这些位置
        common_paths = [
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Epic Games\Launcher"),
            os.path.expandvars(r"%PROGRAMFILES%\Epic Games\Launcher"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"找到 Epic Games Launcher: {path}")
                return path
        
        logger.warning("未找到 Epic Games Launcher 安装路径")
        return None
    
    def scan_epic_games(self) -> List[GameInfo]:
        """扫描 Epic Games 游戏"""
        games = []
        
        if not self.epic_path:
            return games
        
        # Epic Games 游戏信息通常存储在用户数据目录
        user_data_path = Path(os.path.expandvars(r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\Config\Windows"))
        
        # 这里需要实现具体的 Epic Games 数据解析
        # 由于 Epic Games 的数据格式比较复杂，这里提供一个基础框架
        
        logger.info(f"Epic Games 扫描完成，找到 {len(games)} 个游戏")
        return games


class CustomGameManager:
    """自定义游戏管理器"""
    
    def __init__(self):
        self.custom_games_file = Path("custom_games.json")
    
    def load_custom_games(self) -> List[GameInfo]:
        """加载用户添加的自定义游戏"""
        games = []
        
        if not self.custom_games_file.exists():
            return games
        
        try:
            with open(self.custom_games_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for game_data in data.get('games', []):
                game = GameInfo(**game_data)
                # 验证可执行文件是否存在
                if os.path.exists(game.executable_path):
                    game.is_installed = True
                else:
                    game.is_installed = False
                
                games.append(game)
        
        except Exception as e:
            logger.error(f"加载自定义游戏失败: {e}")
        
        logger.info(f"加载了 {len(games)} 个自定义游戏")
        return games
    
    def add_custom_game(self, game_info: GameInfo) -> bool:
        """添加自定义游戏"""
        try:
            games = self.load_custom_games()
            games.append(game_info)
            
            # 保存到文件
            data = {"games": [game.dict() for game in games]}
            with open(self.custom_games_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"添加自定义游戏成功: {game_info.name}")
            return True
        
        except Exception as e:
            logger.error(f"添加自定义游戏失败: {e}")
            return False


class GameScanner:
    """主游戏扫描器，整合所有平台"""
    
    def __init__(self):
        self.steam_scanner = SteamScanner()
        self.epic_scanner = EpicScanner()
        self.custom_manager = CustomGameManager()
        self._games_cache: List[GameInfo] = []
        self._last_scan_time: Optional[float] = None
    
    async def scan_all_games(self, force_refresh: bool = False) -> List[GameInfo]:
        """扫描所有平台的游戏"""
        import time
        
        # 检查缓存是否有效（5分钟内）
        if (not force_refresh and 
            self._last_scan_time and 
            time.time() - self._last_scan_time < 300 and 
            self._games_cache):
            logger.info("使用缓存的游戏列表")
            return self._games_cache
        
        logger.info("开始扫描所有游戏...")
        all_games = []
        
        try:
            # 并发扫描不同平台
            tasks = [
                asyncio.create_task(self._scan_steam_async()),
                asyncio.create_task(self._scan_epic_async()),
                asyncio.create_task(self._scan_custom_async()),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"平台扫描失败: {result}")
                elif isinstance(result, list):
                    all_games.extend(result)
            
            # 去重（基于游戏 ID）
            unique_games = {}
            for game in all_games:
                unique_games[game.id] = game
            
            self._games_cache = list(unique_games.values())
            self._last_scan_time = time.time()
            
            logger.info(f"游戏扫描完成，共找到 {len(self._games_cache)} 个游戏")
            return self._games_cache
        
        except Exception as e:
            logger.error(f"游戏扫描失败: {e}")
            return []
    
    async def _scan_steam_async(self) -> List[GameInfo]:
        """异步扫描 Steam 游戏"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.steam_scanner.scan_steam_games)
    
    async def _scan_epic_async(self) -> List[GameInfo]:
        """异步扫描 Epic Games 游戏"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.epic_scanner.scan_epic_games)
    
    async def _scan_custom_async(self) -> List[GameInfo]:
        """异步扫描自定义游戏"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.custom_manager.load_custom_games)
    
    def get_game_by_id(self, game_id: str) -> Optional[GameInfo]:
        """根据 ID 获取游戏信息"""
        for game in self._games_cache:
            if game.id == game_id:
                return game
        return None
    
    def filter_games(self, 
                     platform: Optional[GamePlatform] = None,
                     category: Optional[GameCategory] = None,
                     installed_only: bool = True) -> List[GameInfo]:
        """筛选游戏列表"""
        filtered = self._games_cache
        
        if platform:
            filtered = [game for game in filtered if game.platform == platform]
        
        if category:
            filtered = [game for game in filtered if game.category == category]
        
        if installed_only:
            filtered = [game for game in filtered if game.is_installed]
        
        return filtered


# 全局游戏扫描器实例
game_scanner = GameScanner()