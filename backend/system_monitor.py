"""
PenPen Launcher 系统监控器

提供系统状态监控、性能信息收集和硬件信息获取功能。
支持 CPU、内存、存储、网络等系统资源的实时监控。
"""

import asyncio
import logging
import platform
import time
from typing import Dict, Optional, List
import os
from pathlib import Path
import subprocess

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


logger = logging.getLogger("penpen_launcher.system_monitor")


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.monitoring_interval = 5  # 监控间隔（秒）
        self.monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._system_stats = {}
        
        # 检查依赖
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil 未安装，系统监控功能将受限")
    
    async def start_monitoring(self):
        """开始系统监控"""
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitor_system())
            logger.info("系统监控已启动")
    
    async def stop_monitoring(self):
        """停止系统监控"""
        self._shutdown_event.set()
        if self.monitoring_task:
            await self.monitoring_task
        logger.info("系统监控已停止")
    
    def get_system_info(self) -> Dict:
        """获取系统基本信息"""
        try:
            system_info = {
                "os": {
                    "name": platform.system(),
                    "version": platform.version(),
                    "release": platform.release(),
                    "architecture": platform.architecture()[0]
                },
                "hostname": platform.node(),
                "uptime": self._get_system_uptime(),
                "python_version": platform.python_version()
            }
            
            if PSUTIL_AVAILABLE:
                boot_time = psutil.boot_time()
                system_info["boot_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))
                system_info["os"]["name"] = platform.system()
            
            return system_info
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def get_cpu_info(self) -> Dict:
        """获取 CPU 信息"""
        try:
            cpu_info = {
                "model": platform.processor(),
                "cores": {
                    "physical": os.cpu_count(),
                    "logical": os.cpu_count()
                }
            }
            
            if PSUTIL_AVAILABLE:
                cpu_info["cores"]["physical"] = psutil.cpu_count(logical=False)
                cpu_info["cores"]["logical"] = psutil.cpu_count(logical=True)
                cpu_info["frequency"] = {
                    "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    "max": psutil.cpu_freq().max if psutil.cpu_freq() else None
                }
                # 获取当前 CPU 使用率
                cpu_info["usage"] = psutil.cpu_percent(interval=1)
                cpu_info["per_core"] = psutil.cpu_percent(interval=1, percpu=True)
            
            return cpu_info
        except Exception as e:
            logger.error(f"获取 CPU 信息失败: {e}")
            return {}
    
    def get_memory_info(self) -> Dict:
        """获取内存信息"""
        try:
            memory_info = {}
            
            if PSUTIL_AVAILABLE:
                virtual_mem = psutil.virtual_memory()
                swap_mem = psutil.swap_memory()
                
                memory_info = {
                    "virtual": {
                        "total": self._bytes_to_gb(virtual_mem.total),
                        "available": self._bytes_to_gb(virtual_mem.available),
                        "used": self._bytes_to_gb(virtual_mem.used),
                        "percentage": virtual_mem.percent
                    },
                    "swap": {
                        "total": self._bytes_to_gb(swap_mem.total),
                        "used": self._bytes_to_gb(swap_mem.used),
                        "percentage": swap_mem.percent
                    }
                }
            else:
                # 备用方法：通过 Windows 命令获取内存信息
                memory_info = self._get_memory_info_fallback()
            
            return memory_info
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}
    
    def get_disk_info(self) -> Dict:
        """获取磁盘信息"""
        try:
            disk_info = {}
            
            if PSUTIL_AVAILABLE:
                # 获取所有磁盘分区
                partitions = psutil.disk_partitions()
                disk_info["partitions"] = []
                
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partition_info = {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": self._bytes_to_gb(usage.total),
                            "used": self._bytes_to_gb(usage.used),
                            "free": self._bytes_to_gb(usage.free),
                            "percentage": round((usage.used / usage.total) * 100, 2)
                        }
                        disk_info["partitions"].append(partition_info)
                    except PermissionError:
                        continue
                
                # 磁盘 I/O 统计
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info["io"] = {
                        "read_bytes": self._bytes_to_gb(disk_io.read_bytes),
                        "write_bytes": self._bytes_to_gb(disk_io.write_bytes),
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count
                    }
            
            return disk_info
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {}
    
    def get_network_info(self) -> Dict:
        """获取网络信息"""
        try:
            network_info = {}
            
            if PSUTIL_AVAILABLE:
                # 网络接口信息
                net_if = psutil.net_if_addrs()
                network_info["interfaces"] = {}
                
                for interface_name, addresses in net_if.items():
                    interface_info = []
                    for addr in addresses:
                        interface_info.append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        })
                    network_info["interfaces"][interface_name] = interface_info
                
                # 网络 I/O 统计
                net_io = psutil.net_io_counters()
                if net_io:
                    network_info["io"] = {
                        "bytes_sent": self._bytes_to_gb(net_io.bytes_sent),
                        "bytes_recv": self._bytes_to_gb(net_io.bytes_recv),
                        "packets_sent": net_io.packets_sent,
                        "packets_recv": net_io.packets_recv
                    }
            
            return network_info
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {}
    
    def get_process_list(self) -> List[Dict]:
        """获取进程列表"""
        try:
            processes = []
            
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                    try:
                        process_info = proc.info
                        processes.append({
                            "pid": process_info['pid'],
                            "name": process_info['name'],
                            "cpu_percent": process_info['cpu_percent'],
                            "memory_percent": round(process_info['memory_percent'], 2),
                            "status": process_info['status']
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            return processes
        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")
            return []
    
    def get_current_stats(self) -> Dict:
        """获取当前系统统计信息"""
        return {
            "timestamp": time.time(),
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info()
        }
    
    async def _monitor_system(self):
        """系统监控主循环"""
        logger.info("开始系统资源监控...")
        
        while not self._shutdown_event.is_set():
            try:
                # 更新系统统计信息
                self._system_stats = self.get_current_stats()
                
                # 检查资源使用情况并记录警告
                self._check_resource_warnings()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"系统监控错误: {e}")
                await asyncio.sleep(self.monitoring_interval)
        
        logger.info("系统监控已停止")
    
    def _check_resource_warnings(self):
        """检查资源使用情况并发出警告"""
        try:
            if not self._system_stats:
                return
            
            # 检查 CPU 使用率
            cpu_info = self._system_stats.get("cpu", {})
            cpu_usage = cpu_info.get("usage", 0)
            if cpu_usage > 90:
                logger.warning(f"CPU 使用率过高: {cpu_usage}%")
            
            # 检查内存使用率
            memory_info = self._system_stats.get("memory", {})
            virtual_mem = memory_info.get("virtual", {})
            memory_percentage = virtual_mem.get("percentage", 0)
            if memory_percentage > 90:
                logger.warning(f"内存使用率过高: {memory_percentage}%")
            
            # 检查磁盘使用率
            disk_info = self._system_stats.get("disk", {})
            partitions = disk_info.get("partitions", [])
            for partition in partitions:
                if partition.get("percentage", 0) > 90:
                    logger.warning(f"磁盘 {partition['device']} 使用率过高: {partition['percentage']}%")
        
        except Exception as e:
            logger.error(f"检查资源警告失败: {e}")
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """将字节转换为 GB"""
        return round(bytes_value / (1024**3), 2)
    
    def _get_system_uptime(self) -> Optional[str]:
        """获取系统运行时间"""
        try:
            if PSUTIL_AVAILABLE:
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                return self._format_uptime(uptime_seconds)
            else:
                # Windows 备用方法
                return self._get_uptime_windows()
        except Exception as e:
            logger.error(f"获取系统运行时间失败: {e}")
            return None
    
    def _format_uptime(self, seconds: float) -> str:
        """格式化运行时间"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}天 {hours}小时 {minutes}分钟"
    
    def _get_uptime_windows(self) -> Optional[str]:
        """Windows 系统获取运行时间的备用方法"""
        try:
            result = subprocess.run(
                ["wmic", "os", "get", "LastBootUpTime", "/value"],
                capture_output=True,
                text=True
            )
            # 解析输出获取启动时间
            # 这里需要解析 WMIC 输出
            return "未知"
        except Exception:
            return None
    
    def _get_memory_info_fallback(self) -> Dict:
        """备用的内存信息获取方法"""
        try:
            # 使用 Windows 命令获取内存信息
            result = subprocess.run(
                ["wmic", "OS", "get", "TotalVirtualMemorySize,TotalVisibleMemorySize,FreeVirtualMemory,FreePhysicalMemory", "/value"],
                capture_output=True,
                text=True
            )
            # 这里需要解析 WMIC 输出
            return {
                "virtual": {
                    "total": 0,
                    "available": 0,
                    "used": 0,
                    "percentage": 0
                }
            }
        except Exception:
            return {}


# 全局系统监控器实例
system_monitor = SystemMonitor()