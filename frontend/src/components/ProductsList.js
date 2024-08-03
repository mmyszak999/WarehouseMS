// src/components/ProductsList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, CardHeader, CircularProgress, Grid } from '@mui/material';

const ProductsList = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/products/all', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setProducts(response.data.results);
            } catch (error) {
                setError('Error fetching products');
                console.error('Error fetching products:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    return (
        <Grid container spacing={3} sx={{ mt: 3 }}>
            {products.map(product => (
                <Grid item xs={12} key={product.id}>
                    <Card>
                        <CardHeader title={product.name} />
                        <CardContent>
                            <Typography variant="body1">{product.description}</Typography>
                            <Typography variant="body2">Weight: {product.weight}</Typography>
                            <Typography variant="body2">Wholesale Price: {product.wholesale_price}</Typography>
                            <Typography variant="body2">Amount in Goods: {product.amount_in_goods}</Typography>
                            <Typography variant="body2">Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</Typography>
                            <Typography variant="body2">Categories:</Typography>
                            <ul>
                                {product.categories.map(category => (
                                    <li key={category.id}>
                                        <Typography variant="body2">{category.name}</Typography>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};

export default ProductsList;
