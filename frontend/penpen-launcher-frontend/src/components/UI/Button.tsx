import React from 'react';

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  focused?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  onClick,
  disabled = false,
  className = '',
  focused = false,
}) => {
  const baseClasses = 'focusable font-semibold rounded-lg transition-all duration-200 border-none outline-none';
  
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
  };

  const sizeClasses = {
    small: 'py-2 px-4 min-h-10 min-w-20 text-sm',
    medium: 'py-3 px-6 min-h-12 min-w-24',
    large: 'py-4 px-8 min-h-14 min-w-32 text-lg',
  };

  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : '';
  const focusedClasses = focused ? 'focused' : '';

  const combinedClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    disabledClasses,
    focusedClasses,
    className
  ].filter(Boolean).join(' ');

  const handleClick = () => {
    if (!disabled && onClick) {
      onClick();
    }
  };

  return (
    <button
      className={combinedClasses}
      onClick={handleClick}
      disabled={disabled}
      tabIndex={0}
    >
      {children}
    </button>
  );
};

export default Button;