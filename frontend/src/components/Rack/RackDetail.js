import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CircularProgress, Typography, Card, CardContent, CardHeader, Grid, AppBar, Toolbar, Button, Box, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { handleError } from '../ErrorHandler'; 
import AuthService from '../../services/AuthService';

const RackDetail = ({ themeMode }) => {
  const { rackId } = useParams();
  const navigate = useNavigate();
  const [rack, setRack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const isStaff = AuthService.getUserRole(); 
  const canMoveStocks = AuthService.canMoveStocks();

  const fetchRackDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/racks/${rackId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setRack(response.data);
    } catch (error) {
      handleError(error, setError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRackDetails();
  }, [rackId]);

  const handleUpdateClick = () => {
    navigate(`/rack/${rackId}/update`); 
  };

  const handleDeleteClick = () => {
    setOpenDialog(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/racks/${rackId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/racks');
    } catch (error) {
      handleError(error, setError);
    } finally {
      setOpenDialog(false);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  if (!rack) {
    return <Typography variant="h6" color="error">Rack not found</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <>
              <Button color="inherit" onClick={handleUpdateClick}>Update Rack</Button>
              <Button color="inherit" onClick={handleDeleteClick} sx={{ ml: 2 }} style={{ color: 'red' }}>
                Delete Rack
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12}>
          <Card className={`card ${themeMode}`}>
            <CardHeader
              title={<Typography variant="h6" fontWeight="bold">{rack.rack_name}</Typography>}
            />
            <CardContent>
              <Typography variant="body1">Max Weight: {rack.max_weight}</Typography>
              <Typography variant="body1">Available Weight: {rack.available_weight}</Typography>
              <Typography variant="body1">Occupied Weight: {rack.occupied_weight}</Typography>
              <Typography variant="body1">Max Levels: {rack.max_levels}</Typography>
              <Typography variant="body1">Available Levels: {rack.available_levels}</Typography>
              <Typography variant="body1">Occupied Levels: {rack.occupied_levels}</Typography>
              <Typography variant="body1">Reserved Weight: {rack.reserved_weight}</Typography>
              <Typography variant="body1">Weight to Reserve: {rack.weight_to_reserve}</Typography>
              <Typography variant="body2">Created At: {rack.created_at || 'N/A'}</Typography>
              {(isStaff || canMoveStocks) && rack.rack_levels && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Rack Levels:</Typography>
                  {rack.rack_levels.map(rack_level => (
                    <Card key={rack_level.id} sx={{ mb: 2 }}>
                      <CardContent>
                      <Typography variant="body1">
                          <Link to={`/rack-level/${rack_level.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                            Rack Level Description: {rack_level.description}
                          </Link>
                        </Typography>
                        <Typography variant="body1">Rack Level Number: {rack_level.rack_level_number}</Typography>
                        <Typography variant="body1">Max Weight: {rack_level.max_weight}</Typography>
                        <Typography variant="body1">Available Weight: {rack_level.available_weight}</Typography>
                        <Typography variant="body1">Occupied Weight: {rack_level.occupied_weight}</Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this rack? This action cannot be undone.
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

export default RackDetail;
