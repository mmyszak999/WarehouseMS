// src/components/Login.js
import React from 'react';

const Login = ({ handleLogin }) => {
    const handleSubmit = (event) => {
        event.preventDefault();
        const { email, password } = event.target.elements;
        handleLogin(email.value, password.value);
    };

    return (
        <div className="container">
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
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
};

export default Login;
