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
import { format } from 'date-fns';
import { handleError } from '../ErrorHandler';

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

const booleanOptions = [
    { value: '', label: 'No Filter' },
    { value: 'true', label: 'Yes' },
    { value: 'false', label: 'No' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const AllUsersList = ({ themeMode }) => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);

    // State to manage filter input values
    const [filterInputs, setFilterInputs] = useState({
        first_name: { value: '', operator: 'eq', sort: '' },
        last_name: { value: '', operator: 'eq', sort: '' },
        email: { value: '', operator: 'eq', sort: '' },
        employment_date: { value: '', operator: 'eq', sort: '' },
        birth_date: { value: '', operator: 'eq', sort: '' },
        can_move_stocks: { value: '' },
        can_recept_stocks: { value: '' },
        can_issue_stocks: { value: '' },
        is_active: { value: '' }
    });

    // State to manage the applied filters
    const [filters, setFilters] = useState({
        first_name: { value: '', operator: 'eq', sort: '' },
        last_name: { value: '', operator: 'eq', sort: '' },
        email: { value: '', operator: 'eq', sort: '' },
        employment_date: { value: '', operator: 'eq', sort: '' },
        birth_date: { value: '', operator: 'eq', sort: '' },
        can_move_stocks: { value: '' },
        can_recept_stocks: { value: '' },
        can_issue_stocks: { value: '' },
        is_active: { value: '' }
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
            let endpoint = `http://localhost:8000/api/users/all?page=${page}&size=${size}`;

            for (const [key, filter] of Object.entries(appliedFilters)) {
                if (filter.value) {
                    if (key === 'employment_date' || key === 'birth_date') {
                        const formattedDate = format(new Date(filter.value), 'yyyy-MM-dd');
                        endpoint += `&${key}__${filter.operator}=${formattedDate}`;
                    } else if (key === 'can_move_stocks' || key === 'can_recept_stocks' || key === 'can_issue_stocks' || key === 'is_active') {
                        endpoint += `&${key}=${filter.value}`;
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
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers(page, size, filters);
    }, [page, size, filters]);

    const handlePageChange = (event, value) => {
        setPage(value);
    };

    const handleSizeChange = (event) => {
        setSize(event.target.value);
        setPage(1);
    };

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        const [field, type] = name.split('.');
        setFilterInputs(prevInputs => ({
            ...prevInputs,
            [field]: { ...prevInputs[field], [type]: value }
        }));
    };

    const handleFilterApply = () => {
        setFilters(filterInputs);
        setPage(1);
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

                        {Object.entries(filterInputs).map(([key, filter]) => (
                            (isStaff || key !== 'is_staff') && (
                                <Box key={key} sx={{ mb: 3 }}>
                                    <Typography variant="subtitle1" gutterBottom>
                                        <strong>{key.replace(/_/g, ' ')}</strong>
                                    </Typography>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} md={12}>
                                            {key === 'employment_date' || key === 'birth_date' ? (
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
                                            ) : key.startsWith('can_') || key === 'is_active' ? (
                                                <FormControl fullWidth>
                                                    <InputLabel>{key.replace(/_/g, ' ')}</InputLabel>
                                                    <Select
                                                        name={`${key}.value`}
                                                        value={filter.value}
                                                        onChange={handleFilterChange}
                                                        fullWidth
                                                    >
                                                        {booleanOptions.map((option) => (
                                                            <MenuItem key={option.value} value={option.value}>
                                                                {option.label}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
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
                                        {!key.startsWith('can_') && key !== 'is_active' && (
                                            <>
                                                <Grid item xs={12} md={12}>
                                                    <FormControl fullWidth>
                                                        <InputLabel>Operator</InputLabel>
                                                        <Select
                                                            name={`${key}.operator`}
                                                            value={filter.operator}
                                                            onChange={handleFilterChange}
                                                            fullWidth
                                                        >
                                                            {operatorOptions.map((option) => (
                                                                <MenuItem key={option.value} value={option.value}>
                                                                    {option.label}
                                                                </MenuItem>
                                                            ))}
                                                        </Select>
                                                    </FormControl>
                                                </Grid>
                                                <Grid item xs={12} md={12}>
                                                    <FormControl fullWidth>
                                                        <InputLabel>Sort Order</InputLabel>
                                                        <Select
                                                            name={`${key}.sort`}
                                                            value={filter.sort}
                                                            onChange={handleFilterChange}
                                                            fullWidth
                                                        >
                                                            {sortOptions.map((option) => (
                                                                <MenuItem key={option.value} value={option.value}>
                                                                    {option.label}
                                                                </MenuItem>
                                                            ))}
                                                        </Select>
                                                    </FormControl>
                                                </Grid>
                                            </>
                                        )}
                                    </Grid>
                                </Box>
                            )
                        ))}
                        <Button variant="contained" onClick={handleFilterApply} fullWidth>Apply Filters</Button>
                    </Box>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Typography variant="h6" gutterBottom>
                        Users
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Box>
                        {users.map(renderUserCard)}
                    </Box>
                    <Box sx={{ mt: 3 }}>
                        <FormControl fullWidth>
                            <InputLabel>Page Size</InputLabel>
                            <Select value={size} onChange={handleSizeChange}>
                                {pageSizeOptions.map((option) => (
                                    <MenuItem key={option} value={option}>
                                        {option}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Box>
                    <Box sx={{ mt: 2 }}>
                        <Pagination
                            count={totalPages}
                            page={page}
                            onChange={handlePageChange}
                            color="primary"
                            sx={{ justifyContent: 'center' }}
                        />
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default AllUsersList;
