import React, { useEffect, useState } from 'react';
import { Typography, Card, CardContent, CircularProgress, Container, AppBar, Toolbar, Button, Grid, Box } from '@mui/material';
import axios from 'axios';
import { Link } from 'react-router-dom';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const WarehousesList = ({ themeMode }) => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isStaff, setIsStaff] = useState(false);

  useEffect(() => {
    const fetchUserRole = () => {
      setIsStaff(AuthService.getUserRole());
    };

    fetchUserRole();
  }, []);

  useEffect(() => {
    const fetchWarehouses = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/warehouse/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setWarehouses(response.data.results);
      } catch (error) {
        handleError(error, setError);
    } finally {
        setLoading(false);
      }
    };

    fetchWarehouses();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <Button color="inherit" component={Link} to="/warehouse/create">Create Warehouse</Button>
          )}
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" className={`container ${themeMode}`}>
        <Typography variant="h4" gutterBottom>Warehouses</Typography>
        {warehouses.length > 0 ? (
          <Grid container spacing={3}>
            {warehouses.map((warehouse) => (
              <Grid item xs={12} key={warehouse.id}>
                <Card className={`card ${themeMode}`} sx={{ marginBottom: 2 }}>
                  <CardContent>
                    <Typography variant="h5">
                      {isStaff ? (
                        <Link to={`/warehouse/${warehouse.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                          {warehouse.warehouse_name}
                        </Link>
                      ) : (
                        warehouse.warehouse_name
                      )}
                    </Typography>
                    <Typography>Max Sections: {warehouse.max_sections}</Typography>
                    <Typography>Max Waiting Rooms: {warehouse.max_waiting_rooms}</Typography>
                    <Typography>Occupied Sections: {warehouse.occupied_sections}</Typography>
                    <Typography>Occupied Waiting Rooms: {warehouse.occupied_waiting_rooms}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography>No warehouses available</Typography>
        )}
      </Container>
    </Box>
  );
};

export default WarehousesList;
