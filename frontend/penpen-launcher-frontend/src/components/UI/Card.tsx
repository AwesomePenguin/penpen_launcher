import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  focused?: boolean;
  title?: string;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  onClick,
  focused = false,
  title,
}) => {
  const baseClasses = 'game-card';
  const clickableClasses = onClick ? 'focusable cursor-pointer' : '';
  const focusedClasses = focused ? 'focused' : '';

  const combinedClasses = [
    baseClasses,
    clickableClasses,
    focusedClasses,
    className
  ].filter(Boolean).join(' ');

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (onClick && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <div
      className={combinedClasses}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={onClick ? 0 : -1}
      role={onClick ? 'button' : undefined}
      aria-label={title}
    >
      {children}
    </div>
  );
};

export default Card;