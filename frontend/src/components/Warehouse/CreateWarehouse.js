import React, { useState } from 'react';
import { TextField, Button, Typography, Container } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateWarehouse = ({ themeMode }) => {
  const [warehouseName, setWarehouseName] = useState('');
  const [maxSections, setMaxSections] = useState(0);
  const [maxWaitingRooms, setMaxWaitingRooms] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/warehouse/', {
        warehouse_name: warehouseName,
        max_sections: maxSections,
        max_waiting_rooms: maxWaitingRooms,
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/warehouses');
    } catch (error) {
        handleError(error, setError);
    }
  };

  return (
    <Container maxWidth="sm" className={`container ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Create Warehouse</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Warehouse Name"
          fullWidth
          value={warehouseName}
          onChange={(e) => setWarehouseName(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          label="Max Sections"
          type="number"
          fullWidth
          value={maxSections}
          onChange={(e) => setMaxSections(parseInt(e.target.value))}
          margin="normal"
          required
        />
        <TextField
          label="Max Waiting Rooms"
          type="number"
          fullWidth
          value={maxWaitingRooms}
          onChange={(e) => setMaxWaitingRooms(parseInt(e.target.value))}
          margin="normal"
          required
        />
        {error && <Typography color="error">{error}</Typography>}
        <Button type="submit" variant="contained" color="primary" fullWidth>Create</Button>
      </form>
    </Container>
  );
};

export default CreateWarehouse;
