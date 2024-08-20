import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Typography,
    Card,
    CardContent,
    CircularProgress,
    Box,
    AppBar,
    Toolbar,
    Button,
    TextField,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle
} from '@mui/material';
import AuthService from '../../services/AuthService';
import '../../App.css';

const UserDetail = ({ themeMode }) => {
    const { userId } = useParams();
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isStaff, setIsStaff] = useState(false);
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        employment_date: '',
        birth_date: '',
        is_staff: false,
        can_move_stocks: false,
        can_recept_stocks: false,
        can_issue_stocks: false
    });

    useEffect(() => {
        const fetchUserRole = () => {
            setIsStaff(AuthService.getUserRole());
        };

        fetchUserRole();
    }, []);

    useEffect(() => {
        const fetchUserDetails = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/users/${userId}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setUser(response.data);
                setFormData({
                    first_name: response.data.first_name,
                    last_name: response.data.last_name,
                    employment_date: response.data.employment_date,
                    birth_date: response.data.birth_date,
                    is_staff: response.data.is_staff,
                    can_move_stocks: response.data.can_move_stocks,
                    can_recept_stocks: response.data.can_recept_stocks,
                    can_issue_stocks: response.data.can_issue_stocks
                });
            } catch (error) {
                if (error.response) {
                    switch (error.response.status) {
                        case 422:
                            const schema_error = JSON.parse(error.request.response)
                            setError('Validation Error: ' + (schema_error.detail[0]?.msg || 'Invalid input'));
                            break;
                        case 500:
                            setError('Server Error: Please try again later');
                            break;
                        case 401:
                            setError('Error: ' + (error.response.statusText || 'You were logged out! '));
                            break;
                        default:
                            const default_error = JSON.parse(error.request.response)
                            setError('Error: ' + (default_error.detail || 'An unexpected error occurred'));
                            break;
                    }
                } else if (error.request) {
                    // Handle network errors
                    setError('Network Error: No response received from server');
                } else {
                    // Handle other errors
                    setError('Error: ' + error.message);
                }
                console.error('Error fetching users:', error);
            }
            finally {
                setLoading(false);
            }
        };

        fetchUserDetails();
    }, [userId]);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.patch(`http://localhost:8000/api/users/${userId}`, formData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            handleClose();
            setUser(prevUser => ({
                ...prevUser,
                ...formData
            }));
        } catch (error) {
            if (error.response) {
                switch (error.response.status) {
                    case 422:
                        const schema_error = JSON.parse(error.request.response)
                        setError('Validation Error: ' + (schema_error.detail[0]?.msg || 'Invalid input'));
                        break;
                    case 500:
                        setError('Server Error: Please try again later');
                        break;
                    case 401:
                        setError('Error: ' + (error.response.statusText || 'You were logged out! '));
                        break;
                    default:
                        const default_error = JSON.parse(error.request.response)
                        setError('Error: ' + (default_error.detail || 'An unexpected error occurred'));
                        break;
                }
            } else if (error.request) {
                // Handle network errors
                setError('Network Error: No response received from server');
            } else {
                // Handle other errors
                setError('Error: ' + error.message);
            }
            console.error('Error fetching users:', error);
        }
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static" className={`app-bar ${themeMode}`}>
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {isStaff && (
                        <Button color="inherit" onClick={handleClickOpen}>
                            Update User
                        </Button>
                    )}
                </Toolbar>
            </AppBar>
            <Card className={`card ${themeMode}`} sx={{ mt: 3 }}>
                <CardContent>
                    <Typography variant="h5" fontWeight="bold">{user.first_name} {user.last_name}</Typography>
                    <Typography variant="body2">Employment Date: {user.employment_date}</Typography>
                    {isStaff ? (
                        <>
                            <Typography variant="body2">Email: {user.email}</Typography>
                            <Typography variant="body2">Birth Date: {user.birth_date}</Typography>
                            <Typography variant="body2">Staff: {user.is_staff ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Can Move Stocks: {user.can_move_stocks ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Can Recept Stocks: {user.can_recept_stocks ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Can Issue Stocks: {user.can_issue_stocks ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Superuser: {user.is_superuser ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Password Set: {user.has_password_set ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Created At: {user.created_at}</Typography>
                        </>
                    ) : (
                        <Typography variant="body2">Active: {user.is_active ? 'Yes' : 'No'}</Typography>
                    )}
                </CardContent>
            </Card>
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Update User</DialogTitle>
                <DialogContent>
                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                        <TextField
                            label="First Name"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleInputChange}
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Last Name"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleInputChange}
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Employment Date"
                            name="employment_date"
                            type="date"
                            value={formData.employment_date}
                            onChange={handleInputChange}
                            fullWidth
                            margin="normal"
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                        <TextField
                            label="Birth Date"
                            name="birth_date"
                            type="date"
                            value={formData.birth_date}
                            onChange={handleInputChange}
                            fullWidth
                            margin="normal"
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                        <TextField
                            label="Can Move Stocks"
                            name="can_move_stocks"
                            type="checkbox"
                            checked={formData.can_move_stocks}
                            onChange={handleInputChange}
                        />
                        <TextField
                            label="Can Recept Stocks"
                            name="can_recept_stocks"
                            type="checkbox"
                            checked={formData.can_recept_stocks}
                            onChange={handleInputChange}
                        />
                        <TextField
                            label="Can Issue Stocks"
                            name="can_issue_stocks"
                            type="checkbox"
                            checked={formData.can_issue_stocks}
                            onChange={handleInputChange}
                        />
                        <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                            Update User
                        </Button>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default UserDetail;
