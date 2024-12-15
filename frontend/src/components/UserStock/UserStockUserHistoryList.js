import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, FormControl, Select, MenuItem, InputLabel } from '@mui/material';
import { Link, useNavigate, useParams } from 'react-router-dom';
import '../../App.css';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const UserStockUserHistoryList = ({ themeMode }) => {
    const { userId } = useParams();
    const [userStocks, setUserStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);

    const navigate = useNavigate();

    const fetchUserStocks = async (page, size) => {
        try {
            setLoading(true);
            const response = await axios.get(`http://localhost:8000/api/users/${userId}/history?page=${page}&size=${size}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            setUserStocks(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
        } catch (error) {
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUserStocks(page, size);
    }, [page, size]);

    const handlePageChange = (event, value) => {
        setPage(value);
    };

    const handleSizeChange = (event) => {
        setSize(event.target.value);
        setPage(1);
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
                </Toolbar>
            </AppBar>
            <Grid container spacing={3} sx={{ mt: 3 }}>
                <Grid item xs={12}>
                    <Grid container spacing={3}>
                        {userStocks.map(userStock => (
                            <Grid item xs={12} key={userStock.id}>
                                <Card className={`card ${themeMode}`}>
                                    <CardContent onClick={() => navigate(`/user-stock/${userStock.id}`)}>
                                        <Typography variant="h6" fontWeight="bold">
                                            Stock ID: {userStock.stock.id}
                                        </Typography>
                                        <Typography variant="body1">
                                            Product: {userStock.stock.product.name}
                                        </Typography>
                                        <Typography variant="body1">
                                            Managed By: {userStock.user.first_name} {userStock.user.last_name}
                                        </Typography>
                                        <Typography variant="body1">
                                            Moved At: {new Date(userStock.moved_at).toLocaleDateString()}
                                        </Typography>
                                        <Typography variant="body2">Waiting Room: {userStock.stock.waiting_room?.name || 'N/A'}</Typography>
                                        <Typography variant="body2">Rack Slot: {userStock.stock.rack_level_slot?.description || 'N/A'}</Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                        <FormControl sx={{ minWidth: 120 }}>
                            <InputLabel>Items per page</InputLabel>
                            <Select
                                value={size}
                                onChange={handleSizeChange}
                                label="Items per page"
                            >
                                {pageSizeOptions.map(option => (
                                    <MenuItem key={option} value={option}>
                                        {option}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        <Pagination
                            count={totalPages}
                            page={page}
                            onChange={handlePageChange}
                            color="primary"
                        />
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default UserStockUserHistoryList;
