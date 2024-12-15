import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { TextField, Button, CircularProgress, Box, Typography } from '@mui/material';
import { handleError } from '../ErrorHandler';
import AuthService from '../../services/AuthService';

const UpdateRack = () => {
  const { rackId } = useParams();
  const navigate = useNavigate();
  const [rack, setRack] = useState({
    rack_name: '',
    max_weight: 0,
    max_levels: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isStaff = AuthService.getUserRole();

  useEffect(() => {
    const fetchRack = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/racks/${rackId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        });
        setRack(response.data);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchRack();
  }, [rackId]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRack({ ...rack, [name]: value });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`http://localhost:8000/api/racks/${rackId}`, rack, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
      navigate(`/rack/${rackId}`);
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) return <CircularProgress />;

  if (error) return <Typography variant="h6" color="error">{error}</Typography>;

  return (
    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h6" gutterBottom>Edit Rack</Typography>
      <form onSubmit={handleFormSubmit} style={{ width: '100%', maxWidth: 600 }}>
        <TextField
          label="Rack Name"
          name="rack_name"
          value={rack.rack_name}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Weight"
          name="max_weight"
          type="number"
          value={rack.max_weight}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Levels"
          name="max_levels"
          type="number"
          value={rack.max_levels}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" color="primary">
          Update Rack
        </Button>
      </form>
    </Box>
  );
};

export default UpdateRack;
