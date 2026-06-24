/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'bg-base': '#09090B',
        'bg-surface': '#111113',
        'bg-elevated': '#18181B',
        'border-subtle': '#27272A',
        'border-accent': '#3F3F46',
        primary: '#6366F1',
        'primary-glow': 'rgba(99,102,241,0.15)',
        secondary: '#8B5CF6',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#38BDF8',
        'text-primary': '#FAFAFA',
        'text-secondary': '#A1A1AA',
        'text-muted': '#52525B',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '12px',
        lg: '16px',
        xl: '24px',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A78BFA 100%)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 20s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
    },
  },
  plugins: [],
}
