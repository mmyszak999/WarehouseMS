import React, { useState } from 'react';
import { TextField, Button, Typography, Container } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateWaitingRoom = ({ themeMode }) => {
  const [name, setName] = useState('');
  const [maxStocks, setMaxStocks] = useState(0);
  const [maxWeight, setMaxWeight] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/waiting_rooms/', {
        name: name,
        max_stocks: maxStocks,
        max_weight: maxWeight,
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/waiting_rooms');
    } catch (error) {
      handleError(error, setError);
    }
  };

  return (
    <Container maxWidth="sm" className={`container ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Create Waiting Room</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Name"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          label="Max Stocks"
          type="number"
          fullWidth
          value={maxStocks}
          onChange={(e) => setMaxStocks(parseInt(e.target.value))}
          margin="normal"
          required
        />
        <TextField
          label="Max Weight"
          type="number"
          fullWidth
          value={maxWeight}
          onChange={(e) => setMaxWeight(parseInt(e.target.value))}
          margin="normal"
          required
        />
        {error && <Typography color="error">{error}</Typography>}
        <Button type="submit" variant="contained" color="primary" fullWidth>Create</Button>
      </form>
    </Container>
  );
};

export default CreateWaitingRoom;
