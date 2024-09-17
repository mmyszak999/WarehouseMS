import React, { useState, useEffect } from 'react';
import {
    TextField, Button, Box, Typography, Container, MenuItem, AppBar, Toolbar,
    FormControl, InputLabel, Select, CircularProgress, Snackbar, Alert, Radio, RadioGroup, FormControlLabel, FormLabel
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { handleError } from '../ErrorHandler';

const CreateReception = () => {
    const [products, setProducts] = useState([]);
    const [waitingRooms, setWaitingRooms] = useState([]);
    const [sections, setSections] = useState([]);
    const [racks, setRacks] = useState({});
    const [rackLevels, setRackLevels] = useState({});
    const [rackLevelSlots, setRackLevelSlots] = useState({});
    const [formData, setFormData] = useState({
        products_data: [{ product_id: '', product_count: 0, waiting_room_id: null, rack_level_id: null, rack_level_slot_id: null, section_id: '', rack_id: '', location_type: '' }],
        description: ''
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productsRes, waitingRoomsRes, sectionsRes] = await Promise.all([
                    axios.get('http://localhost:8000/api/products', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }),
                    axios.get('http://localhost:8000/api/waiting_rooms/?size=25', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }),
                    axios.get('http://localhost:8000/api/sections/?size=25', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
                ]);

                setProducts(productsRes.data.results || []);
                setWaitingRooms(waitingRoomsRes.data.results || []);
                setSections(sectionsRes.data.results || []);
                setLoading(false);
            } catch (error) {
                handleError(error, setError);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const fetchRacks = async (sectionId, index) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}/racks`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
            setRacks((prev) => ({ ...prev, [index]: response.data.results || [] }));
        } catch (error) {
            handleError(error, setError);
        }
    };

    const fetchRackLevels = async (rackId, index) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/racks/${rackId}/rack_levels`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
            setRackLevels((prev) => ({ ...prev, [index]: response.data.results || [] }));
        } catch (error) {
            handleError(error, setError);
        }
    };

    const fetchRackLevelSlots = async (rackLevelId, index) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/rack_levels/${rackLevelId}/slots`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
            setRackLevelSlots((prev) => ({ ...prev, [index]: response.data.results || [] }));
        } catch (error) {
            handleError(error, setError);
        }
    };

    const handleProductChange = (e, index) => {
        const { name, value } = e.target;
        setFormData(prevState => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index] = { ...updatedProducts[index], [name]: value };
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const handleLocationTypeChange = (e, index) => {
        const { value } = e.target;
        setFormData(prevState => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index].location_type = value;
            // Reset fields based on location type
            if (value === 'waiting_room') {
                updatedProducts[index] = {
                    ...updatedProducts[index],
                    waiting_room_id: updatedProducts[index].waiting_room_id,
                    section_id: null,
                    rack_id: null,
                    rack_level_id: null,
                    rack_level_slot_id: null,
                };
            } else if (value === 'rack_level') {
                updatedProducts[index] = {
                    ...updatedProducts[index],
                    waiting_room_id: null,
                    section_id: updatedProducts[index].section_id || '',
                    rack_id: null,
                    rack_level_id: updatedProducts[index].rack_level_id || '',
                    rack_level_slot_id: null,
                };
            } else if (value === 'rack_level_slot') {
                updatedProducts[index] = {
                    ...updatedProducts[index],
                    waiting_room_id: null,
                    section_id: updatedProducts[index].section_id || '',
                    rack_id: updatedProducts[index].rack_id || '',
                    rack_level_id: updatedProducts[index].rack_level_id || '',
                    rack_level_slot_id: updatedProducts[index].rack_level_slot_id || '',
                };
            }
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const handleSectionChange = (e, index) => {
        const { value } = e.target;
        fetchRacks(value, index);
        setFormData(prevState => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index] = {
                ...updatedProducts[index],
                section_id: value,
                rack_id: null,
                rack_level_id: null,
                rack_level_slot_id: null
            };
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const handleRackChange = (e, index) => {
        const { value } = e.target;
        fetchRackLevels(value, index);
        setFormData(prevState => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index] = {
                ...updatedProducts[index],
                rack_id: value,
                rack_level_id: null,
                rack_level_slot_id: null
            };
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const handleRackLevelChange = (e, index) => {
        const { value } = e.target;
        fetchRackLevelSlots(value, index);
        setFormData(prevState => {
            const updatedProducts = [...prevState.products_data];
            updatedProducts[index] = {
                ...updatedProducts[index],
                rack_level_id: value,
                rack_level_slot_id: null
            };
            return { ...prevState, products_data: updatedProducts };
        });
    };

    const addAnotherProduct = () => {
        setFormData(prevState => ({
            ...prevState,
            products_data: [...prevState.products_data, { product_id: '', product_count: 0, waiting_room_id: null, rack_level_id: null, rack_level_slot_id: null, section_id: '', rack_id: '', location_type: '' }]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Ensure that rack_level_id and rack_level_slot_id are mutually exclusive
            const products_data = formData.products_data.map(product => {
                let { waiting_room_id, rack_level_slot_id, rack_level_id } = product;
                if (rack_level_slot_id) {
                    rack_level_id = null;
                }
                return { ...product, rack_level_id, rack_level_slot_id };
            });

            const receptionData = {
                description: formData.description,
                products_data
            };

            await axios.post('http://localhost:8000/api/receptions/', receptionData, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            setSuccess('Reception created successfully!');
            navigate('/');
        } catch (error) {
            handleError(error, setError);
        }
    };

    return (
        <Container component="main" maxWidth="md">
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
                        My App
                    </Typography>
                </Toolbar>
            </AppBar>
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">Create Reception</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    {loading ? <CircularProgress /> : (
                        <>
                            {formData.products_data.map((product, index) => (
                                <Box key={index} sx={{ mb: 2 }}>
                                    <FormControl fullWidth margin="normal">
                                        <InputLabel>Product</InputLabel>
                                        <Select
                                            name="product_id"
                                            value={product.product_id}
                                            onChange={(e) => handleProductChange(e, index)}
                                        >
                                            {products.map((prod) => (
                                                <MenuItem key={prod.id} value={prod.id}>
                                                    {prod.name} ({prod.weight})
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                    <TextField
                                        label="Product Count"
                                        type="number"
                                        name="product_count"
                                        value={product.product_count}
                                        onChange={(e) => handleProductChange(e, index)}
                                        fullWidth
                                        margin="normal"
                                    />
                                    <FormControl component="fieldset">
                                        <FormLabel component="legend">Location Type</FormLabel>
                                        <RadioGroup
                                            name="location_type"
                                            value={product.location_type}
                                            onChange={(e) => handleLocationTypeChange(e, index)}
                                        >
                                            <FormControlLabel value="waiting_room" control={<Radio />} label="Waiting Room" />
                                            <FormControlLabel value="rack_level" control={<Radio />} label="Rack Level" />
                                            <FormControlLabel value="rack_level_slot" control={<Radio />} label="Rack Level Slot" />
                                        </RadioGroup>
                                    </FormControl>
                                    {product.location_type === 'waiting_room' && (
                                        <FormControl fullWidth margin="normal">
                                            <InputLabel>Waiting Room</InputLabel>
                                            <Select
                                                name="waiting_room_id"
                                                value={product.waiting_room_id}
                                                onChange={(e) => handleProductChange(e, index)}
                                            >
                                                {waitingRooms.map((room) => (
                                                    <MenuItem key={room.id} value={room.id}>
                                                        {`Name: ${room.name}, Max Weight: ${room.max_weight}, available stock weight: ${room.available_stock_weight}, available slots: ${room.available_slots}`}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>
                                    )}
                                    {product.location_type === 'rack_level' && (
                                        <>
                                            <FormControl fullWidth margin="normal">
                                                <InputLabel>Section</InputLabel>
                                                <Select
                                                    name="section_id"
                                                    value={product.section_id}
                                                    onChange={(e) => handleSectionChange(e, index)}
                                                >
                                                    {sections.map((section) => (
                                                        <MenuItem key={section.id} value={section.id}>
                                                            {`Section: ${section.section_name}, Available Weight: ${section.available_weight}`}
                                                        </MenuItem>
                                                    ))}
                                                </Select>
                                            </FormControl>
                                            {racks[index] && racks[index].length > 0 && (
                                                <FormControl fullWidth margin="normal">
                                                    <InputLabel>Rack</InputLabel>
                                                    <Select
                                                        name="rack_id"
                                                        value={product.rack_id}
                                                        onChange={(e) => handleRackChange(e, index)}
                                                    >
                                                        {racks[index].map((rack) => (
                                                            <MenuItem key={rack.id} value={rack.id}>
                                                                {`${rack.rack_name}, available weight: ${rack.available_weight}`}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                            )}
                                            {rackLevels[index] && rackLevels[index].length > 0 && (
                                                <FormControl fullWidth margin="normal">
                                                    <InputLabel>Rack Level</InputLabel>
                                                    <Select
                                                        name="rack_level_id"
                                                        value={product.rack_level_id}
                                                        onChange={(e) => handleRackLevelChange(e, index)}
                                                    >
                                                        {rackLevels[index].map((rackLevel) => (
                                                            <MenuItem key={rackLevel.id} value={rackLevel.id}>
                                                                {`${rackLevel.description} - level #${rackLevel.rack_level_number}, available weight: ${rackLevel.available_weight}, available slots: ${rackLevel.available_slots}`}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                            )}
                                        </>
                                    )}
                                    {product.location_type === 'rack_level_slot' && (
                                        <>
                                            <FormControl fullWidth margin="normal">
                                                <InputLabel>Section</InputLabel>
                                                <Select
                                                    name="section_id"
                                                    value={product.section_id}
                                                    onChange={(e) => handleSectionChange(e, index)}
                                                >
                                                    {sections.map((section) => (
                                                        <MenuItem key={section.id} value={section.id}>
                                                            {`Section: ${section.section_name}, available weight: ${section.available_weight}`}
                                                        </MenuItem>
                                                    ))}
                                                </Select>
                                            </FormControl>
                                            {racks[index] && racks[index].length > 0 && (
                                                <FormControl fullWidth margin="normal">
                                                    <InputLabel>Rack</InputLabel>
                                                    <Select
                                                        name="rack_id"
                                                        value={product.rack_id}
                                                        onChange={(e) => handleRackChange(e, index)}
                                                    >
                                                        {racks[index].map((rack) => (
                                                            <MenuItem key={rack.id} value={rack.id}>
                                                                {`${rack.rack_name}, available weight: ${rack.available_weight}`}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                            )}
                                            {rackLevels[index] && rackLevels[index].length > 0 && (
                                                <FormControl fullWidth margin="normal">
                                                    <InputLabel>Rack Level</InputLabel>
                                                    <Select
                                                        name="rack_level_id"
                                                        value={product.rack_level_id}
                                                        onChange={(e) => handleRackLevelChange(e, index)}
                                                    >
                                                        {rackLevels[index].map((rackLevel) => (
                                                            <MenuItem key={rackLevel.id} value={rackLevel.id}>
                                                                {`${rackLevel.description} - level #${rackLevel.rack_level_number}, available weight: ${rackLevel.available_weight}, available slots: ${rackLevel.available_slots}`}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                            )}
                                            {rackLevelSlots[index] && rackLevelSlots[index].length > 0 && (
                                                <FormControl fullWidth margin="normal">
                                                    <InputLabel>Rack Level Slot</InputLabel>
                                                    <Select
                                                        name="rack_level_slot_id"
                                                        value={product.rack_level_slot_id}
                                                        onChange={(e) => handleProductChange(e, index)}
                                                    >
                                                        {rackLevelSlots[index].map((slot) => (
                                                            <MenuItem key={slot.id} value={slot.id}>
                                                                {`${slot.description}, slot #${slot.rack_level_slot_number}, is_active: ${slot.is_active ? 'Yes' : 'No'}, occupied: ${slot.stock ? 'Yes' : 'No'}`}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                            )}
                                        </>
                                    )}
                                </Box>
                            ))}
                            <Button
                                onClick={addAnotherProduct}
                                variant="contained"
                                color="primary"
                                fullWidth
                                sx={{ mt: 2 }}
                            >
                                Add Another Product
                            </Button>
                            <TextField
                                fullWidth
                                margin="normal"
                                name="description"
                                label="Reception Description"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                            <Button
                                type="submit"
                                variant="contained"
                                color="primary"
                                fullWidth
                                sx={{ mt: 2 }}
                            >
                                Create Reception
                            </Button>
                            {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
                            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
                        </>
                    )}
                </Box>
            </Box>
        </Container>
    );
};

export default CreateReception;
