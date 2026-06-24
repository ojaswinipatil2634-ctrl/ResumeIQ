import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({ label, error, icon, className = '', id, ...props }) => {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-text-secondary">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`w-full bg-bg-elevated border ${error ? 'border-danger' : 'border-border-subtle'} rounded-sm px-3 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors ${icon ? 'pl-10' : ''} ${className}`}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-danger">{error}</p>}
    </div>
  );
};
