import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CircularProgress, Typography, Card, CardContent, CardHeader, Grid, AppBar, Toolbar, Button, Box, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { handleError } from '../ErrorHandler';
import AuthService from '../../services/AuthService';

const SectionDetail = ({ themeMode }) => {
  const { sectionId } = useParams();
  const navigate = useNavigate();
  const [section, setSection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const isStaff = AuthService.getUserRole();
  const canMoveStocks = AuthService.canMoveStocks();

  const fetchSection = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setSection(response.data);
    } catch (error) {
      handleError(error, setError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSection();
  }, [sectionId]);

  const handleUpdateClick = () => {
    navigate(`/section/${sectionId}/update`);
  };

  const handleDeleteClick = () => {
    setOpenDialog(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/sections/${sectionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/');
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

  if (!section) {
    return <Typography variant="h6" color="error">Section not found</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <>
              <Button color="inherit" onClick={handleUpdateClick}>Update Section</Button>
              <Button color="inherit" onClick={handleDeleteClick} sx={{ ml: 2 }} style={{ color: 'red' }}>
                Delete Section
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12}>
          <Card className={`card ${themeMode}`}>
            <CardHeader
              title={<Typography variant="h6" fontWeight="bold">{section.section_name}</Typography>}
            />
            <CardContent>
              <Typography variant="body1">Max Weight: {section.max_weight}</Typography>
              <Typography variant="body1">Max Racks: {section.max_racks}</Typography>
              <Typography variant="body1">Available Weight: {section.available_weight}</Typography>
              <Typography variant="body1">Occupied Weight: {section.occupied_weight}</Typography>
              <Typography variant="body1">Reserved Weight: {section.reserved_weight}</Typography>
              <Typography variant="body1">Weight to Reserve: {section.weight_to_reserve}</Typography>
              <Typography variant="body1">Available Racks: {section.available_racks}</Typography>
              <Typography variant="body1">Occupied Racks: {section.occupied_racks}</Typography>
              <Typography variant="body2">Created At: {section.created_at || 'N/A'}</Typography>

              {section.racks && section.racks.length > 0 && (isStaff || canMoveStocks) && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Racks:</Typography>
                  {section.racks.map(rack => (
                    <Card key={rack.id} sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="body1">
                          <Link to={`/rack/${rack.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                            Rack Name: {rack.rack_name}
                          </Link>
                        </Typography>
                        <Typography variant="body1">Max Weight: {rack.max_weight}</Typography>
                        <Typography variant="body1">Available Weight: {rack.available_weight}</Typography>
                        <Typography variant="body1">Occupied Weight: {rack.occupied_weight}</Typography>
                        <Typography variant="body1">Available Levels: {rack.available_levels}</Typography>
                        <Typography variant="body1">Occupied Levels: {rack.occupied_levels}</Typography>
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
            Are you sure you want to delete this section? This action cannot be undone.
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

export default SectionDetail;
