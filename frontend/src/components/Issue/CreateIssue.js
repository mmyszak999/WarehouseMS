import React, { useState, useEffect } from 'react';
import {
  TextField, Button, Box, Typography, Container, MenuItem, AppBar, Toolbar,
  FormControl, InputLabel, Select, CircularProgress, Snackbar, Alert
} from '@mui/material';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateIssue = () => {
  const [waitingRooms, setWaitingRooms] = useState([]);
  const [stocks, setStocks] = useState({});
  const [formData, setFormData] = useState({
    stock_entries: [], // Array of stock entries each with stock_id and waiting_room_id
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWaitingRooms = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/waiting_rooms/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        setWaitingRooms(response.data.results || []);
        setLoading(false);
      } catch (error) {
        handleError(error, setError);
        setLoading(false);
      }
    };

    fetchWaitingRooms();
  }, []);

  const fetchStocks = async (waitingRoomId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const stocksData = response.data.stocks || [];
      setStocks(prevStocks => ({
        ...prevStocks,
        [waitingRoomId]: stocksData.map(stock => ({
          id: stock.id,
          product_name: stock.product.name,
          product_count: stock.product_count,
          weight: stock.weight
        }))
      }));
    } catch (error) {
      handleError(error, setError);
    }
  };

  const handleStockChange = (e, index) => {
    const { value } = e.target;
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      updatedEntries[index] = { ...updatedEntries[index], stock_id: value };
      return { ...prevState, stock_entries: updatedEntries };
    });
  };

  const handleWaitingRoomChange = (e, index) => {
    const { value } = e.target;
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      updatedEntries[index] = { ...updatedEntries[index], waiting_room_id: value };
      return { ...prevState, stock_entries: updatedEntries };
    });

    // Fetch stocks for the new waiting room
    if (value) {
      fetchStocks(value);
    }
  };

  const handleAddStock = () => {
    setFormData(prevState => ({
      ...prevState,
      stock_entries: [...prevState.stock_entries, { stock_id: '', waiting_room_id: '' }]
    }));
  };

  const handleRemoveStock = (index) => {
    setFormData(prevState => ({
      ...prevState,
      stock_entries: prevState.stock_entries.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Transform stock_entries to the required format
    const formattedStockEntries = formData.stock_entries
      .map(entry => entry.stock_id)
      .filter(id => id) // Remove any empty ids
      .map(id => ({ id }));

    const dataToSubmit = {
      stock_ids: formattedStockEntries,
      description: formData.description
    };

    try {
      const response = await axios.post('http://localhost:8000/api/issues/', dataToSubmit, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setSuccess('Issue created successfully!');
      navigate('/'); // Redirect after success
    } catch (error) {
      handleError(error, setError);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
            My App
          </Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Create Issue</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          {loading ? (
            <CircularProgress />
          ) : (
            <>
              {formData.stock_entries.map((entry, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id={`waiting-room-label-${index}`}>Select Waiting Room</InputLabel>
                    <Select
                      labelId={`waiting-room-label-${index}`}
                      value={entry.waiting_room_id}
                      onChange={(e) => handleWaitingRoomChange(e, index)}
                    >
                      {waitingRooms.map(room => (
                        <MenuItem key={room.id} value={room.id}>
                          {room.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id={`stock-label-${index}`}>Select Stock</InputLabel>
                    <Select
                      labelId={`stock-label-${index}`}
                      value={entry.stock_id}
                      onChange={(e) => handleStockChange(e, index)}
                    >
                      {stocks[entry.waiting_room_id]?.map(stk => (
                        <MenuItem key={stk.id} value={stk.id}>
                          {stk.product_name} (Count: {stk.product_count}, Weight: {stk.weight})
                        </MenuItem>
                      )) || (
                        <MenuItem value="" disabled>
                          No stocks available
                        </MenuItem>
                      )}
                    </Select>
                  </FormControl>
                  <Button
                    type="button"
                    color="error"
                    onClick={() => handleRemoveStock(index)}
                    sx={{ mt: 2 }}
                  >
                    Remove Stock
                  </Button>
                </Box>
              ))}
              <Button
                type="button"
                fullWidth
                variant="contained"
                color="primary"
                onClick={handleAddStock}
                sx={{ mt: 2 }}
              >
                Add Another Stock
              </Button>
              <TextField
                variant="outlined"
                margin="normal"
                fullWidth
                name="description"
                label="Description"
                multiline
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </>
          )}
          {error && (
            <Snackbar open={true} autoHideDuration={6000} onClose={() => setError(null)}>
              <Alert onClose={() => setError(null)} severity="error">
                {error}
              </Alert>
            </Snackbar>
          )}
          {success && (
            <Snackbar open={true} autoHideDuration={6000} onClose={() => setSuccess(null)}>
              <Alert onClose={() => setSuccess(null)} severity="success">
                {success}
              </Alert>
            </Snackbar>
          )}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
          >
            Create Issue
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default CreateIssue;
