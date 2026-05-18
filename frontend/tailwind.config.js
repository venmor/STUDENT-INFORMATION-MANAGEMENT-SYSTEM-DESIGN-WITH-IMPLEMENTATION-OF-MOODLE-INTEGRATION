import forms from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}', './tests/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E4E8C',
          dark: '#163A6B',
          light: '#E8F0FE',
        },
        secondary: {
          DEFAULT: '#0D9488',
          dark: '#0F766E',
          light: '#CCFBF1',
        },
        danger: '#B91C1C',
        warning: '#B45309',
        success: '#15803D',
        info: '#0369A1',
        neutral: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          700: '#334155',
          900: '#0F172A',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Sora"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '12px',
        '2xl': '16px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.07)',
        'card-hover': '0 4px 12px 0 rgb(0 0 0 / 0.10)',
        modal: '0 20px 60px -10px rgb(0 0 0 / 0.25)',
      },
      spacing: {
        page: '1280px',
      },
    },
  },
  plugins: [forms],
}
