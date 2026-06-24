import React from 'react';

// ── Card ─────────────────────────────────────────────────────────────────────
interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}
export const Card: React.FC<CardProps> = ({ children, className = '', glow = false }) => (
  <div className={`glass-card card-shadow p-6 ${glow ? 'glow-primary' : ''} ${className}`}>
    {children}
  </div>
);

// ── Badge ─────────────────────────────────────────────────────────────────────
interface BadgeProps {
  children: React.ReactNode;
  color?: string;
  className?: string;
}
export const Badge: React.FC<BadgeProps> = ({ children, color, className = '' }) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}
    style={color ? { backgroundColor: color + '22', color, border: `1px solid ${color}44` } : {}}
  >
    {children}
  </span>
);

// ── Spinner ──────────────────────────────────────────────────────────────────
export const Spinner: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className="animate-spin"
    aria-label="Loading"
  >
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.2" />
    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
  </svg>
);

// ── Progress ──────────────────────────────────────────────────────────────────
interface ProgressProps {
  value: number;
  color?: string;
  className?: string;
}
export const Progress: React.FC<ProgressProps> = ({ value, color = '#6366F1', className = '' }) => (
  <div className={`h-2 bg-bg-elevated rounded-full overflow-hidden ${className}`}>
    <div
      className="h-full rounded-full transition-all duration-700 ease-out"
      style={{ width: `${Math.min(100, Math.max(0, value))}%`, backgroundColor: color }}
    />
  </div>
);

// ── Skeleton ──────────────────────────────────────────────────────────────────
export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-bg-elevated rounded animate-pulse ${className}`} />
);
