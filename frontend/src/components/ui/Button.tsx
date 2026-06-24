import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  children,
  disabled,
  className = '',
  ...props
}) => {
  const base = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-bg-base rounded-sm disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'gradient-bg text-white hover:opacity-90 active:scale-95',
    ghost: 'bg-transparent text-text-secondary hover:text-text-primary hover:bg-white/5 border border-border-subtle',
    danger: 'bg-danger/10 text-danger border border-danger/30 hover:bg-danger/20',
    outline: 'bg-transparent text-primary border border-primary/40 hover:bg-primary/10',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
};
