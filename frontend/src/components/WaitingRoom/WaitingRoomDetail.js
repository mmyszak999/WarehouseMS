import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import {
    AppBar,
    Toolbar,
    CircularProgress,
    Typography,
    Card,
    CardContent,
    CardHeader,
    Box,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const WaitingRoomDetail = ({ themeMode }) => {
    const { waitingRoomId } = useParams();
    const navigate = useNavigate();
    const [waitingRoom, setWaitingRoom] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [waitingRoomStocks, setWaitingRoomStocks] = useState([]);
    const [sourceWaitingRooms, setSourceWaitingRooms] = useState([]);
    const [sections, setSections] = useState([]);
    const [racks, setRacks] = useState([]);
    const [rackLevels, setRackLevels] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
    const [selectedSourceWaitingRoom, setSelectedSourceWaitingRoom] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    const [selectedRack, setSelectedRack] = useState('');
    const [selectedRackLevel, setSelectedRackLevel] = useState('');
    const [stockSourceType, setStockSourceType] = useState('waitingRoom');
    const [isAddStockDialogOpen, setAddStockDialogOpen] = useState(false);
    const [fetchedStocks, setFetchedStocks] = useState([]);
    const token = localStorage.getItem('token');
    const isStaff = AuthService.getUserRole();

    // Fetch waiting room details and stocks
    const fetchWaitingRoom = useCallback(async () => {
        try {
            const response = await axios.get(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setWaitingRoom(response.data);
            setWaitingRoomStocks(response.data.stocks.map(stock => ({
                id: stock.id,
                product_name: stock.product.name,
                weight: stock.weight,
                product_count: stock.product_count
            })));
        } catch (error) {
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    }, [waitingRoomId, token]);

    // Fetch all waiting rooms
    const fetchWaitingRooms = useCallback(async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/waiting_rooms/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setSourceWaitingRooms(response.data.results);
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    // Fetch sections
    const fetchSections = useCallback(async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/sections/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setSections(response.data.results);
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    // Fetch racks based on selected section
    const fetchRacks = useCallback(async (sectionId) => {
        if (!sectionId) return; // Prevent fetching if no section is selected
        try {
            const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}/racks/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setRacks(response.data.results);
            setSelectedRack(''); // Reset rack selection
            setRackLevels([]); // Reset rack levels
            setSelectedRackLevel(''); // Reset rack level selection
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    // Fetch rack levels based on selected rack
    const fetchRackLevels = useCallback(async (rackId) => {
        if (!rackId) return; // Prevent fetching rack levels if no rack is selected
        try {
            const response = await axios.get(`http://localhost:8000/api/racks/${rackId}/rack_levels/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setRackLevels(response.data.results);
            setSelectedRackLevel(''); // Reset rack level selection
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    useEffect(() => {
        fetchWaitingRoom();
        fetchWaitingRooms(); // Fetch waiting rooms
        fetchSections();
    }, [fetchWaitingRoom, fetchWaitingRooms, fetchSections]);

    const handleAddStock = () => {
        setAddStockDialogOpen(true);
        setFetchedStocks([]); // Clear fetched stocks when opening the dialog
    };

    const handleConfirmAddStock = async () => {
        if (selectedStock) {
            try {
                await axios.patch(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/add-stock`, {
                    id: selectedStock.id,
                    source_type: stockSourceType,
                    source_id: stockSourceType === 'waitingRoom' ? selectedSourceWaitingRoom : selectedRackLevel
                }, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setAddStockDialogOpen(false);
                setSelectedStock(null);
                fetchWaitingRoom();
            } catch (error) {
                handleError(error, setError);
            }
        }
    };

    const fetchStocks = useCallback(async (sourceId, sourceType) => {
        try {
            let response;
            if (sourceType === 'waitingRoom') {
                response = await axios.get(`http://localhost:8000/api/waiting_rooms/${sourceId}/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setFetchedStocks(response.data.stocks.map(stock => ({
                    id: stock.id,
                    product_name: stock.product.name,
                    weight: stock.weight
                })));
            } else if (sourceType === 'rackLevel') {
                response = await axios.get(`http://localhost:8000/api/rack_levels/${sourceId}/slots/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setFetchedStocks(response.data.results
                    .filter(stockSlot => stockSlot.stock !== null)
                    .map(stockSlot => ({
                        id: stockSlot.stock.id,
                        product_name: stockSlot.stock.product.name,
                        weight: stockSlot.stock.weight
                    })));
            }
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    const handleStockClick = (stock) => {
        const path = isStaff ? `/stock/all/${stock.id}` : `/stock/${stock.id}`;
        navigate(path);
    };

    if (loading) return <CircularProgress />;
    if (error) return <Typography variant="h6" color="error">{error}</Typography>;

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static" className={`app-bar ${themeMode}`}>
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {isStaff && (
                        <>
                            <Button 
                                color="inherit" 
                                sx={{ ml: 2 }}
                                component={Link}
                                to={`/waiting_room/update/${waitingRoomId}`}
                            >
                                Update Waiting Room
                            </Button>
                        </>
                    )}
                </Toolbar>
            </AppBar>
            <Card className={`card ${themeMode}`} sx={{ mt: 2 }}>
                <CardHeader
                    title={<Typography variant="h6" fontWeight="bold">{waitingRoom?.name || 'Unnamed Room'}</Typography>}
                />
                <CardContent>
                    {/* Display waiting room details */}
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body1">
                            <strong>Max Stocks:</strong> {waitingRoom?.max_stocks}
                        </Typography>
                        <Typography variant="body1">
                            <strong>Max Weight:</strong> {waitingRoom?.max_weight} kg
                        </Typography>
                        <Typography variant="body1">
                            <strong>Occupied Slots:</strong> {waitingRoom?.occupied_slots}
                        </Typography>
                        <Typography variant="body1">
                            <strong>Current Stock Weight:</strong> {waitingRoom?.current_stock_weight} kg
                        </Typography>
                        <Typography variant="body1">
                            <strong>Available Slots:</strong> {waitingRoom?.available_slots}
                        </Typography>
                        <Typography variant="body1">
                            <strong>Available Stock Weight:</strong> {waitingRoom?.available_stock_weight} kg
                        </Typography>
                        <Typography variant="body1">
                            <strong>Created At:</strong> {new Date(waitingRoom?.created_at).toLocaleDateString()}
                        </Typography>
                    </Box>

                    {isStaff && (
                        <Box sx={{ mt: 2 }}>
                            <Button variant="contained" color="primary" onClick={handleAddStock} sx={{ mr: 2 }}>
                                Add Stock
                            </Button>
                        </Box>
                    )}
                    <Typography variant="h6" sx={{ mt: 2 }}>Stocks in Waiting Room:</Typography>
                    {waitingRoomStocks.length > 0 ? (
                        <List>
                            {waitingRoomStocks.map((stock) => (
                                <ListItem key={stock.id} onClick={() => handleStockClick(stock)} button>
                                    <ListItemText primary={`${stock.product_name} (Weight: ${stock.weight}, Count: ${stock.product_count})`} />
                                </ListItem>
                            ))}
                        </List>
                    ) : (
                        <Typography>No stocks available in this waiting room.</Typography>
                    )}
                </CardContent>
            </Card>

            <Dialog open={isAddStockDialogOpen} onClose={() => setAddStockDialogOpen(false)}>
                <DialogTitle>Add Stock to Waiting Room</DialogTitle>
                <DialogContent>
                    <FormControl fullWidth sx={{ mt: 2 }}>
                        <InputLabel>Stock Source Type</InputLabel>
                        <Select
                            value={stockSourceType}
                            onChange={(e) => {
                                setStockSourceType(e.target.value);
                                setSelectedSourceWaitingRoom('');
                                setSelectedSection('');
                                setSelectedRack('');
                                setSelectedRackLevel('');
                                setFetchedStocks([]);
                            }}
                        >
                            <MenuItem value="waitingRoom">Waiting Room</MenuItem>
                            <MenuItem value="rackLevel">Rack Level</MenuItem>
                        </Select>
                    </FormControl>

                    {stockSourceType === 'waitingRoom' && (
                        <FormControl fullWidth sx={{ mt: 2 }}>
                            <InputLabel>Select Source Waiting Room</InputLabel>
                            <Select
                                value={selectedSourceWaitingRoom}
                                onChange={(e) => {
                                    setSelectedSourceWaitingRoom(e.target.value);
                                    fetchStocks(e.target.value, 'waitingRoom');
                                }}
                            >
                                {sourceWaitingRooms.map((room) => (
                                    <MenuItem key={room.id} value={room.id}>{room.name} (Available Stock Weight: {room.available_stock_weight}, Available Slots: {room.available_slots})</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    )}

                    {stockSourceType === 'rackLevel' && (
                        <>
                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>Select Section</InputLabel>
                                <Select
                                    value={selectedSection}
                                    onChange={(e) => {
                                        setSelectedSection(e.target.value);
                                        fetchRacks(e.target.value);
                                    }}
                                >
                                    {sections.map((section) => (
                                        <MenuItem
                                            key={section.id}
                                            value={section.id}
                                        >
                                            {section.section_name} (Available Weight: {section.available_weight}, Max Weight: {section.max_weight}, Max Racks: {section.max_racks})
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            {selectedSection && (
                                <FormControl fullWidth sx={{ mt: 2 }}>
                                    <InputLabel>Select Rack</InputLabel>
                                    <Select
                                        value={selectedRack}
                                        onChange={(e) => {
                                            setSelectedRack(e.target.value);
                                            fetchRackLevels(e.target.value);
                                        }}
                                    >
                                        {racks.map((rack) => (
                                            <MenuItem
                                                key={rack.id}
                                                value={rack.id}
                                            >
                                                Rack: {rack.rack_name} (Available Weight: {rack.available_weight}, Max Weight: {rack.max_weight}, Max Levels: {rack.max_levels})
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            )}

                            {selectedRack && (
                                <FormControl fullWidth sx={{ mt: 2 }}>
                                    <InputLabel>Select Rack Level</InputLabel>
                                    <Select
                                        value={selectedRackLevel}
                                        onChange={(e) => {
                                            setSelectedRackLevel(e.target.value);
                                            fetchStocks(e.target.value, 'rackLevel');
                                        }}
                                    >
                                        {rackLevels.map((level) => (
                                            <MenuItem
                                                key={level.id}
                                                value={level.id}
                                            >
                                                Level #{level.rack_level_number} (Available Weight: {level.available_weight}, Available Slots: {level.available_slots}, Max Slots: {level.max_slots})
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            )}
                        </>
                    )}

                    {fetchedStocks.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="h6">Available Stocks:</Typography>
                            <List>
                                {fetchedStocks.map((stock) => (
                                    <ListItem key={stock.id} button onClick={() => setSelectedStock(stock)}>
                                        <ListItemText primary={`${stock.product_name} (Weight: ${stock.weight}, Count: ${stock.product_count})`} />
                                    </ListItem>
                                ))}
                            </List>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setAddStockDialogOpen(false)} color="secondary">Cancel</Button>
                    <Button onClick={handleConfirmAddStock} color="primary" disabled={!selectedStock}>Confirm</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default WaitingRoomDetail;
