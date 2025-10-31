import React, { useState } from 'react';
import { MainLayout } from '../components/Layout';
import { GameLibrary } from '../components/GameLibrary';
import { Button } from '../components/UI';
import { GameInfo } from '../types/game';

export default function Home() {
  const [selectedGame, setSelectedGame] = useState<GameInfo | null>(null);
  const [isLaunching, setIsLaunching] = useState(false);

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
    console.log('启动游戏:', game.name);
    
    // Simulate launch delay
    setTimeout(() => {
      setIsLaunching(false);
      alert(`即将启动: ${game.name}\n平台: ${game.platform}\n路径: ${game.executablePath}`);
    }, 2000);
  };

  return (
    <MainLayout title="喷喷启动器 - 游戏库">
      <div className="h-full relative">
        <GameLibrary
          onGameSelect={handleGameSelect}
          onGameLaunch={handleGameLaunch}
          focusedGameId={selectedGame?.id}
        />
        
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
            <strong>开发预览版</strong><br />
            • 使用方向键或鼠标导航<br />
            • 按回车键启动游戏<br />
            • 当前使用模拟数据
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
