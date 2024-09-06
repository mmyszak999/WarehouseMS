import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    CircularProgress,
    Typography,
    Card,
    CardContent,
    CardHeader,
    Box,
    AppBar,
    Toolbar,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    Pagination,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Divider
} from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const WaitingRoomDetail = ({ themeMode }) => {
    const { waitingRoomId } = useParams();
    const navigate = useNavigate();
    const [waitingRoom, setWaitingRoom] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stocks, setStocks] = useState([]);
    const [sourceWaitingRooms, setSourceWaitingRooms] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
    const [selectedSourceWaitingRoom, setSelectedSourceWaitingRoom] = useState('');
    const [isAddStockDialogOpen, setAddStockDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [page, setPage] = useState(1);
    const [size, setSize] = useState(10);
    const [totalPages, setTotalPages] = useState(1);

    const userRole = AuthService.getUserRole();
    const token = localStorage.getItem('token');

    const fetchWaitingRoom = useCallback(async () => {
        try {
            const endpoint = `http://localhost:8000/api/waiting_rooms/${waitingRoomId}/`;
            const response = await axios.get(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setWaitingRoom(response.data);
        } catch (error) {
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    }, [waitingRoomId, token]);

    const fetchStocks = useCallback(async (page, size, waitingRoomId) => {
        try {
            const endpoint = `http://localhost:8000/api/waiting_rooms/${waitingRoomId}`;
            const response = await axios.get(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setStocks(response.data.stocks);
            setTotalPages(Math.ceil(response.data.total_count / size)); // Update total pages based on response
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    const fetchSourceWaitingRooms = useCallback(async () => {
        try {
            const endpoint = 'http://localhost:8000/api/waiting_rooms/';
            const response = await axios.get(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setSourceWaitingRooms(response.data.results);
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    useEffect(() => {
        fetchWaitingRoom();
        fetchSourceWaitingRooms();
    }, [fetchWaitingRoom, fetchSourceWaitingRooms]);

    const handleDelete = async () => {
        try {
            await axios.delete(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            navigate('/');  // Redirect to home after deletion
        } catch (error) {
            handleError(error, setError);
        }
    };

    const handleAddStock = () => {
        setAddStockDialogOpen(true);
        if (selectedSourceWaitingRoom) {
            fetchStocks(page, size, selectedSourceWaitingRoom);
        }
    };

    const handleConfirmAddStock = async () => {
        if (selectedStock && selectedSourceWaitingRoom) {
            try {
                await axios.patch(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/add-stock`, {
                    id: selectedStock.id,
                    source_waiting_room: selectedSourceWaitingRoom
                }, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setAddStockDialogOpen(false);
                setSelectedStock(null);
                fetchWaitingRoom(); // Refresh waiting room details
            } catch (error) {
                handleError(error, setError);
            }
        }
    };

    const handlePageChange = (event, value) => {
        setPage(value);
        if (selectedSourceWaitingRoom) {
            fetchStocks(value, size, selectedSourceWaitingRoom);
        }
    };

    const handleSizeChange = (event) => {
        setSize(event.target.value);
        setPage(1); // Reset to first page whenever size changes
        if (selectedSourceWaitingRoom) {
            fetchStocks(1, event.target.value, selectedSourceWaitingRoom);
        }
    };

    const handleStockClick = (stock) => {
        // Conditionally navigate to different routes based on user role
        if (userRole) {
            navigate(`/stock/all/${stock.id}`);
        } else {
            navigate(`/stock/${stock.id}`);
        }
    };

    const handleAddStockClick = (stock) => {
        setSelectedStock(stock); // Navigate to the stock detail page
    };

    if (loading) return <CircularProgress />;
    if (error) return <Typography variant="h6" color="error">{error}</Typography>;

    return (
        <Box sx={{ flexGrow: 1 }}>
            {/* Navigation Bar */}
            <AppBar position="static" className={`app-bar ${themeMode}`}>
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {userRole && (
                        <Button color="inherit" component={Link} to={`/waiting_room/update/${waitingRoomId}`}>
                            Update Waiting Room
                        </Button>
                    )}
                </Toolbar>
            </AppBar>

            <Card className={`card ${themeMode}`} sx={{ mt: 2 }}>
                <CardHeader
                    title={<Typography variant="h6" fontWeight="bold">{waitingRoom?.name || 'Unnamed Room'}</Typography>}
                />
                <CardContent>
                    <Typography variant="body1">Max Stocks: {waitingRoom?.max_stocks}</Typography>
                    <Typography variant="body1">Max Weight: {waitingRoom?.max_weight}</Typography>
                    <Typography variant="body1">Occupied Slots: {waitingRoom?.occupied_slots}</Typography>
                    <Typography variant="body1">Current Stock Weight: {waitingRoom?.current_stock_weight}</Typography>
                    <Typography variant="body1">Available Slots: {waitingRoom?.available_slots}</Typography>
                    <Typography variant="body1">Available Stock Weight: {waitingRoom?.available_stock_weight}</Typography>
                    <Typography variant="body2">Created At: {waitingRoom?.created_at || 'N/A'}</Typography>

                    {userRole && (
                        <Box sx={{ mt: 2 }}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleAddStock}
                                sx={{ mr: 2 }}
                            >
                                Add Stock
                            </Button>
                            <Button
                                variant="contained"
                                color="error"
                                onClick={() => setDeleteDialogOpen(true)}
                            >
                                Delete Waiting Room
                            </Button>
                        </Box>
                    )}

                    {userRole && (
                        <>
                            <Typography variant="h6" sx={{ mt: 2 }}>Stocks in Waiting Room:</Typography>
                            {waitingRoom?.stocks && waitingRoom.stocks.length > 0 ? (
                                <List>
                                    {waitingRoom.stocks.map((stock) => (
                                        <ListItem
                                            button
                                            key={stock.id}
                                            onClick={() => handleStockClick(stock)}
                                        >
                                            <ListItemText
                                                primary={stock.product.name}
                                                secondary={`Weight: ${stock.weight}, Count: ${stock.product_count}`}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            ) : (
                                <Typography variant="body2">No stocks found in this waiting room.</Typography>
                            )}
                        </>
                    )}
                </CardContent>
            </Card>

            {/* Add Stock Dialog */}
            <Dialog open={isAddStockDialogOpen} onClose={() => setAddStockDialogOpen(false)}>
                <DialogTitle>Select Source Waiting Room and Stock to Add</DialogTitle>
                <DialogContent>
                    <FormControl sx={{ mb: 2, minWidth: 120 }}>
                        <InputLabel>Source Waiting Room</InputLabel>
                        <Select
                            value={selectedSourceWaitingRoom}
                            onChange={(e) => {
                                setSelectedSourceWaitingRoom(e.target.value);
                                fetchStocks(page, size, e.target.value);
                            }}
                            label="Source Waiting Room"
                        >
                            {sourceWaitingRooms.map(room => (
                                <MenuItem key={room.id} value={room.id}>
                                    {room.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl sx={{ mb: 2, minWidth: 120 }}>
                        <InputLabel>Items per page</InputLabel>
                        <Select value={size} onChange={handleSizeChange} label="Items per page">
                            <MenuItem value={10}>10</MenuItem>
                            <MenuItem value={20}>20</MenuItem>
                            <MenuItem value={50}>50</MenuItem>
                        </Select>
                    </FormControl>
                    {stocks && stocks.length > 0 ? (
                        <List>
                            {stocks.map(stock => (
                                <ListItem
                                    button
                                    key={stock.id}
                                    selected={selectedStock?.id === stock.id}
                                    onClick={() => handleAddStockClick(stock)}
                                >
                                    <ListItemText
                                        primary={stock.product.name}
                                        secondary={`Weight: ${stock.weight}, Count: ${stock.product_count}`}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    ) : (
                        <Typography>No stocks found in this waiting room.</Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setAddStockDialogOpen(false)}>Cancel</Button>
                    <Button
                        onClick={handleConfirmAddStock}
                        disabled={!selectedStock || !selectedSourceWaitingRoom}
                        color="primary"
                    >
                        Confirm Add Stock
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Dialog */}
            <Dialog open={isDeleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Are you sure you want to delete this waiting room?</DialogTitle>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDelete} color="error">Delete</Button>
                </DialogActions>
            </Dialog>

            {/* Pagination */}
            {totalPages > 1 && (
                <Pagination
                    count={totalPages}
                    page={page}
                    onChange={handlePageChange}
                    sx={{ mt: 2 }}
                />
            )}
        </Box>
    );
};

export default WaitingRoomDetail;
