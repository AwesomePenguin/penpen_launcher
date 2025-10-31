import React from 'react';
import Header from './Header';

export interface MainLayoutProps {
  children: React.ReactNode;
  title?: string;
  showHeader?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  title,
  showHeader = true,
}) => {
  return (
    <div className="tv-safe-area h-screen w-screen flex flex-col">
      {showHeader && <Header title={title} />}
      
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
      
      {/* Footer/Status Bar */}
      <footer className="flex justify-between items-center p-4 border-t border-console-border bg-console-surface">
        <div className="flex items-center space-x-4">
          <span className="text-tv-readable text-console-text-secondary">
            按 OPTIONS 键打开菜单
          </span>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-console-focus animate-focus-pulse"></div>
            <span className="text-tv-readable text-console-text-secondary">手柄已连接</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;