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
    const [stocks, setStocks] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
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

    const fetchStocks = useCallback(async (page, size) => {
        try {
            const endpoint = `http://localhost:8000/api/stocks/?page=${page}&size=${size}`;
            const response = await axios.get(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setStocks(response.data.results);
            setTotalPages(Math.ceil(response.data.total / size));
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    useEffect(() => {
        fetchWaitingRoom();
    }, [fetchWaitingRoom]);

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

    const handleAddStock = async () => {
        setAddStockDialogOpen(true);
        fetchStocks(page, size); // Fetch stocks with current pagination settings
    };

    const handleConfirmAddStock = async () => {
        if (selectedStock) {
            try {
                await axios.patch(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/add-stock`, {
                    id: selectedStock.id
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
        fetchStocks(value, size); // Fetch stocks for the new page
    };

    const handleSizeChange = (event) => {
        setSize(event.target.value);
        setPage(1); // Reset to first page whenever size changes
        fetchStocks(1, event.target.value); // Fetch stocks for the new page size
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
                                waitingRoom.stocks.map((stock, index) => (
                                    <Typography variant="body2" key={index}>
                                        Stock {index + 1}: Product Name: {stock.product.name} - Weight: {stock.weight}
                                        , Product Count: {stock.product_count}, Product Description: {stock.product.description}
                                    </Typography>
                                ))
                            ) : (
                                <Typography variant="body2">No stocks found in this waiting room.</Typography>
                            )}
                        </>
                    )}
                </CardContent>
            </Card>

            {/* Add Stock Dialog */}
            <Dialog open={isAddStockDialogOpen} onClose={() => setAddStockDialogOpen(false)}>
                <DialogTitle>Select Stock to Add</DialogTitle>
                <DialogContent>
                    <FormControl sx={{ mb: 2, minWidth: 120 }}>
                        <InputLabel>Items per page</InputLabel>
                        <Select
                            value={size}
                            onChange={handleSizeChange}
                            label="Items per page"
                        >
                            {[5, 10, 15, 20, 25].map(option => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <List>
                        {stocks.length > 0 ? (
                            stocks.map(stock => (
                                <ListItem button key={stock.id} onClick={() => setSelectedStock(stock)}>
                                    <ListItemText
                                        primary={stock.product.name}
                                        secondary={`Weight: ${stock.weight}, Product Count: ${stock.product_count}`}
                                    />
                                </ListItem>
                            ))
                        ) : (
                            <Typography variant="body2">No stocks available to add.</Typography>
                        )}
                    </List>
                    <Pagination
                        count={totalPages}
                        page={page}
                        onChange={handlePageChange}
                        color="primary"
                        sx={{ mt: 2 }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setAddStockDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleConfirmAddStock} color="primary" disabled={!selectedStock}>
                        Add Stock
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={isDeleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogContent>
                    <Typography variant="body2">
                        Are you sure you want to delete this waiting room? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDelete} color="error" autoFocus>
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default WaitingRoomDetail;
