import React, { useState } from 'react';
import Image from 'next/image';
import { Card } from '../UI';
import { GameInfo } from '../../types/game';

export interface GameCardProps {
  game: GameInfo;
  focused?: boolean;
  onSelect?: (game: GameInfo) => void;
  onLaunch?: (game: GameInfo) => void;
}

const GameCard: React.FC<GameCardProps> = ({
  game,
  focused = false,
  onSelect,
  onLaunch,
}) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  const handleCardClick = () => {
    if (onSelect) {
      onSelect(game);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && onLaunch) {
      event.preventDefault();
      onLaunch(game);
    }
  };

  const formatPlayTime = (minutes?: number): string => {
    if (!minutes) return '从未游玩';
    
    if (minutes < 60) return `${minutes}分钟`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}小时`;
    
    const days = Math.floor(hours / 24);
    return `${days}天${hours % 24}小时`;
  };

  const getPlatformIcon = (platform: string): string => {
    switch (platform) {
      case 'steam': return '🎮';
      case 'epic': return '🏪';
      case 'battlenet': return '⚔️';
      case 'hoyoverse': return '🌟';
      default: return '📁';
    }
  };

  return (
    <Card
      focused={focused}
      onClick={handleCardClick}
      className="animate-scale-in"
      title={game.name}
    >
      <div
        className="w-full h-full flex flex-col"
        onKeyDown={handleKeyDown}
        tabIndex={0}
      >
        {/* Game Image */}
        <div className="relative w-full h-48 bg-console-accent overflow-hidden">
          {game.imageUrl && !imageError ? (
            <Image
              src={game.imageUrl}
              alt={game.name}
              fill
              style={{ objectFit: 'cover' }}
              onLoad={() => setImageLoading(false)}
              onError={() => {
                setImageError(true);
                setImageLoading(false);
              }}
              className={`transition-opacity duration-300 ${imageLoading ? 'opacity-0' : 'opacity-100'}`}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-console-accent">
              <span className="text-tv-4xl opacity-50">🎮</span>
            </div>
          )}
          
          {/* Platform Badge */}
          <div className="absolute top-2 left-2">
            <span className="bg-console-dark bg-opacity-80 text-console-text px-2 py-1 rounded text-sm">
              {getPlatformIcon(game.platform)} {game.platform.toUpperCase()}
            </span>
          </div>
          
          {/* Installation Status */}
          {!game.isInstalled && (
            <div className="absolute top-2 right-2">
              <span className="bg-console-warning text-console-dark px-2 py-1 rounded text-sm font-semibold">
                未安装
              </span>
            </div>
          )}
        </div>

        {/* Game Info */}
        <div className="p-4 flex-1">
          <h3 className="text-tv-title text-console-text font-bold mb-2 line-clamp-2">
            {game.name}
          </h3>
          
          {game.developer && (
            <p className="text-tv-readable text-console-text-secondary mb-2">
              {game.developer}
            </p>
          )}
          
          {game.description && (
            <p className="text-tv-readable text-console-text-secondary mb-3 line-clamp-2">
              {game.description}
            </p>
          )}
          
          <div className="flex justify-between items-center text-sm text-console-text-secondary">
            <span>
              游戏时长: {formatPlayTime(game.playTime)}
            </span>
            
            {game.rating && (
              <div className="flex items-center">
                <span className="text-console-warning">★</span>
                <span className="ml-1">{game.rating}/5</span>
              </div>
            )}
          </div>
          
          {/* Tags */}
          {game.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {game.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="bg-console-border text-console-text-secondary px-2 py-1 rounded text-xs"
                >
                  {tag}
                </span>
              ))}
              {game.tags.length > 3 && (
                <span className="text-console-text-secondary text-xs">
                  +{game.tags.length - 3} 更多
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default GameCard;