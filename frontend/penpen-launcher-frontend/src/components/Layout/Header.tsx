import React from 'react';

export interface HeaderProps {
  title?: string;
  showSystemInfo?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  title = 'PenPen Launcher',
  showSystemInfo = true,
}) => {
  return (
    <header className="flex justify-between items-center p-6 border-b border-console-border bg-console-surface">
      <div className="flex items-center space-x-4">
        <h1 className="text-tv-title text-console-text font-bold">
          {title}
        </h1>
      </div>
      
      {showSystemInfo && (
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-console-success"></div>
            <span className="text-tv-readable text-console-text-secondary">系统在线</span>
          </div>
          
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