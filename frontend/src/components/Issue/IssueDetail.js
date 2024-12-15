import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { CircularProgress, Typography, AppBar, Toolbar, Button, Box, List, ListItem, ListItemText, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from '@mui/material';
import axios from 'axios';
import { format } from 'date-fns';
import { handleError } from '../ErrorHandler';
import AuthService from '../../services/AuthService';

const IssueDetail = ({ themeMode }) => {
  const { issueId } = useParams();
  const navigate = useNavigate();
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);
  const [description, setDescription] = useState('');
  const [isStaff, setIsStaff] = useState(false);

  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchUserRole = () => {
      setIsStaff(AuthService.getUserRole());
    };

    fetchUserRole();
  }, []);

  useEffect(() => {
    const fetchIssue = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/api/issues/${issueId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setIssue(response.data);
        setDescription(response.data.description || '');
      } catch (err) {
        handleError(err, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchIssue();
  }, [issueId, token]);

  const handleUpdateClick = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleUpdate = async () => {
    try {
      await axios.patch(`http://localhost:8000/api/issues/${issueId}`, {
        description
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const response = await axios.get(`http://localhost:8000/api/issues/${issueId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setIssue(response.data);
      setOpen(false);
    } catch (err) {
      handleError(err, setError);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">Error: {error}</Typography>;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" sx={{ ml: 2 }} onClick={handleUpdateClick}>
            Update Issue
          </Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ padding: 2 }}>
        <Typography variant="h6">Issue ID: {issue.id}</Typography>
        <Typography variant="body1">Description: {issue.description || 'N/A'}</Typography>
        <Typography variant="body1">
          Issue Date: {format(new Date(issue.issue_date), 'yyyy-MM-dd')}
        </Typography>
        <Typography variant="body1">
          Created By: {issue.user.first_name} {issue.user.last_name}
        </Typography>

        <Typography variant="h6" sx={{ mt: 2 }}>Stocks:</Typography>
        <List>
          {issue.stocks.map((stock) => (
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
            </ListItem>
          ))}
        </List>
      </Box>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Update Issue</DialogTitle>
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

export default IssueDetail;
