import React, { useEffect, useRef, useState } from 'react';
import { scoreToColor } from '../utils/score.utils';

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  grade?: string;
  animate?: boolean;
}

export const ScoreRing: React.FC<ScoreRingProps> = ({
  score,
  size = 180,
  strokeWidth = 12,
  label = 'Score',
  grade,
  animate = true,
}) => {
  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);
  const [progress, setProgress] = useState(animate ? 0 : score);
  const animRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = scoreToColor(score);
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (!animate || prefersReduced) {
      setDisplayScore(Math.round(score));
      setProgress(score);
      return;
    }

    const duration = 1200;
    const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

    const tick = (timestamp: number) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const t = Math.min(elapsed / duration, 1);
      const eased = easeOut(t);
      setDisplayScore(Math.round(eased * score));
      setProgress(eased * score);
      if (t < 1) animRef.current = requestAnimationFrame(tick);
    };

    animRef.current = requestAnimationFrame(tick);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      startTimeRef.current = null;
    };
  }, [score, animate, prefersReduced]);

  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="relative"
        style={{
          width: size,
          height: size,
          filter: `drop-shadow(0 0 16px ${color}40)`,
        }}
      >
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#27272A"
            strokeWidth={strokeWidth}
          />
          {/* Progress arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            style={{ transition: 'stroke-dashoffset 0.05s linear, stroke 0.4s ease' }}
          />
        </svg>
        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-mono font-medium leading-none"
            style={{ fontSize: size * 0.22, color: '#FAFAFA' }}
          >
            {displayScore}
          </span>
          {grade && (
            <span
              className="font-mono font-medium mt-1"
              style={{ fontSize: size * 0.1, color }}
            >
              {grade}
            </span>
          )}
        </div>
      </div>
      {label && (
        <span className="text-sm text-text-secondary">{label}</span>
      )}
    </div>
  );
};
