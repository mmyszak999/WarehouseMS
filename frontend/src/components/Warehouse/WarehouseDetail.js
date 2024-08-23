import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Typography, CircularProgress, Container, Grid, Card, CardContent, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, AppBar, Toolbar, Box } from '@mui/material';
import axios from 'axios';
import { handleError } from '../ErrorHandler';

const WarehouseDetail = () => {
  const { warehouseId } = useParams();
  const navigate = useNavigate();
  const [warehouse, setWarehouse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false); // For confirming deletion

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

  const handleDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/warehouse/${warehouseId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/'); // Redirect to home after deletion
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md">
        <Typography variant="h4" gutterBottom sx={{ mt: 3 }}>{warehouse.warehouse_name}</Typography>
        <Typography>Max Sections: {warehouse.max_sections}</Typography>
        <Typography>Max Waiting Rooms: {warehouse.max_waiting_rooms}</Typography>
        <Typography>Occupied Sections: {warehouse.occupied_sections}</Typography>
        <Typography>Occupied Waiting Rooms: {warehouse.occupied_waiting_rooms}</Typography>

        {/* Sections */}
        {warehouse.sections && warehouse.sections.length > 0 && (
          <>
            <Typography variant="h5" gutterBottom>Sections</Typography>
            <Grid container spacing={3}>
              {warehouse.sections.map((section) => (
                <Grid item xs={12} key={section.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{section.section_name}</Typography>
                      <Typography>Max Weight: {section.max_weight}</Typography>
                      <Typography>Available Weight: {section.available_weight}</Typography>
                      <Typography>Occupied Weight: {section.occupied_weight}</Typography>
                      <Typography>Available Racks: {section.available_racks}</Typography>
                      <Typography>Occupied Racks: {section.occupied_racks}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </>
        )}

        {/* Waiting Rooms */}
        {warehouse.waiting_rooms && warehouse.waiting_rooms.length > 0 && (
          <>
            <Typography variant="h5" gutterBottom>Waiting Rooms</Typography>
            <Grid container spacing={3}>
              {warehouse.waiting_rooms.map((waitingRoom) => (
                <Grid item xs={12} key={waitingRoom.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{waitingRoom.name || 'Unnamed Waiting Room'}</Typography>
                      <Typography>Max Stocks: {waitingRoom.max_stocks}</Typography>
                      <Typography>Max Weight: {waitingRoom.max_weight}</Typography>
                      <Typography>Occupied Slots: {waitingRoom.occupied_slots}</Typography>
                      <Typography>Current Stock Weight: {waitingRoom.current_stock_weight}</Typography>
                      <Typography>Available Slots: {waitingRoom.available_slots}</Typography>
                      <Typography>Available Stock Weight: {waitingRoom.available_stock_weight}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </>
        )}

        {/* Update and Delete Buttons */}
        <Box sx={{ mt: 3 }}>
          <Button component={Link} to={`/warehouse/update/${warehouseId}`} variant="contained" color="secondary" sx={{ mr: 2 }}>
            Update Warehouse
          </Button>
          <Button 
            variant="contained" 
            color="error" 
            onClick={() => setOpenDialog(true)}
          >
            Delete Warehouse
          </Button>
        </Box>
        
        {/* Confirm Deletion Dialog */}
        <Dialog
          open={openDialog}
          onClose={() => setOpenDialog(false)}
        >
          <DialogTitle>Delete Warehouse</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete the warehouse "{warehouse.warehouse_name}"? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)} color="primary">
              Cancel
            </Button>
            <Button onClick={handleDelete} color="error">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default WarehouseDetail;
