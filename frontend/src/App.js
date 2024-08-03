// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { Button, Container, CssBaseline } from '@mui/material';
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
            console.error('Login failed:', error);
        }
    };

    const handleLogout = () => {
        AuthService.logout();
        setIsLoggedIn(false);
    };

    return (
        <Router>
            <CssBaseline />
            <Container maxWidth="sm">
                {isLoggedIn && <Button variant="contained" color="secondary" onClick={handleLogout} style={{ marginTop: '20px', marginBottom: '20px' }}>Logout</Button>}
                <Routes>
                    <Route path="/" element={isLoggedIn ? <Navigate to="/products" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/login" element={isLoggedIn ? <Navigate to="/products" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/products" element={isLoggedIn ? <ProductsList /> : <Navigate to="/login" />} />
                    <Route path="/create-product" element={isLoggedIn ? <CreateProduct /> : <Navigate to="/login" />} />
                </Routes>
            </Container>
        </Router>
    );
};

export default App;
