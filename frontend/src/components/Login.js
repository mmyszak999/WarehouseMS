// src/components/Login.js
import React from 'react';
import { TextField, Button, Typography, Box } from '@mui/material';

const Login = ({ handleLogin }) => {
    const handleSubmit = (event) => {
        event.preventDefault();
        const { email, password } = event.target.elements;
        handleLogin(email.value, password.value);
    };

    return (
        <Box component="div" sx={{ mt: 8 }}>
            <Typography component="h1" variant="h5" align="center">
                Login
            </Typography>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="email"
                    label="Email Address"
                    name="email"
                    autoComplete="email"
                    autoFocus
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="password"
                    label="Password"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                />
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                >
                    Login
                </Button>
            </Box>
        </Box>
    );
};

export default Login;
