import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  CircularProgress, Typography, Grid, Card, CardContent, Box, AppBar, Toolbar, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle
} from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler'; // Error handling

const RackLevelDetail = ({ themeMode }) => {
  const { rackLevelId } = useParams();
  const navigate = useNavigate();
  const [rackLevel, setRackLevel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const isStaff = AuthService.getUserRole(); // Check if user is staff
  const canMoveStocks = AuthService.canMoveStocks();

  const fetchRackLevelDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/rack_levels/${rackLevelId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setRackLevel(response.data);
    } catch (error) {
      handleError(error, setError); // Handle errors
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRackLevelDetails();
  }, [rackLevelId]);

  const handleUpdateClick = () => {
    navigate(`/rack-level/${rackLevelId}/update`);
  };

  const handleDeleteClick = () => {
    setOpenDialog(true); // Open the confirmation dialog
  };

  const handleConfirmDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/rack_levels/${rackLevelId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      navigate('/rack-levels'); // Navigate to the rack levels list after successful deletion
    } catch (error) {
      handleError(error, setError); // Handle deletion error
    } finally {
      setOpenDialog(false); // Close the confirmation dialog
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false); // Close the confirmation dialog without deleting
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  if (!rackLevel) {
    return <Typography variant="h6" color="error">Rack Level not found</Typography>;
  }

  const getSlotColor = (slot) => {
    if (!slot.is_active) {
      return '#b0bec5'; // Light gray for inactive slots
    }
    if (slot.is_active && !slot.stock) {
      return '#4caf50'; // Green for available slots
    }
    if (slot.is_active && slot.stock) {
      return '#f44336'; // Red for occupied slots
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <>
              <Button color="inherit" onClick={handleUpdateClick}>
                Update Rack Level
              </Button>
              <Button
                color="inherit"
                onClick={handleDeleteClick}
                sx={{ ml: 2 }}
                style={{ color: 'red' }}
              >
                Delete Rack Level
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12}>
          <Card className={`card ${themeMode}`} sx={{ padding: 3 }}>
            <CardContent>
              <Typography variant="h4" gutterBottom>
                Rack Level: {rackLevel.rack_level_number}
              </Typography>
              <Typography variant="body1">Description: {rackLevel.description}</Typography>
              <Typography variant="body1">Max Weight: {rackLevel.max_weight}</Typography>
              <Typography variant="body1">Available Weight: {rackLevel.available_weight}</Typography>
              <Typography variant="body1">Occupied Weight: {rackLevel.occupied_weight}</Typography>
              <Typography variant="body1">Max Slots: {rackLevel.max_slots}</Typography>
              <Typography variant="body1">Available Slots: {rackLevel.available_slots}</Typography>
              <Typography variant="body1">Occupied Slots: {rackLevel.occupied_slots}</Typography>
              <Typography variant="body1">Active Slots: {rackLevel.active_slots}</Typography>
              <Typography variant="body1">Inactive Slots: {rackLevel.inactive_slots}</Typography>
            </CardContent>
          </Card>

          {(isStaff || canMoveStocks) && rackLevel.rack_level_slots && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Rack Level Slots:
              </Typography>
              <Grid container spacing={2}>
                {rackLevel.rack_level_slots.map((slot, index) => (
                  <Grid item key={slot.id} xs={3} sm={2}>
                    <Card
                      sx={{
                        backgroundColor: getSlotColor(slot),
                        color: 'white',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: 100, // Set a fixed height for square shape
                        borderRadius: 2,
                        boxShadow: 3,
                        cursor: 'pointer',
                        '&:hover': {
                          opacity: 0.8,
                        },
                      }}
                      component={Link}
                      to={`/rack-level-slot/${slot.id}`} // Link to slot details
                    >
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {index + 1}
                      </Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Grid>
      </Grid>

      {/* Confirmation Dialog for Deleting Rack Level */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this rack level? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleConfirmDelete} color="secondary" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RackLevelDetail;
