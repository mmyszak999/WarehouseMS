// src/components/NotFound.js
import React from 'react';
import { Box, Button, Typography, Container, AppBar, Toolbar } from '@mui/material';
import { Link } from 'react-router-dom';

const NotFound = () => {
    return (
        <Container component="main" maxWidth="xs">
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
                        My App
                    </Typography>
                </Toolbar>
            </AppBar>
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">404 - Page Not Found</Typography>
                <Typography variant="body1" sx={{ mt: 2 }}>Sorry, the page you are looking for does not exist.</Typography>
                <Button variant="contained" color="primary" component={Link} to="/" sx={{ mt: 3, mb: 2 }}>
                    Go to Home
                </Button>
            </Box>
        </Container>
    );
};

export default NotFound;
