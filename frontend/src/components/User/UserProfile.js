import React, { useEffect, useState } from 'react';
import { Typography, Card, CardContent, CircularProgress, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { handleError } from '../ErrorHandler';

const UserProfile = ({ themeMode }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        handleError(error, setError);
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
          
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to={`/user/${user.id}/history`}
            sx={{ mt: 2 }}
          >
            Check User History
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserProfile;
