import React, { useState } from 'react';
import { TextField, Button, Typography, Container } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateSection = ({ themeMode }) => {
  const [sectionName, setSectionName] = useState('');
  const [maxWeight, setMaxWeight] = useState(0);
  const [maxRacks, setMaxRacks] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/sections/', {
        section_name: sectionName,
        max_weight: maxWeight,
        max_racks: maxRacks,
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      navigate('/sections');
    } catch (error) {
      handleError(error, setError);
    }
  };

  return (
    <Container maxWidth="sm" className={`container ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Create Section</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Section Name"
          fullWidth
          value={sectionName}
          onChange={(e) => setSectionName(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          label="Max Weight"
          type="number"
          fullWidth
          value={maxWeight}
          onChange={(e) => setMaxWeight(parseFloat(e.target.value))}
          margin="normal"
          required
        />
        <TextField
          label="Max Racks"
          type="number"
          fullWidth
          value={maxRacks}
          onChange={(e) => setMaxRacks(parseInt(e.target.value))}
          margin="normal"
          required
        />
        {error && <Typography color="error">{error}</Typography>}
        <Button type="submit" variant="contained" color="primary" fullWidth>
          Create
        </Button>
      </form>
    </Container>
  );
};

export default CreateSection;
