/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#04060A',
          900: '#06090F',
          850: '#0A0D13',
          800: '#0E1219',
          700: '#141A24',
          border: '#191F2A',
          borderHi: '#2A3444',
        },
        neon: { DEFAULT: '#2E8BFF', soft: '#7FB4FF', deep: '#1A4FA8' },
        violet: { DEFAULT: '#8B5CF6', soft: '#B79CFF' },
        mint: '#34D399',
        amber: '#F2B33D',
        rose: '#F0616B',
        cyan: '#22D3EE',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: { xl2: '1.15rem' },
      boxShadow: {
        lift: '0 24px 48px -32px rgba(0,0,0,0.95)',
        neon: '0 10px 30px -12px rgba(46,139,255,0.9)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
        pop: {
          '0%': { transform: 'scale(.6)' },
          '60%': { transform: 'scale(1.12)' },
          '100%': { transform: 'scale(1)' },
        },
        sweep: {
          '0%': { transform: 'translateX(-110%)' },
          '100%': { transform: 'translateX(110%)' },
        },
      },
      animation: {
        rise: 'rise .5s cubic-bezier(.22,.8,.3,1) both',
        pop: 'pop .28s cubic-bezier(.22,.8,.3,1) both',
        sweep: 'sweep 1.1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
