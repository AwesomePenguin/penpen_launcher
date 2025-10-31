// API and system-related type definitions
export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
  timestamp: string;
}

export interface SystemStatus {
  cpu: {
    usage: number;
    temperature?: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  storage: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    connected: boolean;
    type?: 'wifi' | 'ethernet';
    speed?: number;
  };
  activeGame?: {
    name: string;
    pid: number;
    startTime: Date;
  };
}

export interface WebSocketMessage {
  type: 'gameStatusChange' | 'systemStatusUpdate' | 'gameLibraryUpdate';
  data: any;
  timestamp: string;
}

export interface UpdateInfo {
  available: boolean;
  currentVersion: string;
  latestVersion?: string;
  downloadUrl?: string;
  changelog?: string;
}