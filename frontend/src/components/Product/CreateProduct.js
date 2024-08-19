import React, { useState, useEffect } from 'react';
import { TextField, Button, Box, Typography, Container, MenuItem, AppBar, Toolbar, FormControl, InputLabel, Select } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const CreateProduct = () => {
    const [productData, setProductData] = useState({
        name: '',
        description: '',
        weight: '',
        wholesale_price: '',
        category_ids: { id: [] },
    });

    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate(); // Use navigate to programmatically navigate

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/categories?size=100', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    }
                });
                setCategories(response.data.results || []);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching categories:', error);
                setLoading(false);
            }
        };

        fetchCategories();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name === 'category_ids') {
            setProductData(prevState => ({
                ...prevState,
                category_ids: { id: value }
            }));
        } else {
            setProductData(prevState => ({
                ...prevState,
                [name]: value,
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formattedData = {
            ...productData,
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
            navigate('/products'); // Redirect to /products after creation
        } catch (error) {
            console.error('Error creating product:', error);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
                        My App
                    </Typography>
                </Toolbar>
            </AppBar>
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
                    <FormControl fullWidth margin="normal">
                        <InputLabel>Categories</InputLabel>
                        <Select
                            multiple
                            value={productData.category_ids.id}
                            onChange={handleChange}
                            name="category_ids"
                            renderValue={(selected) => selected.map(id => categories.find(cat => cat.id === id)?.name).join(', ')}
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
                        </Select>
                    </FormControl>
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
