import React, { useState, useEffect } from 'react';
import { SystemStatus } from '@/types/api';
import { api, ApiError } from '@/services/api';

export interface HeaderProps {
  title?: string;
  showSystemInfo?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  title = 'PenPen Launcher',
  showSystemInfo = true,
}) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取系统状态
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        setError(null);
        const status = await api.system.getStatus();
        setSystemStatus(status);
        console.log('系统状态获取成功:', status);
      } catch (err) {
        const errorMessage = err instanceof ApiError ? err.message : '获取系统状态失败';
        setError(errorMessage);
        console.error('系统状态获取失败:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSystemStatus();
    
    // 定期更新系统状态（每10秒）
    const interval = setInterval(fetchSystemStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const formatStorageSize = (sizeGB: number): string => {
    if (sizeGB >= 1000) {
      return `${(sizeGB / 1000).toFixed(1)}TB`;
    }
    return `${sizeGB.toFixed(0)}GB`;
  };

  const getStatusColor = (percentage: number): string => {
    if (percentage >= 90) return 'text-red-400';
    if (percentage >= 70) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getNetworkIcon = (type?: string): string => {
    switch (type) {
      case 'wifi': return '📶';
      case 'ethernet': return '🔗';
      default: return '🌐';
    }
  };

  return (
    <header className="flex justify-between items-center p-6 border-b border-console-border bg-console-surface">
      <div className="flex items-center space-x-4">
        <h1 className="text-tv-title text-console-text font-bold">
          {title}
        </h1>
      </div>
      
      {showSystemInfo && (
        <div className="flex items-center space-x-6">
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse"></div>
              <span className="text-tv-readable text-console-text-secondary">加载系统状态...</span>
            </div>
          ) : error ? (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <span className="text-tv-readable text-console-text-secondary">系统状态错误</span>
            </div>
          ) : systemStatus ? (
            <>
              {/* CPU状态 */}
              <div className="flex items-center space-x-2">
                <span className="text-tv-readable text-console-text-secondary">CPU:</span>
                <span className={`text-tv-readable font-mono ${getStatusColor(systemStatus.cpu.usage)}`}>
                  {systemStatus.cpu.usage.toFixed(1)}%
                </span>
                {systemStatus.cpu.temperature && (
                  <span className="text-tv-readable text-console-text-secondary">
                    ({systemStatus.cpu.temperature.toFixed(0)}°C)
                  </span>
                )}
              </div>

              {/* 内存状态 */}
              <div className="flex items-center space-x-2">
                <span className="text-tv-readable text-console-text-secondary">内存:</span>
                <span className={`text-tv-readable font-mono ${getStatusColor(systemStatus.memory.percentage)}`}>
                  {systemStatus.memory.percentage.toFixed(1)}%
                </span>
                <span className="text-tv-readable text-console-text-secondary">
                  ({formatStorageSize(systemStatus.memory.used)}/{formatStorageSize(systemStatus.memory.total)})
                </span>
              </div>

              {/* 存储状态 */}
              <div className="flex items-center space-x-2">
                <span className="text-tv-readable text-console-text-secondary">存储:</span>
                <span className={`text-tv-readable font-mono ${getStatusColor(systemStatus.storage.percentage)}`}>
                  {systemStatus.storage.percentage.toFixed(1)}%
                </span>
                <span className="text-tv-readable text-console-text-secondary">
                  ({formatStorageSize(systemStatus.storage.used)}/{formatStorageSize(systemStatus.storage.total)})
                </span>
              </div>

              {/* 网络状态 */}
              <div className="flex items-center space-x-2">
                <span className="text-tv-readable text-console-text-secondary">
                  {getNetworkIcon(systemStatus.network.type)}
                </span>
                <div className={`w-3 h-3 rounded-full ${systemStatus.network.connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-tv-readable text-console-text-secondary">
                  {systemStatus.network.connected ? '在线' : '离线'}
                </span>
                {systemStatus.network.speed && (
                  <span className="text-tv-readable text-console-text-secondary">
                    ({systemStatus.network.speed}Mbps)
                  </span>
                )}
              </div>

              {/* 活动游戏状态 */}
              {systemStatus.activeGame && (
                <div className="flex items-center space-x-2">
                  <span className="text-tv-readable text-console-text-secondary">游戏:</span>
                  <span className="text-tv-readable text-green-400">
                    {systemStatus.activeGame.name}
                  </span>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              <span className="text-tv-readable text-console-text-secondary">系统状态未知</span>
            </div>
          )}
          
          <div className="text-tv-readable text-console-text-secondary">
            {new Date().toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;