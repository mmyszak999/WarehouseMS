import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { TextField, Button, CircularProgress, Box, Typography } from '@mui/material';
import { handleError } from '../ErrorHandler';
import AuthService from '../../services/AuthService';

const UpdateRackLevel = () => {
  const { rackLevelId } = useParams();
  const navigate = useNavigate();
  const [rackLevel, setRackLevel] = useState({
    description: '',
    max_weight: 0,
    max_slots: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isStaff = AuthService.getUserRole();

  useEffect(() => {
    const fetchRackLevel = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/rack_levels/${rackLevelId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        });
        setRackLevel(response.data);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchRackLevel();
  }, [rackLevelId]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRackLevel({ ...rackLevel, [name]: value });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`http://localhost:8000/api/rack_levels/${rackLevelId}`, rackLevel, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
      navigate(`/rack-level/${rackLevelId}`);
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) return <CircularProgress />;

  if (error) return <Typography variant="h6" color="error">{error}</Typography>;

  return (
    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h6" gutterBottom>Edit Rack Level</Typography>
      <form onSubmit={handleFormSubmit} style={{ width: '100%', maxWidth: 600 }}>
        <TextField
          label="Description"
          name="description"
          value={rackLevel.description}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Weight"
          name="max_weight"
          type="number"
          value={rackLevel.max_weight}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Slots"
          name="max_slots"
          type="number"
          value={rackLevel.max_slots}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" color="primary">
          Update Rack Level
        </Button>
      </form>
    </Box>
  );
};

export default UpdateRackLevel;
