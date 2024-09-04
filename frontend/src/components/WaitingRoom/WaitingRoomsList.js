import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, TextField, MenuItem, Select, InputLabel, FormControl, Divider } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import '../../App.css'; // Import your CSS file
import AuthService from '../../services/AuthService'; // Import the AuthService for role checking
import { debounce } from 'lodash';

const operatorOptions = [
    { value: 'eq', label: 'Equals (=)' },
    { value: 'ne', label: 'Not Equals (!=)' },
    { value: 'gt', label: 'Greater Than (>)' },
    { value: 'lt', label: 'Less Than (<)' },
    { value: 'ge', label: 'Greater or Equal (>=)' },
    { value: 'le', label: 'Less or Equal (<=)' }
];

const sortOptions = [
    { value: '', label: 'No Sort' },
    { value: 'asc', label: 'Ascending' },
    { value: 'desc', label: 'Descending' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const WaitingRoomsList = ({ themeMode }) => {
    const [waitingRooms, setWaitingRooms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);
    const [filters, setFilters] = useState({
        occupied_slots: { value: '', operator: 'eq', sort: '' },
        current_stock_weight: { value: '', operator: 'eq', sort: '' },
        available_slots: { value: '', operator: 'eq', sort: '' },
        available_stock_weight: { value: '', operator: 'eq', sort: '' },
        max_stocks: { value: '', operator: 'eq', sort: '' },
        max_weight: { value: '', operator: 'eq', sort: '' },
    });

    const navigate = useNavigate();
    const userRole = AuthService.getUserRole(); // Get the user's role

    const fetchWaitingRooms = async (page, size, appliedFilters) => {
        try {
            setLoading(true);
            let endpoint = `http://localhost:8000/api/waiting_rooms/?page=${page}&size=${size}`;

            // Append filter and sort params
            for (const [key, filter] of Object.entries(appliedFilters)) {
                if (filter.value) {
                    endpoint += `&${key}__${filter.operator}=${filter.value}`;
                }
                if (filter.sort) {
                    endpoint += `&sort=${key}__${filter.sort}`;
                }
            }

            const response = await axios.get(endpoint, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            setWaitingRooms(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchWaitingRooms(page, size, filters);
    }, [page, size]);

    const handlePageChange = (event, value) => {
        setPage(value);
    };

    const handleSizeChange = (event) => {
        setSize(event.target.value);
        setPage(1); // Reset to first page whenever size changes
    };

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        const [field, type] = name.split('.');
        setFilters(prevFilters => ({
            ...prevFilters,
            [field]: { ...prevFilters[field], [type]: value }
        }));
    };

    const handleFilterApply = () => {
        fetchWaitingRooms(page, size, filters);
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
                    {userRole && (
                        <Button color="inherit" component={Link} to="/waiting_room/create">
                        Create Waiting Room
                        </Button>
                    )}
                </Toolbar>
            </AppBar>
            <Grid container spacing={3} sx={{ mt: 3 }}>
                {/* Filters Section */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ padding: 2, borderRight: '1px solid #ddd' }}>
                        <Typography variant="h6" gutterBottom>Filters</Typography>
                        <Divider sx={{ mb: 2 }} />

                        {Object.entries(filters).map(([key, filter]) => (
                            <Box key={key} sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    <strong>{key.replace(/_/g, ' ')}</strong>
                                </Typography>
                                <Grid container spacing={2}>
                                    {/* Value Input */}
                                    <Grid item xs={12}>
                                        <TextField
                                            label={key.replace(/_/g, ' ')}
                                            name={`${key}.value`}
                                            value={filter.value}
                                            onChange={handleFilterChange}
                                            fullWidth
                                        />
                                    </Grid>
                                    {/* Operator Select */}
                                    <Grid item xs={12}>
                                        <FormControl fullWidth>
                                            <InputLabel>Operator</InputLabel>
                                            <Select
                                                name={`${key}.operator`}
                                                value={filter.operator}
                                                onChange={handleFilterChange}
                                                label="Operator"
                                            >
                                                {operatorOptions.map(option => (
                                                    <MenuItem key={option.value} value={option.value}>
                                                        {option.label}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                    </Grid>
                                    {/* Sort By Select */}
                                    <Grid item xs={12}>
                                        <FormControl fullWidth>
                                            <InputLabel>Sort By</InputLabel>
                                            <Select
                                                name={`${key}.sort`}
                                                value={filter.sort}
                                                onChange={handleFilterChange}
                                                label="Sort By"
                                            >
                                                {sortOptions.map(option => (
                                                    <MenuItem key={option.value} value={option.value}>
                                                        {option.label}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                    </Grid>
                                </Grid>
                            </Box>
                        ))}
                        <Button variant="contained" color="primary" onClick={handleFilterApply}>
                            Apply Filters
                        </Button>
                    </Box>
                </Grid>

                {/* Waiting Rooms List Section */}
                <Grid item xs={12} md={8}>
                    <Grid container spacing={3}>
                        {waitingRooms.map(waitingRoom => (
                            <Grid item xs={12} key={waitingRoom.id}>
                                <Card className={`card ${themeMode}`}>
                                    <CardHeader
                                        title={
                                            <Typography 
                                                variant="h6" 
                                                fontWeight="bold"
                                                component={Link} 
                                                to={`/waiting_room/${waitingRoom.id}`} // Link to the detailed page
                                                style={{ textDecoration: 'none', color: 'inherit' }} // Style to maintain theme
                                            >
                                                {waitingRoom.name || 'Unnamed Room'}
                                            </Typography>
                                        }
                                    />
                                    <CardContent onClick={() => navigate(`/waiting_room/${waitingRoom.id}`)}> {/* Navigate on click */}
                                        <Typography variant="body1">Max Stocks: {waitingRoom.max_stocks}</Typography>
                                        <Typography variant="body1">Max Weight: {waitingRoom.max_weight}</Typography>
                                        <Typography variant="body1">Occupied Slots: {waitingRoom.occupied_slots}</Typography>
                                        <Typography variant="body1">Current Stock Weight: {waitingRoom.current_stock_weight}</Typography>
                                        <Typography variant="body1">Available Slots: {waitingRoom.available_slots}</Typography>
                                        <Typography variant="body1">Available Stock Weight: {waitingRoom.available_stock_weight}</Typography>
                                        <Typography variant="body2">Created At: {waitingRoom.created_at || 'N/A'}</Typography>
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

export default WaitingRoomsList;
