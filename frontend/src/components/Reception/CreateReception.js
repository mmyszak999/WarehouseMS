import React, { useState, useEffect } from 'react';
import {
    TextField, Button, Box, Typography, Container, MenuItem, AppBar, Toolbar,
    FormControl, InputLabel, Select, CircularProgress, Snackbar, Alert
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { handleError } from '../ErrorHandler';

const CreateReception = () => {
    const [products, setProducts] = useState([]);
    const [waitingRooms, setWaitingRooms] = useState([]);
    const [rackLevels, setRackLevels] = useState([]);
    const [rackLevelSlots, setRackLevelSlots] = useState([]);
    const [formData, setFormData] = useState({
        products_data: [
            { product_id: '', product_count: 0, waiting_room_id: null, rack_level_id: null, rack_level_slot_id: null }
        ],
        description: ''
    });
    const [selectedRackLevel, setSelectedRackLevel] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productsRes, waitingRoomsRes, rackLevelsRes] = await Promise.all([
                    axios.get('http://localhost:8000/api/products', {
                        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                    }),
                    axios.get('http://localhost:8000/api/waiting_rooms/?size=25', {
                        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                    }),
                    axios.get('http://localhost:8000/api/rack_levels/?size=250', {
                        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                    })
                ]);

                setProducts(productsRes.data.results || []);
                setWaitingRooms(waitingRoomsRes.data.results || []);
                setRackLevels(rackLevelsRes.data.results || []);
                setLoading(false);
            } catch (error) {
                handleError(error, setError);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    useEffect(() => {
        if (selectedRackLevel) {
            const fetchRackLevelSlots = async () => {
                try {
                    const response = await axios.get(
                        `http://localhost:8000/api/rack_levels/${selectedRackLevel}/slots`, {
                            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                        }
                    );
                    setRackLevelSlots(response.data.results || []);
                } catch (error) {
                    handleError(error, setError);
                }
            };
            fetchRackLevelSlots();
        } else {
            setRackLevelSlots([]); // Clear slots if "None" is selected
        }
    }, [selectedRackLevel]);

    const handleProductChange = (e, index) => {
        const { name, value } = e.target;
        setFormData((prevState) => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index] = { ...updatedProducts[index], [name]: value };
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const handleAddProduct = () => {
        setFormData((prevState) => ({
            ...prevState,
            products_data: [
                ...prevState.products_data,
                { product_id: '', product_count: 0, waiting_room_id: null, rack_level_id: null, rack_level_slot_id: null }
            ]
        }));
    };

    const handleRemoveProduct = (index) => {
        setFormData((prevState) => ({
            ...prevState,
            products_data: prevState.products_data.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(
                'http://localhost:8000/api/receptions/', formData, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                }
            );
            setSuccess('Reception created successfully!');
            navigate('/'); // Redirect to home or another page
        } catch (error) {
            handleError(error, setError);
        }
    };

    return (
        <Container component="main" maxWidth="md">
            <AppBar position="static">
                <Toolbar>
                    <Typography
                        variant="h6"
                        component={Link}
                        to="/"
                        sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}
                    >
                        My App
                    </Typography>
                </Toolbar>
            </AppBar>
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">Create Reception</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    {loading ? (
                        <CircularProgress />
                    ) : (
                        <>
                            {formData.products_data.map((product, index) => {
                                const selectedProduct = products.find(p => p.id === product.product_id);
                                const selectedRoom = waitingRooms.find(w => w.id === product.waiting_room_id);

                                return (
                                    <Box key={index} sx={{ mb: 2 }}>
                                        <FormControl fullWidth margin="normal">
                                            <InputLabel id={`product-label-${index}`}>Product</InputLabel>
                                            <Select
                                                labelId={`product-label-${index}`}
                                                name="product_id"
                                                value={product.product_id}
                                                onChange={(e) => handleProductChange(e, index)}
                                            >
                                                {products.map((prod) => (
                                                    <MenuItem key={prod.id} value={prod.id}>
                                                        Name: {prod.name}, Weight: {prod.weight}, Description: {prod.description}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                        {selectedProduct && (
                                            <Typography variant="body2" color="textSecondary">
                                                {`Description: ${selectedProduct.description}, Weight: ${selectedProduct.weight}`}
                                            </Typography>
                                        )}

                                        <TextField
                                            variant="outlined"
                                            margin="normal"
                                            required
                                            fullWidth
                                            name="product_count"
                                            label="Product Count"
                                            type="number"
                                            value={product.product_count}
                                            onChange={(e) => handleProductChange(e, index)}
                                        />

                                        <FormControl fullWidth margin="normal">
                                            <InputLabel id={`waiting-room-label-${index}`}>Waiting Room</InputLabel>
                                            <Select
                                                labelId={`waiting-room-label-${index}`}
                                                name="waiting_room_id"
                                                value={product.waiting_room_id || ''}
                                                onChange={(e) => handleProductChange(e, index)}
                                            >
                                                {waitingRooms.map((room) => (
                                                    <MenuItem key={room.id} value={room.id}>
                                                        Name: {room.name}, Occupied slots: {room.occupied_slots}, Available slots: {room.available_slots},
                                                        Available stock weight: {room.available_stock_weight}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                        {selectedRoom && (
                                            <Typography variant="body2" color="textSecondary">
                                                {`Max Stocks: ${selectedRoom.max_stocks}, Available Weight: ${selectedRoom.available_stock_weight}`}
                                            </Typography>
                                        )}

                                        <Button
                                            type="button"
                                            color="error"
                                            onClick={() => handleRemoveProduct(index)}
                                        >
                                            Remove Product
                                        </Button>
                                    </Box>
                                );
                            })}
                        </>
                    )}
                    <Button
                        type="button"
                        fullWidth
                        variant="contained"
                        color="primary"
                        onClick={handleAddProduct}
                    >
                        Add Another Product
                    </Button>
                    <TextField
                        variant="outlined"
                        margin="normal"
                        fullWidth
                        name="description"
                        label="Description"
                        multiline
                        rows={4}
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                    {error && (
                        <Snackbar open={true} autoHideDuration={6000} onClose={() => setError(null)}>
                            <Alert onClose={() => setError(null)} severity="error">
                                {error}
                            </Alert>
                        </Snackbar>
                    )}
                    {success && (
                        <Snackbar open={true} autoHideDuration={6000} onClose={() => setSuccess(null)}>
                            <Alert onClose={() => setSuccess(null)} severity="success">
                                {success}
                            </Alert>
                        </Snackbar>
                    )}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={loading}
                    >
                        Create Reception
                    </Button>
                </Box>
            </Box>
        </Container>
    );
};

export default CreateReception;
