// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import { Button, Container, CssBaseline, AppBar, Toolbar, Typography } from '@mui/material';
import ProductsList from './components/ProductsList';
import AuthService from './services/AuthService';
import Login from './components/Login';
import CreateProduct from './components/CreateProduct';

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(!!AuthService.getCurrentUser());

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

    return (
        <Router>
            <CssBaseline />
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        My App
                    </Typography>
                    {isLoggedIn ? (
                        <>
                            <Button color="inherit" component={Link} to="/products">Products</Button>
                            <Button color="inherit" component={Link} to="/create-product">Create Product</Button>
                            <Button color="inherit" onClick={handleLogout}>Logout</Button>
                        </>
                    ) : (
                        <Button color="inherit" component={Link} to="/login">Login</Button>
                    )}
                </Toolbar>
            </AppBar>
            <Container maxWidth="sm" sx={{ mt: 4 }}>
                <Routes>
                    <Route path="/" element={isLoggedIn ? <Navigate to="/" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/login" element={isLoggedIn ? <Navigate to="/" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/products" element={isLoggedIn ? <ProductsList /> : <Navigate to="/login" />} />
                    <Route path="/create-product" element={isLoggedIn ? <CreateProduct /> : <Navigate to="/login" />} />
                </Routes>
            </Container>
        </Router>
    );
};

export default App;
