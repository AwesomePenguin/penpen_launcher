import React, { useState, useEffect } from 'react';
import GameCard from './GameCard';
import { LoadingSpinner } from '../UI';
import { GameInfo } from '../../types/game';

export interface GameLibraryProps {
  games?: GameInfo[];
  loading?: boolean;
  onGameSelect?: (game: GameInfo) => void;
  onGameLaunch?: (game: GameInfo) => void;
  focusedGameId?: string;
}

// Mock data for development
const mockGames: GameInfo[] = [
  {
    id: '1',
    name: 'Cyberpunk 2077',
    description: 'Open-world action-adventure story set in Night City.',
    developer: 'CD Projekt Red',
    publisher: 'CD Projekt',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\Cyberpunk2077\\bin\\x64\\Cyberpunk2077.exe',
    platform: 'steam',
    category: 'rpg',
    isInstalled: true,
    playTime: 4560,
    rating: 4,
    tags: ['RPG', 'Open World', 'Futuristic'],
  },
  {
    id: '2',
    name: 'The Witcher 3: Wild Hunt',
    description: 'Story-driven open world RPG set in a visually stunning fantasy universe.',
    developer: 'CD Projekt Red',
    publisher: 'CD Projekt',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\TheWitcher3\\bin\\x64\\witcher3.exe',
    platform: 'steam',
    category: 'rpg',
    isInstalled: true,
    playTime: 12000,
    rating: 5,
    tags: ['RPG', 'Fantasy', 'Open World'],
  },
  {
    id: '3',
    name: 'Genshin Impact',
    description: 'Open-world action RPG with anime-style graphics.',
    developer: 'miHoYo',
    publisher: 'miHoYo',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\GenshinImpact\\GenshinImpact.exe',
    platform: 'hoyoverse',
    category: 'rpg',
    isInstalled: true,
    playTime: 800,
    rating: 4,
    tags: ['RPG', 'Anime', 'Gacha'],
  },
  {
    id: '4',
    name: 'Fortnite',
    description: 'Battle royale game with building mechanics.',
    developer: 'Epic Games',
    publisher: 'Epic Games',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\Fortnite\\FortniteClient-Win64-Shipping.exe',
    platform: 'epic',
    category: 'action',
    isInstalled: false,
    playTime: 200,
    rating: 3,
    tags: ['Battle Royale', 'Multiplayer', 'Free'],
  },
  {
    id: '5',
    name: 'Overwatch 2',
    description: 'Team-based multiplayer first-person shooter.',
    developer: 'Blizzard Entertainment',
    publisher: 'Blizzard Entertainment',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\Overwatch2\\Overwatch.exe',
    platform: 'battlenet',
    category: 'action',
    isInstalled: true,
    playTime: 3200,
    rating: 4,
    tags: ['FPS', 'Multiplayer', 'Team'],
  },
  {
    id: '6',
    name: 'Custom Game',
    description: 'A custom installed game.',
    developer: 'Unknown Developer',
    imageUrl: '/api/placeholder/300/400',
    executablePath: 'C:\\Games\\CustomGame\\game.exe',
    platform: 'custom',
    category: 'other',
    isInstalled: true,
    playTime: 45,
    tags: ['Indie', 'Custom'],
  },
];

const GameLibrary: React.FC<GameLibraryProps> = ({
  games = mockGames,
  loading = false,
  onGameSelect,
  onGameLaunch,
  focusedGameId,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const filteredGames = games.filter(game => {
    const matchesSearch = game.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         game.developer?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         game.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || game.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const categories = [
    { id: 'all', name: '全部游戏', count: games.length },
    { id: 'rpg', name: '角色扮演', count: games.filter(g => g.category === 'rpg').length },
    { id: 'action', name: '动作游戏', count: games.filter(g => g.category === 'action').length },
    { id: 'strategy', name: '策略游戏', count: games.filter(g => g.category === 'strategy').length },
    { id: 'other', name: '其他', count: games.filter(g => g.category === 'other').length },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="text-tv-title text-console-text mt-4">正在加载游戏库...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with search and filters */}
      <div className="p-6 border-b border-console-border bg-console-surface">
        
        {/* Category filters */}
        <div className="flex space-x-2 overflow-x-auto">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`btn-secondary whitespace-nowrap ${
                selectedCategory === category.id ? 'bg-console-focus text-white' : ''
              }`}
            >
              {category.name} ({category.count})
            </button>
          ))}
        </div>
      </div>

      {/* Game Grid */}
      <div className="flex-1 overflow-y-auto">
        {filteredGames.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <span className="text-tv-4xl opacity-50 block mb-4">🎮</span>
              <p className="text-tv-title text-console-text">未找到游戏</p>
              <p className="text-tv-readable text-console-text-secondary">
                请尝试调整搜索条件或分类筛选
              </p>
            </div>
          </div>
        ) : (
          <div className="game-grid">
            {filteredGames.map((game) => (
              <GameCard
                key={game.id}
                game={game}
                focused={focusedGameId === game.id}
                onSelect={onGameSelect}
                onLaunch={onGameLaunch}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GameLibrary;