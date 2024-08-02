// src/App.js
import React, { useState } from 'react';
import ProductsList from './components/ProductsList';
import AuthService from './services/AuthService';

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(!!AuthService.getCurrentUser());

    const handleLogin = async (event) => {
        event.preventDefault();
        const { email, password } = event.target.elements;
        try {
            await AuthService.login(email.value, password.value);
            setIsLoggedIn(true);
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    const handleLogout = () => {
        AuthService.logout();
        setIsLoggedIn(false);
    };

    if (!isLoggedIn) {
        return (
            <div>
                <h1>Login</h1>
                <form onSubmit={handleLogin}>
                    <div>
                        <label>Email:</label>
                        <input type="text" name="email" required />
                    </div>
                    <div>
                        <label>Password:</label>
                        <input type="password" name="password" required />
                    </div>
                    <button type="submit">Login</button>
                </form>
            </div>
        );
    }

    return (
        <div>
            <button onClick={handleLogout}>Logout</button>
            <ProductsList />
        </div>
    );
};

export default App;
