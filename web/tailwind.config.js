/** @type {import('tailwindcss').Config} */
// Design tokens are defined as `R G B` triplets in src/index.css and referenced
// here through the `rgb(var(--token) / <alpha-value>)` pattern so every color
// supports Tailwind opacity modifiers (e.g. bg-primary/10).
const token = (name) => `rgb(var(${name}) / <alpha-value>)`

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: token('--bg'),
        surface: token('--surface'),
        'surface-2': token('--surface-2'),
        'surface-3': token('--surface-3'),
        border: token('--border'),
        'border-strong': token('--border-strong'),
        foreground: token('--fg'),
        muted: token('--muted-fg'),
        primary: {
          DEFAULT: token('--primary'),
          fg: token('--primary-fg'),
          soft: token('--primary-soft'),
        },
        info: token('--info'),
        warning: token('--warning'),
        danger: token('--danger'),
        'framework-pytorch': token('--fw-pytorch'),
        'framework-tensorflow': token('--fw-tensorflow'),
        'framework-sklearn': token('--fw-sklearn'),
        'framework-onnx': token('--fw-onnx'),
      },
      fontFamily: {
        sans: ['"Fira Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"Fira Code"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      fontSize: {
        'display': ['2.25rem', { lineHeight: '1.15', letterSpacing: '-0.02em', fontWeight: '700' }],
        'title': ['1.5rem', { lineHeight: '1.25', letterSpacing: '-0.01em', fontWeight: '600' }],
        'eyebrow': ['0.6875rem', { lineHeight: '1', letterSpacing: '0.12em', fontWeight: '600' }],
      },
      borderRadius: {
        lg: '0.625rem',
        xl: '0.875rem',
        '2xl': '1.125rem',
      },
      boxShadow: {
        card: '0 1px 2px 0 rgb(0 0 0 / 0.3), 0 1px 3px 0 rgb(0 0 0 / 0.2)',
        'card-hover': '0 8px 24px -6px rgb(0 0 0 / 0.5)',
        glow: '0 0 0 1px rgb(var(--primary) / 0.4), 0 8px 24px -8px rgb(var(--primary) / 0.35)',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          from: { opacity: '0', transform: 'translateX(16px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
        'bar-stripes': {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '1rem 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in 200ms ease-out',
        'slide-up': 'slide-up 240ms cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-right': 'slide-in-right 240ms cubic-bezier(0.16, 1, 0.3, 1)',
        shimmer: 'shimmer 1.5s infinite',
        'bar-stripes': 'bar-stripes 1s linear infinite',
      },
    },
  },
  plugins: [],
}
