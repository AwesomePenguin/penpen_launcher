import React, { useState, useEffect } from 'react';
import { MainLayout } from '../components/Layout';
import { GameLibrary } from '../components/GameLibrary';
import { Button } from '../components/UI';
import { GameInfo } from '../types/game';
import { api, ApiError } from '../services/api';

export default function Home() {
  const [selectedGame, setSelectedGame] = useState<GameInfo | null>(null);
  const [isLaunching, setIsLaunching] = useState(false);
  const [games, setGames] = useState<GameInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载游戏库数据
  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const gameList = await api.games.getGames();
      setGames(gameList);
      console.log('从后端加载游戏:', gameList.length, '个游戏');
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : '加载游戏库失败';
      setError(errorMessage);
      console.error('加载游戏失败:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGameSelect = (game: GameInfo) => {
    setSelectedGame(game);
    console.log('Game selected:', game.name);
  };

  const handleGameLaunch = async (game: GameInfo) => {
    if (!game.isInstalled) {
      alert(`${game.name} 尚未安装。请先安装游戏。`);
      return;
    }

    setIsLaunching(true);
    setSelectedGame(game);
    console.log('启动游戏:', game.name);
    
    try {
      const result = await api.games.launchGame(game.id);
      if (result.success) {
        alert(`游戏启动成功！\n游戏: ${game.name}\n进程 ID: ${result.processId}`);
      } else {
        alert(`游戏启动失败：${result.error || '未知错误'}`);
      }
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : '启动游戏时发生错误';
      alert(`启动失败：${errorMessage}`);
      console.error('游戏启动失败:', err);
    } finally {
      setIsLaunching(false);
    }
  };

  return (
    <MainLayout title="喷喷启动器 - 游戏库">
      <div className="h-full relative">
        {isLoading ? (
          // 加载状态
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-console-focus border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-tv-readable text-console-text">正在加载游戏库...</p>
            </div>
          </div>
        ) : error ? (
          // 错误状态
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-tv-readable text-red-400 mb-4">⚠️ {error}</p>
              <Button onClick={loadGames} variant="primary">
                重新加载
              </Button>
            </div>
          </div>
        ) : (
          // 正常显示游戏库
          <GameLibrary
            games={games}
            onGameSelect={handleGameSelect}
            onGameLaunch={handleGameLaunch}
            focusedGameId={selectedGame?.id}
          />
        )}
        
        {/* Launch confirmation overlay */}
        {isLaunching && (
          <div className="absolute inset-0 bg-console-dark bg-opacity-90 flex items-center justify-center animate-fade-in">
            <div className="bg-console-surface border border-console-border rounded-tv-lg p-8 text-center animate-scale-in">
              <div className="mb-4">
                <div className="w-16 h-16 border-4 border-console-focus border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
              <h3 className="text-tv-title text-console-text font-bold mb-2">
                正在启动游戏...
              </h3>
              <p className="text-tv-readable text-console-text-secondary">
                请稍候，正在启动 {selectedGame?.name}
              </p>
            </div>
          </div>
        )}
        
        {/* Development info overlay */}
        <div className="absolute bottom-4 right-4 bg-console-surface border border-console-border rounded-tv-lg p-4 opacity-80">
          <p className="text-sm text-console-text-secondary">
            <strong>实时数据版本</strong><br />
            • 使用方向键或鼠标导航<br />
            • 按回车键启动游戏<br />
            • 连接到后端 API (端口 8000)
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
