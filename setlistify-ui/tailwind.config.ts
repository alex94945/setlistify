import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)'],
        mono: ['var(--font-geist-mono)'],
      },
      colors: {
        'purple-accent': '#6d28d9',
        purple: {
          '700': '#6d28d9',
        },
        spotify: {
          green: '#1DB954',
        },
      },
    },
  },
  plugins: [],
};

export default config;
