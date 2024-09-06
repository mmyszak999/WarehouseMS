import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, Typography, CircularProgress, Link as MuiLink, AppBar, Toolbar, Button } from '@mui/material';
import { useParams, Link } from 'react-router-dom';
import { handleError } from '../ErrorHandler';
import AuthService from '../../services/AuthService';

const StockDetail = () => {
  const { stockId } = useParams();
  const [stock, setStock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isStaff, setIsStaff] = useState(false);

    useEffect(() => {
        const fetchUserRole = () => {
            setIsStaff(AuthService.getUserRole());
        };

        fetchUserRole();
    }, []);

  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchStock = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/api/stocks/${stockId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setStock(response.data);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchStock();
  }, [stockId, token]);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  if (!stock) return <Typography>No stock data found.</Typography>;

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* AppBar with Home Link */}
      <AppBar position="static">
        <Toolbar>
          <Button color="inherit" component={Link} to="/">
            Home
          </Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ padding: 3 }}>
        <Typography variant="h4" gutterBottom>
          Stock Details
        </Typography>
        <Typography variant="h6">
          <strong>Product: </strong> 
          <MuiLink
            component={Link}
            to={`/product/${stock.product.id}`}
            sx={{ textDecoration: 'none', color: 'primary.main' }}
          >
            {stock.product.name}
          </MuiLink>
        </Typography>
        <Typography variant="subtitle1">
          <strong>Description:</strong> {stock.product.description}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Weight:</strong> {stock.product.weight}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Stock Weight:</strong> {stock.weight}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Product Count:</strong> {stock.product_count}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Waiting Room: </strong> 
          {stock.waiting_room ? (
            <MuiLink
              component={Link}
              to={`/waiting_room/${stock.waiting_room.id}`}
              sx={{ textDecoration: 'none', color: 'primary.main' }}
            >
              {stock.waiting_room.name}
            </MuiLink>
          ) : 'N/A'}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Rack Level Slot:</strong> {stock.rack_level_slot ? stock.rack_level_slot.description : 'N/A'}
        </Typography>
        <Typography variant="subtitle1">
          <strong>Created At:</strong> {stock.created_at}
        </Typography>
      </Box>
    </Box>
  );
};

export default StockDetail;
