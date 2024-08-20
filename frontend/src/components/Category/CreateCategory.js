import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Container, AppBar, Toolbar } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuthService from '../../services/AuthService';

const CreateCategory = () => {
    const [categoryName, setCategoryName] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const isStaff = AuthService.getUserRole();

    const handleChange = (e) => {
        setCategoryName(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/api/categories', { name: categoryName }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log('Category created:', response.data);
            navigate('/categories'); // Redirect to the categories list
        } catch (error) {
            if (error.response) {
                switch (error.response.status) {
                    case 422:
                        const schema_error = JSON.parse(error.request.response)
                        setError('Validation Error: ' + (schema_error.detail[0]?.msg || 'Invalid input'));
                        break;
                    case 500:
                        setError('Server Error: Please try again later');
                        break;
                    case 401:
                        setError('Error: ' + (error.response.statusText || 'You were logged out! '));
                        break;
                    default:
                        const default_error = JSON.parse(error.request.response)
                        setError('Error: ' + (default_error.detail || 'An unexpected error occurred'));
                        break;
                }
            } else if (error.request) {
                // Handle network errors
                setError('Network Error: No response received from server');
            } else {
                // Handle other errors
                setError('Error: ' + error.message);
            }
            console.error('Error fetching users:', error);
        }
    };

    if (!isStaff) {
        return <Typography variant="h6" color="error">You do not have permission to access this page.</Typography>;
    }

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
                <Typography component="h1" variant="h5">Create Category</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    <TextField
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        id="name"
                        label="Category Name"
                        name="name"
                        autoComplete="name"
                        autoFocus
                        value={categoryName}
                        onChange={handleChange}
                    />
                    {error && (
                        <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                            {error}
                        </Typography>
                    )}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Create Category
                    </Button>
                </Box>
            </Box>
        </Container>
    );
};

export default CreateCategory;
