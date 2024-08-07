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
        category_ids: { id: [] } // Correctly format as an object with an id property
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

                // Extract categories from the `results` key
                const productCategories = productResponse.data.category_ids?.id || [];
                const categoriesData = categoriesResponse.data.results || [];

                setProduct(productResponse.data);
                setCategories(categoriesData);
                setFormData({
                    name: productResponse.data.name || '',
                    wholesale_price: productResponse.data.wholesale_price || '',
                    description: productResponse.data.description || '',
                    category_ids: { id: productCategories } // Format correctly
                });
            } catch (error) {
                setError('Error fetching product or categories');
                console.error('Error fetching product or categories:', error);
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
            category_ids: { id: value } // Ensure format is correct
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // No need to filter out empty fields if we're sending category_ids in the required format
        const cleanedFormData = {
            ...formData,
            category_ids: { id: formData.category_ids.id } // Ensure category_ids is in the correct format
        };

        console.log('Cleaned Form Data:', cleanedFormData); // Debug log

        try {
            await axios.patch(`http://localhost:8000/api/products/${productId}`, cleanedFormData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            navigate(`/product/${productId}`);
        } catch (error) {
            // Properly extract and format error messages
            const errorMessage = error.response?.data?.detail?.map(err => err.msg).join(', ') || 'Error updating product';
            setError(errorMessage);
            console.error('Error updating product:', error);
        }
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{String(error)}</Typography>; // Convert error to string
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
