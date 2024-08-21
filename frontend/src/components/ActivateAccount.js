import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TextField, Button, Container, Typography, Box } from '@mui/material';
import axios from 'axios';

const ActivateAccount = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [passwordRepeat, setPasswordRepeat] = useState('');
  const [error, setError] = useState('');

  const handleError = (error) => {
    if (error.response) {
        switch (error.response.status) {
            case 422:
                const schema_error = JSON.parse(error.request.response);
                setError('Validation Error: ' + (schema_error.detail[0]?.msg || 'Invalid input'));
                break;
            case 500:
                setError('Server Error: Please try again later');
                break;
            case 401:
                setError('Error: ' + (error.response.statusText || 'You were logged out!'));
                break;
            default:
                const default_error = JSON.parse(error.request.response);
                setError('Error: ' + (default_error.detail || 'An unexpected error occurred'));
                break;
        }
    } else if (error.request) {
        setError('Network Error: No response received from server');
    } else {
        setError('Error: ' + error.message);
    }
    console.error('Error:', error);
};

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== passwordRepeat) {
      setError('Passwords do not match.');
      return;
    }

    try {
      const response = await axios.post(`http://localhost:8000/api/email/confirm-account-activation/${token}`, {
        password,
        password_repeat: passwordRepeat,
      });

      if (response.status === 200) {
        alert('Account activated successfully!');
        navigate('/login');
      } else {
        setError('Something went wrong. Please try again.');
      }
    } catch (error) {
      handleError(error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">
          Activate Account
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="password_repeat"
            label="Repeat Password"
            type="password"
            value={passwordRepeat}
            onChange={(e) => setPasswordRepeat(e.target.value)}
            autoComplete="new-password"
          />
          {error && (
            <Typography color="error" variant="body2">
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
            Submit
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default ActivateAccount;
