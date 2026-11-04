/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#04050A',
          900: '#070A12',
          880: '#0A0E18',
          850: '#0D1220',
          800: '#121828',
          700: '#1A2233',
          border: '#1D2537',
          borderHi: '#33415E',
        },
        neon: { DEFAULT: '#4C8DFF', soft: '#9CC2FF', deep: '#1E4FA8' },
        violet: { DEFAULT: '#8B5CF6', soft: '#C4B0FF' },
        mint: '#3CE6A0',
        amber: '#FFB84D',
        gold: '#FFC857',
        rose: '#FF5C7A',
        cyan: '#38E8FF',
        lime: '#C6FF4D',
        ember: '#FF7A45',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Sora', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: { xl2: '1.15rem', '3xl': '1.75rem' },
      boxShadow: {
        lift: '0 40px 80px -60px rgba(0,0,0,0.95)',
        neon: '0 16px 40px -18px rgba(76,141,255,0.85)',
        violet: '0 16px 40px -18px rgba(139,92,246,0.8)',
        inset: 'inset 0 1px 0 rgba(255,255,255,0.07)',
      },
      backgroundImage: {
        'grid-faint':
          'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
        'neon-sweep': 'linear-gradient(135deg, #7FE9FF 0%, #4C8DFF 52%, #8B5CF6 100%)',
        'gold-sweep': 'linear-gradient(135deg, #FFE9A8 0%, #FFC857 45%, #FF9A3D 100%)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
        pop: {
          '0%': { transform: 'scale(.55)', opacity: '.4' },
          '60%': { transform: 'scale(1.14)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        drift: {
          '0%,100%': { transform: 'translate3d(0,0,0) scale(1)' },
          '50%': { transform: 'translate3d(18px,-22px,0) scale(1.06)' },
        },
        breathe: {
          '0%,100%': { opacity: '.55' },
          '50%': { opacity: '1' },
        },
        shine: {
          '0%': { transform: 'translateX(-130%) skewX(-18deg)' },
          '100%': { transform: 'translateX(150%) skewX(-18deg)' },
        },
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
      animation: {
        rise: 'rise .55s cubic-bezier(.22,.8,.3,1) both',
        pop: 'pop .3s cubic-bezier(.22,.8,.3,1) both',
        drift: 'drift 16s ease-in-out infinite',
        breathe: 'breathe 3.4s ease-in-out infinite',
        shine: 'shine .9s ease-out',
        ticker: 'ticker 26s linear infinite',
      },
    },
  },
  plugins: [],
}
