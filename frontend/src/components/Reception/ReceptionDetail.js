import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { CircularProgress, Typography, AppBar, Toolbar, Button, Box, List, ListItem, ListItemText, TextField, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import axios from 'axios';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const ReceptionDetail = ({ themeMode }) => {
  const { receptionId } = useParams();
  const navigate = useNavigate();
  const [reception, setReception] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);
  const [description, setDescription] = useState('');

  const token = localStorage.getItem('token');
  const canReceptStocks = AuthService.canReceptStocks();
  const isStaff = AuthService.getUserRole(); // Check if the user is a staff member

  useEffect(() => {
    const fetchReceptionDetails = async () => {
      if (!canReceptStocks) {
        navigate('/');  // Redirect if the user doesn't have permission
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/api/receptions/${receptionId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        console.log(response.data, "xxx1")
        setReception(response.data);
        setDescription(response.data.description || '');
      } catch (err) {
        handleError(err, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchReceptionDetails();
  }, [receptionId, token, canReceptStocks, navigate]);

  const handleUpdateClick = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleUpdate = async () => {
    try {
      await axios.patch(`http://localhost:8000/api/receptions/${receptionId}`, {
        description
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      // Refetch reception details after update
      const response = await axios.get(`http://localhost:8000/api/receptions/${receptionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setReception(response.data);
      setOpen(false);
    } catch (err) {
      handleError(err, setError);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button 
            color="inherit" 
            sx={{ ml: 2 }}
            onClick={handleUpdateClick}
          >
            Update Reception
          </Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ padding: 2 }}>
        <Typography variant="h6">Reception ID: {reception.id}</Typography>
        <Typography variant="body1">Description: {reception.description || 'N/A'}</Typography>
        <Typography variant="body1">
          Reception Date: {new Date(reception.reception_date).toLocaleDateString()}
        </Typography>
        <Typography variant="body1">Created By: {reception.user.first_name} {reception.user.last_name}</Typography>

        <Typography variant="h6" sx={{ mt: 2 }}>Stocks:</Typography>
        <List>
          {reception.stocks.map((stock) => (
            <ListItem key={stock.id}>
              <ListItemText
                primary={
                  <Link 
                    to={isStaff ? `/stock/all/${stock.id}` : `/stock/${stock.id}`} 
                    style={{ textDecoration: 'none', color: 'inherit' }}
                  >
                    Stock: {stock.product.name}
                  </Link>
                }
                secondary={`Weight: ${stock.weight}, Product Count: ${stock.product_count}`}
              />
              
              {/* Link do Waiting Room, jeśli istnieje waiting_room_id */}
              {stock.waiting_room_id && (
                <Button 
                  component={Link} 
                  to={`/waiting_room/${stock.waiting_room_id}`} 
                  sx={{ ml: 2 }} 
                  variant="contained" 
                  color="primary"
                >
                  View Waiting Room
                </Button>
              )}
              
              {stock.rack_level_slot_id ? (
                <Button 
                  component={Link} 
                  to={`/rack-level-slot/${stock.rack_level_slot_id}`} 
                  sx={{ ml: 2 }} 
                  variant="contained" 
                  color="secondary"
                >
                  View Rack Level Slot
                </Button>
              ) : null}
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Update Dialog */}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Update Reception</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Description"
            fullWidth
            variant="standard"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleUpdate}>Update</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ReceptionDetail;
