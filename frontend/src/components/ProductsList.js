import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination } from '@mui/material';
import { Link } from 'react-router-dom';
import AuthService from '../services/AuthService';
import '../App.css'; // Import your CSS file

const ProductsList = ({ themeMode }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [size, setSize] = useState(10);

    const userRole = AuthService.getUserRole();

    const fetchProducts = async (page) => {
        try {
            setLoading(true);
            const endpoint = userRole
                ? `http://localhost:8000/api/products/all?page=${page}&size=${size}`
                : `http://localhost:8000/api/products/?page=${page}&size=${size}`;

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
    }, [userRole, page]);

    const handlePageChange = (event, value) => {
        setPage(value);
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    return (
        <Box>
            <AppBar position="static" className={`app-bar ${themeMode}`}>
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {userRole && (
                        <Button color="inherit" component={Link} to="/product/create">Create Product</Button>
                    )}
                </Toolbar>
            </AppBar>
            <Grid container spacing={3} sx={{ mt: 3 }}>
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
                                        <li key={category.id} className={`list-item ${themeMode}`}>
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
        </Box>
    );
};

export default ProductsList;
