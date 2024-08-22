import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { CircularProgress, Typography, Box, TextField, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler'

const CategoryDetail = ({ themeMode }) => {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [newName, setNewName] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false); // State to manage delete confirmation dialog
  const isStaff = AuthService.getUserRole(); // Directly use the boolean result

  useEffect(() => {
    const fetchCategory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/categories/${categoryId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setCategory(response.data);
        setNewName(response.data.name); // Set initial value for the text field
      }
      catch (error) {
          handleError(error, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchCategory();
  }, [categoryId]);

  const handleUpdateName = async () => {
    try {
      await axios.patch(`http://localhost:8000/api/categories/${categoryId}`, {
        name: newName
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setCategory(prevCategory => ({ ...prevCategory, name: newName }));
      setEditMode(false);
    } catch (error) {
    handleError(error, setError);
  }
  };

  const handleDeleteCategory = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/categories/${categoryId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/categories'); // Redirect to the categories list after deletion
    } catch (error) {
      handleError(error, setError);
  }
  };

  const handleOpenDeleteDialog = () => {
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
  };

  const handleConfirmDelete = () => {
    handleDeleteCategory();
    setDeleteDialogOpen(false);
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{String(error)}</Typography>;
  }

  return (
    <Box className={`category-detail ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Category Detail</Typography>
      <Typography variant="h6">Name: {category.name}</Typography>
      <Typography variant="body1">Created At: {category.created_at}</Typography>

      {isStaff && (
        <Box sx={{ mt: 2 }}>
          {editMode ? (
            <>
              <TextField
                label="New Name"
                variant="outlined"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Button variant="contained" color="primary" onClick={handleUpdateName}>
                Save
              </Button>
              <Button variant="outlined" color="secondary" onClick={() => setEditMode(false)} sx={{ ml: 2 }}>
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Button variant="contained" color="primary" onClick={() => setEditMode(true)}>
                Edit Name
              </Button>
              <Button variant="contained" color="error" onClick={handleOpenDeleteDialog} sx={{ ml: 2 }}>
                Delete Category
              </Button>
            </>
          )}
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
      >
        <DialogTitle>{"Confirm Delete"}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this category? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="secondary">
            No
          </Button>
          <Button onClick={handleConfirmDelete} color="error" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CategoryDetail;
