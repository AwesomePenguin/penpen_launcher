"""
PenPen Launcher 后端测试脚本

快速验证后端组件是否正常工作
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加上级目录到 Python 路径以导入后端模块
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置简单的日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_imports():
    """测试所有模块导入"""
    try:
        logger.info("测试模块导入...")
        
        # 测试数据模型
        from models import GameInfo, GamePlatform, GameCategory, LaunchRequest, SystemStatus
        logger.info("✓ models.py 导入成功")
        
        # 测试游戏扫描器
        from game_scanner import GameScanner, game_scanner
        logger.info("✓ game_scanner.py 导入成功")
        
        # 测试进程管理器
        from process_manager import ProcessManager, process_manager
        logger.info("✓ process_manager.py 导入成功")
        
        # 测试系统监控器
        from system_monitor import SystemMonitor, system_monitor
        logger.info("✓ system_monitor.py 导入成功")
        
        # 测试核心 API
        from core_api import app
        logger.info("✓ core_api.py 导入成功")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ 导入错误: {e}")
        return False

async def test_game_scanner():
    """测试游戏扫描器功能"""
    try:
        logger.info("测试游戏扫描器...")
        
        from game_scanner import game_scanner
        
        # 测试游戏扫描（快速模式，使用缓存）
        games = await game_scanner.scan_all_games(force_refresh=False)
        logger.info(f"✓ 游戏扫描完成，找到 {len(games)} 个游戏")
        
        if games:
            logger.info(f"  示例游戏: {games[0].name} ({games[0].platform})")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 游戏扫描器测试失败: {e}")
        return False

async def test_process_manager():
    """测试进程管理器"""
    try:
        logger.info("测试进程管理器...")
        
        from process_manager import process_manager
        
        # 获取当前活跃游戏
        active_games = process_manager.get_active_games()
        logger.info(f"✓ 当前活跃游戏: {len(active_games)} 个")
        
        # 获取系统资源使用情况
        resource_usage = process_manager.get_system_resource_usage()
        if resource_usage:
            logger.info(f"✓ 系统资源获取成功")
            if 'cpu' in resource_usage:
                logger.info(f"  CPU 使用率: {resource_usage['cpu'].get('usage', 'N/A')}%")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 进程管理器测试失败: {e}")
        return False

async def test_system_monitor():
    """测试系统监控器"""
    try:
        logger.info("测试系统监控器...")
        
        from system_monitor import system_monitor
        
        # 获取系统信息
        system_info = system_monitor.get_system_info()
        if system_info:
            logger.info(f"✓ 系统信息获取成功")
            logger.info(f"  操作系统: {system_info.get('os', {}).get('name', 'Unknown')}")
        
        # 获取 CPU 信息
        cpu_info = system_monitor.get_cpu_info()
        if cpu_info:
            logger.info(f"✓ CPU 信息获取成功")
            cores = cpu_info.get('cores', {})
            logger.info(f"  CPU 核心: {cores.get('physical', 'Unknown')}物理/{cores.get('logical', 'Unknown')}逻辑")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 系统监控器测试失败: {e}")
        return False

async def test_api_models():
    """测试数据模型创建"""
    try:
        logger.info("测试数据模型...")
        
        from models import GameInfo, GamePlatform, GameCategory
        from datetime import datetime
        
        # 创建测试游戏信息
        test_game = GameInfo(
            id="test_game_1",
            name="测试游戏",
            description="这是一个测试游戏",
            developer="测试开发者",
            publisher="测试发行商",
            executable_path="C:\\test\\game.exe",
            platform=GamePlatform.STEAM,
            category=GameCategory.ACTION,
            is_installed=True,
            tags=["测试", "示例"],
            release_date="2025-01-01",
            image_url=None,
            last_played=None,
            play_time=0,
            rating=None
        )
        
        logger.info(f"✓ 游戏模型创建成功: {test_game.name}")
        logger.info(f"  游戏 ID: {test_game.id}")
        logger.info(f"  平台: {test_game.platform}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 数据模型测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    logger.info("=== PenPen Launcher 后端测试开始 ===")
    
    # 检查当前目录
    backend_dir = Path(__file__).parent.parent
    logger.info(f"后端目录: {backend_dir}")
    
    # 检查必要文件是否存在
    required_files = [
        "models.py",
        "game_scanner.py", 
        "process_manager.py",
        "system_monitor.py",
        "core_api.py",
        "launcher.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (backend_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"✗ 缺少必要文件: {missing_files}")
        return False
    
    logger.info("✓ 所有必要文件存在")
    
    # 运行各项测试
    tests = [
        ("模块导入", test_imports),
        ("数据模型", test_api_models),
        ("游戏扫描器", test_game_scanner),
        ("进程管理器", test_process_manager),
        ("系统监控器", test_system_monitor),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- 测试 {test_name} ---")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✓ {test_name} 测试通过")
            else:
                logger.error(f"✗ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"✗ {test_name} 测试异常: {e}")
    
    # 测试结果
    logger.info(f"\n=== 测试结果 ===")
    logger.info(f"通过: {passed}/{total} 测试")
    
    if passed == total:
        logger.info("🎉 所有测试通过！后端准备就绪")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} 个测试失败，请检查依赖安装和配置")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"测试运行异常: {e}")
        sys.exit(1)