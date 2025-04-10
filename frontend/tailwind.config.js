/** @type {import('tailwindcss').Config} */
// eslint-disable-next-line no-undef
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      container: {
        center: true,
        padding: {
          DEFAULT: '0rem',
          lg: '0rem',
        },
        screens: {
          sm: '100%',
          md: '1200px',
          lg: '1340px',
          '2xl': '1400px',
        },
      },
      fontFamily: {
        primary: ['var(--font-primary)'],
      },
      colors: {
        generator: 'var(--generator-color)',
        'generator-light': 'var(--generator-light-color)',
        predictor: '#E55057',
        predictorLight: '#E5505733',
        extender: '#4CB448',
        extenderLight: '#4CB44833',
        default: '#5183F0',
        defaultLight: '#5183F033',
      },
      boxShadow: {
        'nav-icon': '3.33px 3.33px 26.67px 0px #00000014',
        playground: '4px 4px 32px 0px #5183F014',
        footer: '0px -4px 16px 0px #5183F014',
      },
      backgroundImage: {
        btn: 'linear-gradient(90deg, #2EE1E2 -3.75%, #49CDFE 27.32%, #6A59C1 73.65%, #9541A3 109.25%)',
        login:
          'linear-gradient(90deg, rgba(46, 225, 226, 0.4) -3.75%, rgba(73, 205, 254, 0.4) 27.32%, rgba(106, 89, 193, 0.4) 73.65%, rgba(149, 65, 163, 0.4) 109.25%)',
        shade:
          'linear-gradient(90deg, #2EE1E2 -3.75%, #49CDFE 27.32%, #6A59C1 73.65%, #9541A3 109.25%)',
        'predictor-main':
          'linear-gradient(90deg, #E4464E -4.54%, rgba(228, 70, 78, 0.776) 43.82%, rgba(255, 255, 255, 0) 100%)',
        'extender-main':
          'linear-gradient(90deg, #4CB448 -4.54%, rgba(76, 180, 72, 0.776) 43.82%, rgba(255, 255, 255, 0) 100%)',
        card: 'linear-gradient(176.74deg, #FFFFFF 5.33%, #E1EAFF 78.64%)',
      },
    },
  },
  plugins: [],
};
