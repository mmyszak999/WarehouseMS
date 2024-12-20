import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    Button,
    CircularProgress,
    TextField,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import { handleError } from '../ErrorHandler';

const UpdateProduct = ({ themeMode }) => {
    const { productId } = useParams();
    const navigate = useNavigate();
    const [product, setProduct] = useState(null);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        wholesale_price: '',
        description: '',
        category_ids: { id: [] }
    });

    useEffect(() => {
        const fetchProductAndCategories = async () => {
            try {
                const [productResponse, categoriesResponse] = await Promise.all([
                    axios.get(`http://localhost:8000/api/products/all/${productId}`, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }),
                    axios.get('http://localhost:8000/api/categories?size=100&page=1', {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    })
                ]);

                const productCategories = productResponse.data.category_ids?.id || [];
                const categoriesData = categoriesResponse.data.results || [];

                setProduct(productResponse.data);
                setCategories(categoriesData);
                setFormData({
                    name: productResponse.data.name || '',
                    wholesale_price: productResponse.data.wholesale_price || '',
                    description: productResponse.data.description || '',
                    category_ids: { id: productCategories }
                });
            } catch (error) {
                handleError(error, setError);
            } finally {
                setLoading(false);
            }
        };

        fetchProductAndCategories();
    }, [productId]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value
        }));
    };

    const handleCategoryChange = (e) => {
        const { value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            category_ids: { id: value }
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const cleanedFormData = {
            ...formData,
            category_ids: { id: formData.category_ids.id } 
        };

        console.log('Cleaned Form Data:', cleanedFormData);

        try {
            await axios.patch(`http://localhost:8000/api/products/${productId}`, cleanedFormData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            navigate(`/product/${productId}`);
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
                setError('Network Error: No response received from server');
            } else {
                setError('Error: ' + error.message);
            }
            console.error('Error fetching users:', error);
        }
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{String(error)}</Typography>;
    }

    return (
        <Box className={`update-product-form ${themeMode}`}>
            <Typography variant="h4" gutterBottom>Update Product</Typography>
            <form onSubmit={handleSubmit}>
                <TextField
                    label="Name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    fullWidth
                    margin="normal"
                />
                <TextField
                    label="Wholesale Price"
                    name="wholesale_price"
                    value={formData.wholesale_price}
                    onChange={handleInputChange}
                    fullWidth
                    margin="normal"
                    type="number"
                />
                <TextField
                    label="Description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    fullWidth
                    margin="normal"
                    multiline
                    rows={4}
                />
                <FormControl fullWidth margin="normal">
                    <InputLabel>Categories</InputLabel>
                    <Select
                        multiple
                        value={formData.category_ids.id}
                        onChange={handleCategoryChange}
                        renderValue={(selected) => selected.join(', ')}
                    >
                        {loading ? (
                            <MenuItem disabled>Loading categories...</MenuItem>
                        ) : categories.length > 0 ? (
                            categories.map(category => (
                                <MenuItem key={category.id} value={category.id}>
                                    {category.name}
                                </MenuItem>
                            ))
                        ) : (
                            <MenuItem disabled>No categories available</MenuItem>
                        )}
                    </Select>
                </FormControl>
                <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                    Update Product
                </Button>
            </form>
        </Box>
    );
};

export default UpdateProduct;
