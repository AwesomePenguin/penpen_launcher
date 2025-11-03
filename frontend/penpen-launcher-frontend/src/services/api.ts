/**
 * PenPen Launcher API Service
 * 
 * 提供与后端 FastAPI 服务的通信接口
 * 处理游戏库、系统状态和游戏启动等功能
 */

import { GameInfo, LaunchResult } from '@/types/game';
import { SystemStatus } from '@/types/api';

const API_BASE_URL = 'http://localhost:8000';

/**
 * API 响应类型
 */
interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  error_message?: string;
  timestamp: string;
}

/**
 * API 错误类
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 转换后端数据格式到前端格式
 */
function transformGameInfo(backendGame: any): GameInfo {
  return {
    id: backendGame.id,
    name: backendGame.name,
    description: backendGame.description,
    developer: backendGame.developer,
    publisher: backendGame.publisher,
    releaseDate: backendGame.release_date,
    imageUrl: backendGame.image_url,
    executablePath: backendGame.executable_path,
    platform: backendGame.platform,
    category: backendGame.category,
    isInstalled: backendGame.is_installed,
    lastPlayed: backendGame.last_played ? new Date(backendGame.last_played) : undefined,
    playTime: backendGame.play_time,
    rating: backendGame.rating,
    tags: backendGame.tags || [],
  };
}

/**
 * 基础 API 请求函数
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new ApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }

    const data = await response.json();
    
    // 处理标准化的 API 响应格式
    if (data.status === 'error') {
      throw new ApiError(data.error_message || '未知错误');
    }
    
    return data.data || data; // 返回 data 字段或原始数据
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // 网络错误或其他错误
    throw new ApiError(
      error instanceof Error ? error.message : '网络请求失败'
    );
  }
}

/**
 * 游戏库 API
 */
export const gameApi = {
  /**
   * 获取所有游戏列表
   */
  async getGames(): Promise<GameInfo[]> {
    const backendGames = await apiRequest<any[]>('/api/games');
    return backendGames.map(transformGameInfo);
  },

  /**
   * 启动指定游戏
   */
  async launchGame(gameId: string): Promise<LaunchResult> {
    return apiRequest<LaunchResult>(`/api/games/${gameId}/launch`, {
      method: 'POST',
    });
  },

  /**
   * 获取游戏详细信息（如果后端提供单个游戏端点）
   */
  async getGame(gameId: string): Promise<GameInfo> {
    return apiRequest<GameInfo>(`/api/games/${gameId}`);
  },
};

/**
 * 系统 API
 */
export const systemApi = {
  /**
   * 获取系统状态
   */
  async getStatus(): Promise<SystemStatus> {
    return apiRequest<SystemStatus>('/api/system/status');
  },

  /**
   * 健康检查
   */
  async getHealth(): Promise<{ status: string; service: string }> {
    return apiRequest<{ status: string; service: string }>('/api/health');
  },

  /**
   * 重启系统服务
   */
  async restart(): Promise<{ success: boolean }> {
    return apiRequest<{ success: boolean }>('/api/system/restart', {
      method: 'POST',
    });
  },
};

/**
 * WebSocket 连接管理
 */
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Set<(message: any) => void> = new Set();

  /**
   * 连接 WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // 已经连接
    }

    try {
      this.ws = new WebSocket('ws://localhost:8000/ws');
      
      this.ws.onopen = () => {
        console.log('WebSocket 连接已建立');
        this.clearReconnectTimer();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.messageHandlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('WebSocket 消息解析失败:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket 连接已关闭');
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
      };
    } catch (error) {
      console.error('WebSocket 连接失败:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * 断开 WebSocket
   */
  disconnect(): void {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * 添加消息处理器
   */
  onMessage(handler: (message: any) => void): void {
    this.messageHandlers.add(handler);
  }

  /**
   * 移除消息处理器
   */
  offMessage(handler: (message: any) => void): void {
    this.messageHandlers.delete(handler);
  }

  /**
   * 发送消息
   */
  send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket 未连接，无法发送消息');
    }
  }

  /**
   * 计划重连
   */
  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    this.reconnectTimer = setTimeout(() => {
      console.log('尝试重连 WebSocket...');
      this.connect();
    }, 3000); // 3秒后重连
  }

  /**
   * 清除重连计时器
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

// 导出单例 WebSocket 服务
export const webSocketService = new WebSocketService();

/**
 * API 服务汇总导出
 */
export const api = {
  games: gameApi,
  system: systemApi,
  ws: webSocketService,
};

export default api;