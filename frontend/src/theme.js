// src/theme.js
import { createTheme } from '@mui/material/styles';

const getTheme = (mode) => createTheme({
  palette: {
    mode,
    ...(mode === 'dark' && {
      primary: {
        main: '#90caf9',
      },
      secondary: {
        main: '#f48fb1',
      },
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
      text: {
        primary: '#e0e0e0',
        secondary: '#b0b0b0',
      },
    }),
  },
  components: {
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: mode === 'dark' ? '#e0e0e0' : '#000',
        },
      },
    },
  },
});

export default getTheme;
