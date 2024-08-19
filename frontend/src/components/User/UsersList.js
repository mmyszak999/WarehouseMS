import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    Typography,
    Card,
    CardContent,
    CardHeader,
    CircularProgress,
    Grid,
    AppBar,
    Toolbar,
    Button,
    Box,
    Pagination,
    TextField,
    MenuItem,
    Select,
    InputLabel,
    FormControl,
    Divider
} from '@mui/material';
import { Link } from 'react-router-dom';
import AuthService from '../../services/AuthService';
import '../../App.css';
import { format } from 'date-fns';  // Importing date-fns for date formatting

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

const UsersList = ({ themeMode }) => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);
    const [filters, setFilters] = useState({
        first_name: { value: '', operator: 'eq', sort: '' },
        last_name: { value: '', operator: 'eq', sort: '' },
        employment_date: { value: '', operator: 'eq', sort: '' }
    });

    const [isStaff, setIsStaff] = useState(false);

    useEffect(() => {
        const fetchUserRole = () => {
            setIsStaff(AuthService.getUserRole());
        };

        fetchUserRole();
    }, []);

    const fetchUsers = async (page, size, appliedFilters) => {
        try {
            setLoading(true);
            let endpoint = `http://localhost:8000/api/users?page=${page}&size=${size}`;

            for (const [key, filter] of Object.entries(appliedFilters)) {
                if (filter.value) {
                    if (key === 'employment_date') {
                        // Format the date value to match the backend's expected format
                        const formattedDate = format(new Date(filter.value), 'yyyy-MM-dd');
                        endpoint += `&${key}__${filter.operator}=${formattedDate}`;
                    } else {
                        endpoint += `&${key}__${filter.operator}=${filter.value}`;
                    }
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
            setUsers(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
        } catch (error) {
            setError('Error fetching users');
            console.error('Error fetching users:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers(page, size, filters);
    }, [page, size]);  // Now only fetches on page or size change

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
        // This will only be called when the user clicks the "Apply Filters" button
        setPage(1);  // Reset to first page when applying new filters
        fetchUsers(1, size, filters);
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    const renderUserCard = (user) => {
        const userInfo = isStaff ? {
            ...user, 
            is_staff: user.is_staff ? 'Yes' : 'No', 
            has_password_set: user.has_password_set ? 'Yes' : 'No'
        } : {
            first_name: user.first_name,
            last_name: user.last_name,
            employment_date: user.employment_date,
            is_active: user.is_active ? 'Active' : 'Inactive'
        };

        return (
            <Card className={`card ${themeMode}`} key={user.id}>
                <CardHeader
                    title={
                        <Link to={`/user/${user.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Typography variant="h6" fontWeight="bold">
                                {userInfo.first_name} {userInfo.last_name}
                            </Typography>
                        </Link>
                    }
                />
                <CardContent>
                    <Typography variant="body2" fontFamily="Arial, sans-serif">Employment Date: {userInfo.employment_date}</Typography>
                    {isStaff && (
                        <>
                            <Typography variant="body2" fontFamily="Arial, sans-serif">Staff: {userInfo.is_staff}</Typography>
                            <Typography variant="body2" fontFamily="Arial, sans-serif">Password Set: {userInfo.has_password_set}</Typography>
                        </>
                    )}
                    {!isStaff && (
                        <Typography variant="body2" fontFamily="Arial, sans-serif">Status: {userInfo.is_active}</Typography>
                    )}
                </CardContent>
            </Card>
        );
    };

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static" className={`app-bar ${themeMode}`}>
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {isStaff && (
                        <Button color="inherit" component={Link} to="/user/create">Create User</Button>
                    )}
                </Toolbar>
            </AppBar>
            <Grid container spacing={3} sx={{ mt: 3 }}>
                <Grid item xs={12} md={4}>
                    <Box sx={{ padding: 2, borderRight: '1px solid #ddd' }}>
                        <Typography variant="h6" gutterBottom>Filters</Typography>
                        <Divider sx={{ mb: 2 }} />

                        {/* Filter Inputs */}
                        {Object.entries(filters).map(([key, filter]) => (
                            (isStaff || key !== 'is_staff') && (
                                <Box key={key} sx={{ mb: 3 }}>
                                    <Typography variant="subtitle1" gutterBottom>
                                        <strong>{key.replace(/_/g, ' ')}</strong>
                                    </Typography>
                                    <Grid container spacing={2}>
                                        {/* Value Input */}
                                        <Grid item xs={12} md={12}>
                                            {key === 'employment_date' ? (
                                                <TextField
                                                    type="date"
                                                    label={key.replace(/_/g, ' ')}
                                                    name={`${key}.value`}
                                                    value={filter.value}
                                                    onChange={handleFilterChange}
                                                    fullWidth
                                                    InputLabelProps={{
                                                        shrink: true,
                                                    }}
                                                />
                                            ) : (
                                                <TextField
                                                    label={key.replace(/_/g, ' ')}
                                                    name={`${key}.value`}
                                                    value={filter.value}
                                                    onChange={handleFilterChange}
                                                    fullWidth
                                                />
                                            )}
                                        </Grid>
                                        {/* Operator Select */}
                                        <Grid item xs={12} md={12}>
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
                                        <Grid item xs={12} md={12}>
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
                            )
                        ))}
                        {isStaff && (
                            <Box sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    <strong>Staff Filter</strong>
                                </Typography>
                                <FormControl fullWidth>
                                    <InputLabel>Is Staff</InputLabel>
                                    <Select
                                        name="is_staff.value"
                                        value={filters.is_staff?.value || ''}
                                        onChange={handleFilterChange}
                                        label="Is Staff"
                                    >
                                        <MenuItem value="">No Filter</MenuItem>
                                        <MenuItem value="true">Yes</MenuItem>
                                        <MenuItem value="false">No</MenuItem>
                                    </Select>
                                </FormControl>
                            </Box>
                        )}
                        {isStaff && (
                            <Button variant="contained" color="primary" onClick={handleFilterApply}>
                                Apply Filters
                            </Button>
                        )}
                    </Box>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Grid container spacing={3}>
                        {users.map(user => (
                            <Grid item xs={12} key={user.id}>
                                {renderUserCard(user)}
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

export default UsersList;
