// Game-related type definitions
export interface GameInfo {
  id: string;
  name: string;
  description?: string;
  developer?: string;
  publisher?: string;
  releaseDate?: string;
  imageUrl?: string;
  executablePath: string;
  platform: GamePlatform;
  category: GameCategory;
  isInstalled: boolean;
  lastPlayed?: Date;
  playTime?: number;
  rating?: number;
  tags: string[];
}

export type GamePlatform = 'steam' | 'epic' | 'battlenet' | 'custom' | 'hoyoverse';

export type GameCategory = 'action' | 'adventure' | 'rpg' | 'strategy' | 'simulation' | 'sports' | 'other';

export interface GameLaunchRequest {
  gameId: string;
  launchOptions?: LaunchOptions;
}

export interface LaunchOptions {
  launcherPreference?: GamePlatform;
  additionalArgs?: string[];
  fullscreen?: boolean;
}

export interface LaunchResult {
  success: boolean;
  processId?: number;
  error?: string;
}