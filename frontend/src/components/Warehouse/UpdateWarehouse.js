import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TextField, Button, Typography, Container, CircularProgress } from '@mui/material';
import axios from 'axios';
import { handleError } from '../ErrorHandler';

const UpdateWarehouse = () => {
  const { warehouseId } = useParams();
  const navigate = useNavigate();
  const [warehouse, setWarehouse] = useState({ warehouse_name: '', max_sections: 0, max_waiting_rooms: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWarehouseDetail = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/warehouse/${warehouseId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setWarehouse(response.data);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchWarehouseDetail();
  }, [warehouseId]);

  const handleInputChange = (e) => {
    setWarehouse({ ...warehouse, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.patch(`http://localhost:8000/api/warehouse/${warehouseId}`, warehouse, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate(`/warehouse/${warehouseId}`);
    } catch (error) {
      handleError(error, setError);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Update Warehouse</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Warehouse Name"
          name="warehouse_name"
          value={warehouse.warehouse_name}
          onChange={handleInputChange}
          fullWidth
          margin="normal"
          required
        />
        <TextField
          label="Max Sections"
          name="max_sections"
          type="number"
          value={warehouse.max_sections}
          onChange={handleInputChange}
          fullWidth
          margin="normal"
          required
        />
        <TextField
          label="Max Waiting Rooms"
          name="max_waiting_rooms"
          type="number"
          value={warehouse.max_waiting_rooms}
          onChange={handleInputChange}
          fullWidth
          margin="normal"
          required
        />
        <Button type="submit" variant="contained" color="primary">
          Update
        </Button>
      </form>
    </Container>
  );
};

export default UpdateWarehouse;
