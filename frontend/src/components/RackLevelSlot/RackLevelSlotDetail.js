import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  CircularProgress, Typography, Grid, Card, CardContent, Box, AppBar, Toolbar, Button
} from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler'; // Error handling

const RackLevelSlotDetail = ({ themeMode }) => {
  const { rackLevelSlotId } = useParams();
  const navigate = useNavigate();
  const [rackLevelSlot, setRackLevelSlot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isStaff = AuthService.getUserRole();
  const canMoveStocks = AuthService.canMoveStocks();

  const fetchRackLevelSlotDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setRackLevelSlot(response.data);
    } catch (error) {
      handleError(error, setError); // Handle errors
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRackLevelSlotDetails();
  }, [rackLevelSlotId]);

  const handleActivateDeactivate = async () => {
    const url = rackLevelSlot.is_active
      ? `http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}/deactivate`
      : `http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}/activate`;

    try {
      await axios.patch(url, {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      // Refresh the slot details after activation/deactivation
      fetchRackLevelSlotDetails();
    } catch (error) {
      handleError(error, setError); // Handle errors
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  if (!rackLevelSlot) {
    return <Typography variant="h6" color="error">Rack Level Slot not found</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <Button
              color="inherit"
              onClick={() => navigate(`/rack-level-slot/${rackLevelSlotId}/update`)}
            >
              Update Rack Level Slot
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12}>
          <Card className={`card ${themeMode}`} sx={{ padding: 3 }}>
            <CardContent>
              <Typography variant="h4" gutterBottom>
                {rackLevelSlot.description}
              </Typography>
              <Typography variant="body1">Slot number in the rack level: {rackLevelSlot.rack_level_slot_number}</Typography>
              <Typography variant="body1">Active: {rackLevelSlot.is_active ? 'Yes' : 'No'}</Typography>
              <Typography variant="body1">Created At: {new Date(rackLevelSlot.created_at).toLocaleDateString()}</Typography>

              {/* Activate/Deactivate Button */}
              {isStaff && (
                <Button
                  variant="contained"
                  color={rackLevelSlot.is_active ? 'error' : 'success'}
                  onClick={handleActivateDeactivate}
                  sx={{ mb: 2 }}
                >
                  {rackLevelSlot.is_active ? 'Deactivate' : 'Activate'}
                </Button>
              )}

              {/* Stock Information */}
              {rackLevelSlot.stock && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Stock Information:
                  </Typography>
                  <Typography variant="body1">Product Name: {rackLevelSlot.stock.product.name}</Typography>
                  <Typography variant="body1">Product Description: {rackLevelSlot.stock.product.description}</Typography>
                  <Typography variant="body1">Weight: {rackLevelSlot.stock.weight}</Typography>
                  <Typography variant="body1">Product Count: {rackLevelSlot.stock.product_count}</Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RackLevelSlotDetail;
