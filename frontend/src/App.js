// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import { Button, Container, AppBar, Toolbar, Typography, Box, IconButton, CssBaseline, ThemeProvider } from '@mui/material';
import ProductsList from './components/ProductsList';
import ProductDetail from './components/ProductDetail';
import AuthService from './services/AuthService';
import Login from './components/Login';
import CreateProduct from './components/CreateProduct';
import NotFound from './components/NotFound';
import './App.css';
import getTheme from './theme';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(!!AuthService.getCurrentUser());
  const [themeMode, setThemeMode] = useState('light');

  useEffect(() => {
    document.body.className = themeMode;
  }, [themeMode]);

  const handleLogin = async (email, password) => {
    try {
      await AuthService.login(email, password);
      setIsLoggedIn(true);
    } catch (error) {
      throw new Error(error.message);
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setIsLoggedIn(false);
  };

  const toggleTheme = () => {
    setThemeMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={getTheme(themeMode)}>
      <CssBaseline />
      <Router>
        <AppBar position="static" className={`app-bar ${themeMode}`}>
          <Toolbar>
            <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
              My App
            </Typography>
            <IconButton color="inherit" onClick={toggleTheme}>
              <i className={`fa fa-${themeMode === 'light' ? 'moon' : 'sun'}`} />
            </IconButton>
            {isLoggedIn && <Button color="inherit" onClick={handleLogout}>Logout</Button>}
          </Toolbar>
        </AppBar>
        <Container maxWidth="sm" sx={{ mt: 4 }} className={`container ${themeMode}`}>
          <Routes>
            <Route
              path="/"
              element={
                isLoggedIn ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
                    <Button variant="contained" color="primary" component={Link} to="/products" sx={{ mb: 2 }}>
                      View Products
                    </Button>
                  </Box>
                ) : (
                  <Login handleLogin={handleLogin} />
                )
              }
            />
            <Route path="/login" element={isLoggedIn ? <Navigate to="/" /> : <Login handleLogin={handleLogin} />} />
            <Route path="/products" element={isLoggedIn ? <ProductsList themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/product/:productId" element={isLoggedIn ? <ProductDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/product/create" element={isLoggedIn ? <CreateProduct themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
};

export default App;
