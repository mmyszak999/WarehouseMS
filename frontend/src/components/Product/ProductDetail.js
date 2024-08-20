import { Box, Button, CircularProgress, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Typography } from '@mui/material';
import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../App.css'; // Import your CSS file
import AuthService from '../../services/AuthService';

const ProductDetail = ({ themeMode }) => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [legacyDialogOpen, setLegacyDialogOpen] = useState(false); // State to manage legacy confirmation dialog

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

        fetchProduct();
    }, [productId, userRole]);

    const handleMakeLegacy = async () => {
        try {
            await axios.patch(`http://localhost:8000/api/products/${productId}/legacy`, {}, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            setProduct(prevProduct => ({ ...prevProduct, legacy_product: true }));
            setLegacyDialogOpen(false);
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
        }
    };

    const handleOpenLegacyDialog = () => {
        setLegacyDialogOpen(true);
    };

    const handleCloseLegacyDialog = () => {
        setLegacyDialogOpen(false);
    };

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
            <Typography variant="body2" className="product-legacy">Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</Typography>
            {userRole && (
                <Typography variant="body2" className="product-wholesale-price">Wholesale Price: {product.wholesale_price}</Typography>
            )}
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

            {userRole && (
                <Box sx={{ mt: 4 }}>
                    <Button variant="contained" color="primary" component={Link} to={`/product/update/${product.id}`} sx={{ mt: 2 }}>
                        Update Product
                    </Button>

                    {!product.legacy_product && (
                        <Button variant="contained" color="warning" onClick={handleOpenLegacyDialog} sx={{ mt: 2, ml: 2 }}>
                            Make Product Legacy
                        </Button>
                    )}
                </Box>
            )}

            {/* Legacy Confirmation Dialog */}
            <Dialog
                open={legacyDialogOpen}
                onClose={handleCloseLegacyDialog}
            >
                <DialogTitle>{"Confirm Legacy Status"}</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to mark this product as a legacy product? This action cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseLegacyDialog} color="secondary">
                        No
                    </Button>
                    <Button onClick={handleMakeLegacy} color="warning" autoFocus>
                        Yes
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ProductDetail;
