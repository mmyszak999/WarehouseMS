// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import ProductsList from './components/ProductsList';
import AuthService from './services/AuthService';
import Login from './components/Login';
import './App.css';

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
            <div className="container">
                {isLoggedIn && <button className="logout-button" onClick={handleLogout}>Logout</button>}
                <Routes>
                    <Route path="/" element={isLoggedIn ? <Navigate to="/products" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/login" element={isLoggedIn ? <Navigate to="/products" /> : <Login handleLogin={handleLogin} />} />
                    <Route path="/products" element={isLoggedIn ? <ProductsList /> : <Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
