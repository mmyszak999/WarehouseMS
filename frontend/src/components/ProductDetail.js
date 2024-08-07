// src/components/ProductDetail.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, CircularProgress, Box, Button } from '@mui/material';
import { useParams, Link } from 'react-router-dom';
import AuthService from '../services/AuthService';
import '../App.css'; // Import your CSS file

const ProductDetail = ({ themeMode }) => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const userRole = AuthService.getUserRole();

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
        <Box className="product-details">
            <Typography variant="h4" className="product-name">{product.name}</Typography>
            <Typography variant="body1" className="product-description">Description: {product.description}</Typography>
            <Typography variant="body2" className="product-weight">Weight: {product.weight}</Typography>
            {userRole && (
                <>
                    <Typography variant="body2" className="product-wholesale-price">Wholesale Price: {product.wholesale_price}</Typography>
                    <Button variant="contained" color="primary" component={Link} to={`/product/update/${product.id}`} sx={{ mt: 2 }}>
                        Update Product
                    </Button>
                </>
            )}
            <Typography variant="body2" className="product-legacy">Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</Typography>
            <Typography variant="body2" className="product-categories">Categories:</Typography>
            <ul>
                {product.categories.map(category => (
                    <li key={category.id} className="list-item">
                        {userRole ? (
                            <Typography
                                variant="body2"
                                className="product-category-name"
                                component={Link}
                                to={`/category/${category.id}`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                            >
                                {category.name}
                            </Typography>
                        ) : (
                            <Typography variant="body2" className="product-category-name">
                                {category.name}
                            </Typography>
                        )}
                    </li>
                ))}
            </ul>
        </Box>
    );
};

export default ProductDetail;
