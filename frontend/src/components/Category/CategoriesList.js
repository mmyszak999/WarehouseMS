import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, TextField, MenuItem, Select, InputLabel, FormControl, Divider } from '@mui/material';
import { Link } from 'react-router-dom';
import AuthService from '../../services/AuthService';
import '../../App.css'; 
import { debounce } from 'lodash';
import { handleError } from '../ErrorHandler'

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

const CategoriesList = ({ themeMode }) => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);
    const [filters, setFilters] = useState({
        name: { value: '', operator: 'eq', sort: '' },
    });

    const [isStaff, setIsStaff] = useState(false);

    useEffect(() => {
        const fetchUserRole = () => {
            setIsStaff(AuthService.getUserRole());
        };

        fetchUserRole();
    }, []);

    const fetchCategories = async (page, size, appliedFilters) => {
        try {
            setLoading(true);
            let endpoint = `http://localhost:8000/api/categories?page=${page}&size=${size}`;

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
            setCategories(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
        } catch (error) {
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCategories(page, size, filters);
    }, [page, size]);

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
        setFilters(prevFilters => ({
            ...prevFilters,
            [field]: { ...prevFilters[field], [type]: value }
        }));
    };

    const debounceFetchCategories = useCallback(
        debounce((updatedFilters) => {
            fetchCategories(page, size, updatedFilters);
        }, 500),
        [page, size]
    );

    const handleFilterApply = () => {
        debounceFetchCategories(filters);
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
                        <Button color="inherit" component={Link} to="/category/create">Create Category</Button>
                    )}
                </Toolbar>
            </AppBar>
            <Grid container spacing={3} sx={{ mt: 3 }}>
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
                                    <Grid item xs={12} md={12}>
                                        <TextField
                                            label={key.replace(/_/g, ' ')}
                                            name={`${key}.value`}
                                            value={filter.value}
                                            onChange={handleFilterChange}
                                            fullWidth
                                        />
                                    </Grid>
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
                        ))}
                        <Button variant="contained" color="primary" onClick={handleFilterApply}>
                            Apply Filters
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Grid container spacing={3}>
                        {categories.map(category => (
                            <Grid item xs={12} key={category.id}>
                                <Card className={`card ${themeMode}`}>
                                    <CardHeader
                                        title={
                                            isStaff ? (
                                                <Link to={`/category/${category.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                                    <Typography variant="h6" fontWeight="bold">{category.name}</Typography>
                                                </Link>
                                            ) : (
                                                <Typography variant="h6" fontWeight="bold">{category.name}</Typography>
                                            )
                                        }
                                    />
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

export default CategoriesList;
