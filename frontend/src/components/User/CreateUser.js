import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Container, AppBar, Toolbar, FormControlLabel, Checkbox } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const CreateUser = () => {
  const [userData, setUserData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    birth_date: '',
    employment_date: '',
    is_staff: false,
    can_move_stocks: false,
    can_recept_stocks: false,
    can_issue_stocks: false,
  });
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setUserData({
      ...userData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/users/create', userData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      console.log('User created:', response.data);
      navigate('/users/all');
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
      console.error('Error creating user:', error);
    }
  };

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
        <Typography component="h1" variant="h5">Create User</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="first_name"
            label="First Name"
            name="first_name"
            autoComplete="first_name"
            value={userData.first_name}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="last_name"
            label="Last Name"
            name="last_name"
            autoComplete="last_name"
            value={userData.last_name}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email"
            name="email"
            autoComplete="email"
            value={userData.email}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="birth_date"
            label="Birth Date"
            name="birth_date"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={userData.birth_date}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="employment_date"
            label="Employment Date"
            name="employment_date"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={userData.employment_date}
            onChange={handleChange}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={userData.is_staff}
                onChange={handleChange}
                name="is_staff"
                color="primary"
              />
            }
            label="Staff Member"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={userData.can_move_stocks}
                onChange={handleChange}
                name="can_move_stocks"
                color="primary"
              />
            }
            label="Can Move Stocks"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={userData.can_recept_stocks}
                onChange={handleChange}
                name="can_recept_stocks"
                color="primary"
              />
            }
            label="Can Recept Stocks"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={userData.can_issue_stocks}
                onChange={handleChange}
                name="can_issue_stocks"
                color="primary"
              />
            }
            label="Can Issue Stocks"
          />
          <Button type="submit" fullWidth variant="contained" color="primary" sx={{ mt: 3, mb: 2 }}>
            Create User
          </Button>
          {error && (
            <Typography color="error" variant="body2" align="center">
              {error}
            </Typography>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default CreateUser;
