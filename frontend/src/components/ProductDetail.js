import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, CircularProgress, Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import AuthService from '../services/AuthService';

const ProductDetail = () => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const userRole = AuthService.getUserRole();
    console.log(userRole, "wwa");
    useEffect(() => {
        const fetchProduct = async () => {
            try {
                const endpoint = userRole
                    ? `http://localhost:8000/api/products/all/${productId}`
                    : `http://localhost:8000/api/products/${productId}`;

                const response = await axios.get(endpoint, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                console.log(response.data, "ww");
                setProduct(response.data);
            } catch (error) {
                setError('Error fetching product details');
                console.error('Error fetching product details:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProduct();
    }, [productId, userRole]);

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    if (!product) {
        return <Typography variant="h6">Product not found</Typography>;
    }

    return (
        <Box>
            <Typography variant="h4">{product.name}</Typography>
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
                    <li key={category.id}>
                        <Typography variant="body2">{category.name}</Typography>
                    </li>
                ))}
            </ul>
        </Box>
    );
};

export default ProductDetail;
