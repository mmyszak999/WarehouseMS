import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import {
  TextField, Button, CircularProgress, Typography, Box, AppBar, Toolbar
} from '@mui/material';
import { handleError } from '../ErrorHandler';

const UpdateRackLevelSlot = ({ themeMode }) => {
  const { rackLevelSlotId } = useParams();
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRackLevelSlot = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setDescription(response.data.description || '');
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchRackLevelSlot();
  }, [rackLevelSlotId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await axios.patch(`http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}`, { description }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate(`/rack-level-slot/${rackLevelSlotId}`);
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
        </Toolbar>
      </AppBar>
      
      <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>Update Rack Level Slot</Typography>
        
        <form onSubmit={handleSubmit}>
          <TextField
            label="Description"
            variant="outlined"
            fullWidth
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            sx={{ mb: 2 }}
          />

          <Button type="submit" variant="contained" color="primary">
            Update
          </Button>
        </form>
      </Box>
    </Box>
  );
};

export default UpdateRackLevelSlot;
