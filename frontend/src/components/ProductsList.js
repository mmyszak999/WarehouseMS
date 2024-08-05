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

const ProductsList = ({ themeMode }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);
    const [filters, setFilters] = useState({
        name: { value: '', operator: 'eq' },
        weight: { value: '', operator: 'eq' },
        created_at: { value: '', operator: 'eq' }
    });
    const [sort, setSort] = useState(''); // e.g., "weight__asc,created_at__desc"

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
            }

            // Append sort params
            if (sort) {
                endpoint += `&sort=${sort}`;
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
    }, [userRole, page, filters, sort]);

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

    const handleSortChange = (event) => {
        setSort(event.target.value);
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
                <Grid item xs={12} md={3}>
                    <Box sx={{ padding: 2, borderRight: '1px solid #ddd' }}>
                        <Typography variant="h6" gutterBottom>Filters</Typography>
                        <Divider sx={{ mb: 2 }} />
                        
                        <Box sx={{ mb: 2 }}>
                            <TextField
                                label="Name Filter"
                                name="name.value"
                                value={filters.name.value}
                                onChange={handleFilterChange}
                                fullWidth
                                sx={{ mb: 2 }}
                            />
                            <FormControl fullWidth>
                                <InputLabel>Operator</InputLabel>
                                <Select
                                    name="name.operator"
                                    value={filters.name.operator}
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
                        </Box>
                        
                        <Box sx={{ mb: 2 }}>
                            <TextField
                                label="Weight Filter"
                                name="weight.value"
                                value={filters.weight.value}
                                onChange={handleFilterChange}
                                fullWidth
                                sx={{ mb: 2 }}
                            />
                            <FormControl fullWidth>
                                <InputLabel>Operator</InputLabel>
                                <Select
                                    name="weight.operator"
                                    value={filters.weight.operator}
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
                        </Box>

                        <Box sx={{ mb: 2 }}>
                            <TextField
                                label="Creation Date Filter"
                                name="created_at.value"
                                value={filters.created_at.value}
                                onChange={handleFilterChange}
                                fullWidth
                                sx={{ mb: 2 }}
                            />
                            <FormControl fullWidth>
                                <InputLabel>Operator</InputLabel>
                                <Select
                                    name="created_at.operator"
                                    value={filters.created_at.operator}
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
                        </Box>
                        
                        <FormControl fullWidth>
                            <InputLabel>Sort By</InputLabel>
                            <Select
                                value={sort}
                                onChange={handleSortChange}
                                label="Sort By"
                            >
                                <MenuItem value="">None</MenuItem>
                                <MenuItem value="weight__asc">Weight Ascending</MenuItem>
                                <MenuItem value="weight__desc">Weight Descending</MenuItem>
                                <MenuItem value="created_at__asc">Creation Date Ascending</MenuItem>
                                <MenuItem value="created_at__desc">Creation Date Descending</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
                <Grid item xs={12} md={9}>
                    <Grid container spacing={3}>
                        {products.map(product => (
                            <Grid item xs={12} key={product.id}>
                                <Card className={`card ${themeMode}`}>
                                    <CardHeader
                                        title={
                                            <Link to={`/product/${product.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                                {product.name}
                                            </Link>
                                        }
                                    />
                                    <CardContent>
                                        <Typography variant="body1">{product.description}</Typography>
                                        <Typography variant="body2">Weight: {product.weight}</Typography>
                                        {userRole && (
                                            <>
                                                <Typography variant="body2">Wholesale Price: {product.wholesale_price}</Typography>
                                            </>
                                        )}
                                        <Typography variant="body2">Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</Typography>
                                        <Typography variant="body2">Categories:</Typography>
                                        <ul>
                                            {product.categories.map(category => (
                                                <li key={category.name} className={`list-item ${themeMode}`}>
                                                    <Typography variant="body2">{category.name}</Typography>
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
