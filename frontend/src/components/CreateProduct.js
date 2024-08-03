// src/components/CreateProduct.js
import React, { useState, useEffect } from 'react';
import { TextField, Button, Box, Typography, Container, MenuItem } from '@mui/material';
import axios from 'axios';

const CreateProduct = () => {
    const [productData, setProductData] = useState({
        name: '',
        description: '',
        weight: '',
        wholesale_price: '',
        category_id: '',
    });

    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/categories');
                setCategories(response.data.results || []); // Use response.data.results for paginated data
                setLoading(false);
            } catch (error) {
                console.error('Error fetching categories:', error);
                setLoading(false);
            }
        };

        fetchCategories();
    }, []);

    const handleChange = (e) => {
        setProductData({
            ...productData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formattedData = {
            ...productData,
            category_id: productData.category_id.trim(),
            weight: parseFloat(productData.weight),
            wholesale_price: parseFloat(productData.wholesale_price),
        };

        try {
            const response = await axios.post('http://localhost:8000/api/products', formattedData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log('Product created:', response.data);
        } catch (error) {
            console.error('Error creating product:', error);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">Create Product</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    <TextField
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        id="name"
                        label="Name"
                        name="name"
                        autoComplete="name"
                        autoFocus
                        value={productData.name}
                        onChange={handleChange}
                    />
                    <TextField
                        variant="outlined"
                        margin="normal"
                        fullWidth
                        id="description"
                        label="Description"
                        name="description"
                        autoComplete="description"
                        value={productData.description}
                        onChange={handleChange}
                    />
                    <TextField
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        id="weight"
                        label="Weight"
                        name="weight"
                        autoComplete="weight"
                        value={productData.weight}
                        onChange={handleChange}
                    />
                    <TextField
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        id="wholesale_price"
                        label="Wholesale Price"
                        name="wholesale_price"
                        autoComplete="wholesale_price"
                        value={productData.wholesale_price}
                        onChange={handleChange}
                    />
                    <TextField
                        select
                        variant="outlined"
                        margin="normal"
                        fullWidth
                        id="category_id"
                        label="Category"
                        name="category_id"
                        value={productData.category_id}
                        onChange={handleChange}
                        disabled={loading}
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
                    </TextField>
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Create Product
                    </Button>
                </Box>
            </Box>
        </Container>
    );
};

export default CreateProduct;
