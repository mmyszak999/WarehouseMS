import React, { useEffect, useState } from 'react';
import { Typography, Card, CardContent, CircularProgress, Box } from '@mui/material';
import axios from 'axios';
import AuthService from '../../services/AuthService';

const UserProfile = ({ themeMode }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/users/me', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setUser(response.data);
      } catch (error) {
        handleError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Card className={`card ${themeMode}`} sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" fontWeight="bold">{user.first_name} {user.last_name}</Typography>
          <Typography variant="body2">Email: {user.email}</Typography>
          <Typography variant="body2">Employment Date: {user.employment_date}</Typography>
          <Typography variant="body2">Birth Date: {user.birth_date}</Typography>
          <Typography variant="body2">Can Move Stocks: {user.can_move_stocks ? 'Yes' : 'No'}</Typography>
          <Typography variant="body2">Can Recept Stocks: {user.can_recept_stocks ? 'Yes' : 'No'}</Typography>
          <Typography variant="body2">Can Issue Stocks: {user.can_issue_stocks ? 'Yes' : 'No'}</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserProfile;
