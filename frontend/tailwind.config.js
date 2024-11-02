/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        pulse: {
          '0%, 100%': {
            opacity: 1,
          },
          '50%': {
            opacity: .5,
          },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#ececec',
            p: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
            },
            a: {
              color: '#00A3BF',
              '&:hover': {
                color: '#008CA6',
              },
            },
            h3: {
              color: '#ececec',
              marginTop: '1.5em',
              marginBottom: '0.75em',
            },
            ul: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
              listStyleType: 'disc',
              paddingLeft: '1.625em',
            },
            li: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            strong: {
              color: '#ececec',
              fontWeight: '600',
            },
            blockquote: {
              borderLeftColor: '#343637',
              color: '#ececec',
              fontStyle: 'italic',
              marginLeft: 0,
              paddingLeft: '1em',
            },
            code: {
              color: '#ececec',
              backgroundColor: '#1a1b1e',
              padding: '0.2em 0.4em',
              borderRadius: '0.25em',
              fontSize: '0.875em',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}