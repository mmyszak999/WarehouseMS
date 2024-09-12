import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { TextField, Button, CircularProgress, Box, Typography } from '@mui/material';
import { handleError } from '../ErrorHandler'; // Error handler
import AuthService from '../../services/AuthService';

const UpdateSection = () => {
  const { sectionId } = useParams(); // Get section ID from route params
  const navigate = useNavigate();
  const [section, setSection] = useState({ section_name: '', max_weight: 0, max_racks: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isStaff = AuthService.getUserRole();

  useEffect(() => {
    const fetchSection = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        });
        setSection(response.data);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchSection();
  }, [sectionId]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSection({ ...section, [name]: value });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`http://localhost:8000/api/sections/${sectionId}`, section, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
      navigate(`/section/${sectionId}`); // Navigate back to section details after update
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) return <CircularProgress />;

  if (error) return <Typography variant="h6" color="error">{error}</Typography>;

  return (
    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h6" gutterBottom>Edit Section</Typography>
      <form onSubmit={handleFormSubmit}>
        <TextField
          label="Section Name"
          name="section_name"
          value={section.section_name}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Weight"
          name="max_weight"
          type="number"
          value={section.max_weight}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <TextField
          label="Max Racks"
          name="max_racks"
          type="number"
          value={section.max_racks}
          onChange={handleInputChange}
          fullWidth
          required
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" color="primary">
          Update Section
        </Button>
      </form>
    </Box>
  );
};

export default UpdateSection;
