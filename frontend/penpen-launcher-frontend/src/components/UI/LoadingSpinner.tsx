import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color = 'var(--console-focus)',
  className = '',
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  const spinnerStyle = {
    borderColor: `${color}33`, // 20% opacity for border
    borderTopColor: color,
  };

  return (
    <div
      className={`animate-spin rounded-full border-2 ${sizeClasses[size]} ${className}`}
      style={spinnerStyle}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export default LoadingSpinner;