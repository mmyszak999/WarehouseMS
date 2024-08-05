import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, TextField, MenuItem, Select, InputLabel, FormControl, Divider } from '@mui/material';
import { Link } from 'react-router-dom';
import AuthService from '../services/AuthService';
import '../App.css'; // Import your CSS file

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

const ProductsList = ({ themeMode }) => {
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
        category__name: { value: '', operator: 'eq', sort: '' },
        legacy_product: { value: '', operator: 'eq', sort: '' }  // Added legacy_product filter
    });

    const userRole = AuthService.getUserRole();

    const fetchProducts = async (page) => {
        try {
            setLoading(true);
            let endpoint = `http://localhost:8000/api/products?page=${page}&size=${size}`;

            // Append filter params
            for (const [key, filter] of Object.entries(filters)) {
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
            setError('Error fetching products');
            console.error('Error fetching products:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts(page);
    }, [userRole, page, filters]);

    const handlePageChange = (event, value) => {
        setPage(value);
    };

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        const [field, type] = name.split('.');
        setFilters(prevFilters => ({
            ...prevFilters,
            [field]: { ...prevFilters[field], [type]: value }
        }));
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
                                    {key.replace(/_/g, ' ')}
                                </Typography>
                                <Grid container spacing={2}>
                                    {/* Value Input */}
                                    <Grid item xs={12} md={12}>
                                        <TextField
                                            label={`${key.replace(/_/g, ' ')}`}
                                            name={`${key}.value`}
                                            value={filter.value}
                                            onChange={handleFilterChange}
                                            fullWidth
                                            disabled={key === 'legacy_product'}
                                        />
                                    </Grid>
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
                                    {/* Legacy Product Filter */}
                                    {key === 'legacy_product' && (
                                        <Grid item xs={12} md={12}>
                                            <FormControl fullWidth>
                                                <InputLabel>Legacy Product</InputLabel>
                                                <Select
                                                    name={`${key}.value`}
                                                    value={filter.value}
                                                    onChange={handleFilterChange}
                                                    label="Legacy Product"
                                                >
                                                    {legacyProductOptions.map(option => (
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
                                        {userRole && (
                                            <>
                                                <Typography variant="body2" fontFamily="Arial, sans-serif">Wholesale Price: {product.wholesale_price}</Typography>
                                            </>
                                        )}
                                        <Typography variant="body2" fontFamily="Arial, sans-serif">Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</Typography>
                                        <Typography variant="body2" fontFamily="Arial, sans-serif">Categories:</Typography>
                                        <ul>
                                            {product.categories.map(category => (
                                                <li key={category.name} className={`list-item ${themeMode}`}>
                                                    <Typography variant="body2" fontFamily="Arial, sans-serif">{category.name}</Typography>
                                                </li>
                                            ))}
                                        </ul>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
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

export default ProductsList;
