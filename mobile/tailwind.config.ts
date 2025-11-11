import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#488AFF',
        secondary: '#2DD4BF',
        danger: '#FF6B6B',
        warning: '#FFD93D',
        success: '#6BCB77',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      spacing: {
        'safe-top': 'max(1rem, env(safe-area-inset-top))',
        'safe-right': 'max(1rem, env(safe-area-inset-right))',
        'safe-bottom': 'max(1rem, env(safe-area-inset-bottom))',
        'safe-left': 'max(1rem, env(safe-area-inset-left))',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
} satisfies Config
