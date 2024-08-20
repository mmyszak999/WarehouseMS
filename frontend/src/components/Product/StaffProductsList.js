import React, { useEffect, useState, useCallback } from 'react';
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
import '../../App.css'; // Import your CSS file
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

const legacyProductOptions = [
    { value: '', label: 'No Filter' },
    { value: 'true', label: 'Yes' },
    { value: 'false', label: 'No' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const StaffProductsList = ({ themeMode }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);
    const [filters, setFilters] = useState({
        name: { value: '', operator: 'eq', sort: '' },
        weight: { value: '', operator: 'eq', sort: '' },
        description: { value: '', operator: 'eq', sort: '' },
        categories__name: { value: '', operator: 'eq', sort: '' },
        wholesale_price: { value: '', operator: 'eq', sort: '' },
        legacy_product: { value: '', operator: 'eq', sort: '' }
    });

    const [isStaff, setIsStaff] = useState(false);

    useEffect(() => {
        // Fetch user role
        const fetchUserRole = () => {
            setIsStaff(AuthService.getUserRole());
        };

        fetchUserRole();
    }, []);

    const fetchProducts = async (page, size, appliedFilters) => {
        try {
            setLoading(true);
            let endpoint = `http://localhost:8000/api/products/all?page=${page}&size=${size}`;

            // Append filter params
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
            setProducts(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
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
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts(page, size, filters);
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

    const debounceFetchProducts = useCallback(
        debounce((updatedFilters) => {
            fetchProducts(page, size, updatedFilters);
        }, 500), // Adjust debounce delay as needed
        [page, size]
    );

    const handleFilterApply = () => {
        debounceFetchProducts(filters);
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
                        <Button color="inherit" component={Link} to="/product/create">Create Product</Button>
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
                            <Box key={key} sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    <strong>{key.replace(/_/g, ' ')}</strong>
                                </Typography>
                                <Grid container spacing={2}>
                                    {/* Value Input */}
                                    {key !== 'legacy_product' && (
                                        <Grid item xs={12} md={12}>
                                            <TextField
                                                label={key.replace(/_/g, ' ')}
                                                name={`${key}.value`}
                                                value={filter.value}
                                                onChange={handleFilterChange}
                                                fullWidth
                                            />
                                        </Grid>
                                    )}
                                    {/* Operator Select */}
                                    {key !== 'legacy_product' && (
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
                                    )}
                                    {/* Sort By Select */}
                                    {key !== 'legacy_product' && (
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
                                    )}
                                </Grid>
                            </Box>
                        ))}

                        {/* Legacy Product Filter */}
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Legacy Product</InputLabel>
                            <Select
                                value={filters.legacy_product.value}
                                onChange={(e) => handleFilterChange({ target: { name: 'legacy_product.value', value: e.target.value } })}
                            >
                                {legacyProductOptions.map(option => (
                                    <MenuItem key={option.value} value={option.value}>
                                        {option.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        <Button variant="contained" color="primary" onClick={handleFilterApply}>
                            Apply Filters
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Grid container spacing={3}>
                        {products.map(product => (
                            <Grid item xs={12} key={product.id}>
                                <Card className={`card ${themeMode}`}>
                                    <CardHeader
                                        title={
                                            <Link to={`/product/${product.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                                <Typography variant="h6" fontWeight="bold">{product.name}</Typography>
                                            </Link>
                                        }
                                    />
                                    <CardContent>
                                        <Typography variant="body1" fontFamily="Arial, sans-serif">{product.description}</Typography>
                                        <Typography variant="body2" fontFamily="Arial, sans-serif">Weight: {product.weight}</Typography>
                                        {isStaff && (
                                            <>
                                                <Typography variant="body2" fontFamily="Arial, sans-serif">Wholesale Price: {product.wholesale_price}</Typography>
                                            </>
                                        )}
                                        <Typography variant="body2" fontFamily="Arial, sans-serif">Categories:</Typography>
                                        <ul>
                                            {product.categories.map(category => (
                                                <li key={category.id} className={`list-item ${themeMode}`}>
                                                    <Typography variant="body2" fontFamily="Arial, sans-serif">{category.name}</Typography>
                                                </li>
                                            ))}
                                        </ul>
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

export default StaffProductsList;
