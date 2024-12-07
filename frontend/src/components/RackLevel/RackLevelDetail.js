import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
    Button, Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, 
    FormControl, InputLabel, Select, MenuItem, RadioGroup, FormControlLabel, Radio, 
    Box, CircularProgress, Typography, Grid, Card, CardContent, AppBar, Toolbar
} from '@mui/material';
import axios from 'axios';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const RackLevelDetail = ({ themeMode }) => {
    const { rackLevelId } = useParams();
    const navigate = useNavigate();
    const [rackLevel, setRackLevel] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [isAddStockDialogOpen, setAddStockDialogOpen] = useState(false);
    const [stockSourceType, setStockSourceType] = useState('waitingRoom');
    const [selectedSourceWaitingRoom, setSelectedSourceWaitingRoom] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    const [selectedRack, setSelectedRack] = useState('');
    const [selectedRackLevel, setSelectedRackLevel] = useState('');
    const [fetchedStocks, setFetchedStocks] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
    const [sourceWaitingRooms, setSourceWaitingRooms] = useState([]);
    const [sections, setSections] = useState([]);
    const [racks, setRacks] = useState([]);
    const [rackLevels, setRackLevels] = useState([]);
    const token = localStorage.getItem('token');
    const isStaff = AuthService.getUserRole();
    const canMoveStocks = AuthService.canMoveStocks();

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

    const fetchRacks = useCallback(async (sectionId) => {
        if (!sectionId) return;
        try {
            const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}/racks/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setRacks(response.data.results);
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    const fetchRackLevels = useCallback(async (rackId) => {
        if (!rackId) return;
        try {
            const response = await axios.get(`http://localhost:8000/api/racks/${rackId}/rack_levels/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setRackLevels(response.data.results);
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    const fetchRackLevelDetails = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/api/rack_levels/${rackLevelId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setRackLevel(response.data);
        } catch (error) {
            handleError(error, setError);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRackLevelDetails();
        fetchWaitingRooms();
        fetchSections();
    }, [rackLevelId, fetchWaitingRooms, fetchSections]);

    const handleAddStock = () => {
        setAddStockDialogOpen(true);
        setFetchedStocks([]);
    };

    const fetchStocks = useCallback(async (sourceId, sourceType) => {
        try {
            let response;
            if (sourceType === 'waitingRoom') {
                response = await axios.get(`http://localhost:8000/api/waiting_rooms/${sourceId}/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setFetchedStocks(response.data.stocks);
            } else if (sourceType === 'rackLevel') {
                response = await axios.get(`http://localhost:8000/api/rack_levels/${sourceId}/slots/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setFetchedStocks(response.data.results.filter(slot => slot.stock !== null).map(slot => slot.stock));
            }
        } catch (error) {
            handleError(error, setError);
        }
    }, [token]);

    const handleConfirmAddStock = async () => {
        if (selectedStock) {
            try {
                await axios.patch(`http://localhost:8000/api/rack_levels/${rackLevelId}/add-stock`, {
                    id: selectedStock.id,
                    source_type: stockSourceType,
                    source_id: stockSourceType === 'waitingRoom' ? selectedSourceWaitingRoom : selectedRackLevel
                }, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setAddStockDialogOpen(false);
                setSelectedStock(null);
                fetchRackLevelDetails();
            } catch (error) {
                handleError(error, setError);
            }
        }
    };

    const handleUpdateClick = () => {
        navigate(`/rack-level/${rackLevelId}/update`);
    };

    const handleDeleteClick = () => {
        setOpenDialog(true);
    };

    const handleConfirmDelete = async () => {
        try {
            await axios.delete(`http://localhost:8000/api/rack_levels/${rackLevelId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            navigate('/rack-levels');
        } catch (error) {
            handleError(error, setError);
        } finally {
            setOpenDialog(false);
        }
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    if (!rackLevel) {
        return <Typography variant="h6" color="error">Rack Level not found</Typography>;
    }

    const getSlotColor = (slot) => {
        if (!slot.is_active) {
            return '#b0bec5';
        }
        if (slot.is_active && !slot.stock) {
            return '#4caf50';
        }
        if (slot.is_active && slot.stock) {
            return '#f44336';
        }
    };

    return (
      <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static" className={`app-bar ${themeMode}`}>
              <Toolbar>
                  <Button color="inherit" component={Link} to="/">Home</Button>
                  {isStaff && (
                      <>
                          <Button color="inherit" onClick={handleUpdateClick}>
                              Update Rack Level
                          </Button>
                          <Button
                              color="inherit"
                              onClick={handleDeleteClick}
                              sx={{ ml: 2 }}
                              style={{ color: 'red' }}
                          >
                              Delete Rack Level
                          </Button>
                      </>
                  )}
              </Toolbar>
          </AppBar>

          <Grid container spacing={3} sx={{ mt: 3 }}>
              <Grid item xs={12}>
                  <Card className={`card ${themeMode}`} sx={{ padding: 3 }}>
                      <CardContent>
                          <Typography variant="h4" gutterBottom>
                              Rack Level: {rackLevel.rack_level_number}
                          </Typography>
                          <Typography variant="body1">Description: {rackLevel.description}</Typography>
                          <Typography variant="body1">Max Weight: {rackLevel.max_weight}</Typography>
                          <Typography variant="body1">Available Weight: {rackLevel.available_weight}</Typography>
                          <Typography variant="body1">Occupied Weight: {rackLevel.occupied_weight}</Typography>
                          <Typography variant="body1">Max Slots: {rackLevel.max_slots}</Typography>
                          <Typography variant="body1">Available Slots: {rackLevel.available_slots}</Typography>
                          <Typography variant="body1">Occupied Slots: {rackLevel.occupied_slots}</Typography>
                      </CardContent>
                  </Card>

                  {(isStaff || canMoveStocks) && rackLevel.rack_level_slots && (
                      <Box sx={{ mt: 3 }}>
                          <Typography variant="h6" gutterBottom>
                              Rack Level Slots:
                          </Typography>
                          <Grid container spacing={2}>
                              {rackLevel.rack_level_slots
                              .slice() 
                              .sort((a, b) => a.rack_level_slot_number - b.rack_level_slot_number)
                              .map((slot, index) => (
                                  <Grid item xs={3} key={index}>
                                      <Card
                                          sx={{
                                              backgroundColor: getSlotColor(slot),
                                              height: '100%',
                                              cursor: 'pointer',
                                          }}
                                          onClick={() => navigate(`/rack-level-slot/${slot.id}`)}
                                      >
                                          <CardContent>
                                              <Typography variant="body2">
                                                  Slot {index + 1} - {slot.is_active ? 'Active' : 'Inactive'}
                                              </Typography>
                                              {slot.stock && (
                                                  <>
                                                      <Typography variant="body2">Stock ID: {slot.stock.id}</Typography>
                                                      <Typography variant="body2">Weight: {slot.stock.weight}</Typography>
                                                  </>
                                              )}
                                          </CardContent>
                                      </Card>
                                  </Grid>
                              ))}
                          </Grid>
                      </Box>
                  )}

                  <Button onClick={handleAddStock} variant="contained" color="primary" sx={{ mt: 3 }}>
                      Add Stock
                  </Button>
              </Grid>
          </Grid>

            <Dialog open={isAddStockDialogOpen} onClose={() => setAddStockDialogOpen(false)}>
                <DialogTitle>Select a source to move the stock from</DialogTitle>
                <DialogContent>
                    <FormControl component="fieldset">
                        <RadioGroup value={stockSourceType} onChange={(e) => setStockSourceType(e.target.value)}>
                            <FormControlLabel value="waitingRoom" control={<Radio />} label="Waiting Room" />
                            <FormControlLabel value="rackLevel" control={<Radio />} label="Rack Level" />
                        </RadioGroup>
                    </FormControl>

                    {stockSourceType === 'waitingRoom' && (
                        <FormControl fullWidth sx={{ mt: 2 }}>
                            <InputLabel>Select a Waiting Room</InputLabel>
                            <Select
                                value={selectedSourceWaitingRoom}
                                onChange={(e) => setSelectedSourceWaitingRoom(e.target.value)}
                            >
                                {sourceWaitingRooms.map((room) => (
                                    <MenuItem key={room.id} value={room.id}>
                                        {room.name} (Available Stock Weight: {room.available_stock_weight}, Available Slots: {room.available_slots})
                                    </MenuItem>
                                ))}
                            </Select>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={() => fetchStocks(selectedSourceWaitingRoom, 'waitingRoom')}
                                sx={{ mt: 2 }}
                            >
                                Fetch Stocks
                            </Button>
                        </FormControl>
                    )}

                    {stockSourceType === 'rackLevel' && (
                        <>
                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>Select a Section</InputLabel>
                                <Select
                                    value={selectedSection}
                                    onChange={(e) => {
                                        setSelectedSection(e.target.value);
                                        fetchRacks(e.target.value);
                                    }}
                                >
                                    {sections.map((section) => (
                                        <MenuItem key={section.id} value={section.id}>
                                            {section.section_name} (Available Weight: {section.available_weight}, Max Weight: {section.max_weight}, Max Racks: {section.max_racks})
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>Select a Rack</InputLabel>
                                <Select
                                    value={selectedRack}
                                    onChange={(e) => {
                                        setSelectedRack(e.target.value);
                                        fetchRackLevels(e.target.value);
                                    }}
                                >
                                    {racks.map((rack) => (
                                        <MenuItem key={rack.id} value={rack.id}>
                                            Rack: {rack.rack_name} (Available Weight: {rack.available_weight}, Max Weight: {rack.max_weight}, Max Levels: {rack.max_levels})
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>Select a Rack Level</InputLabel>
                                <Select
                                    value={selectedRackLevel}
                                    onChange={(e) => setSelectedRackLevel(e.target.value)}
                                >
                                    {rackLevels.map((level) => (
                                        <MenuItem key={level.id} value={level.id}>
                                            Level #{level.rack_level_number} (Available Weight: {level.available_weight}, Available Slots: {level.available_slots}, Max Slots: {level.max_slots})
                                        </MenuItem>
                                    ))}
                                </Select>
                                <Button
                                    variant="outlined"
                                    color="primary"
                                    onClick={() => fetchStocks(selectedRackLevel, 'rackLevel')}
                                    sx={{ mt: 2 }}
                                >
                                    Fetch Stocks
                                </Button>
                            </FormControl>
                        </>
                    )}

                    {fetchedStocks.length > 0 && (
                        <List sx={{ mt: 2 }}>
                            {fetchedStocks.map((stock) => (
                                <ListItem
                                    key={stock.id}
                                    button
                                    selected={selectedStock === stock}
                                    onClick={() => setSelectedStock(stock)}
                                >
                                    <ListItemText primary={`${stock.product.name} (Weight: ${stock.weight}, Count: ${stock.product_count})`} />
                                </ListItem>
                            ))}
                        </List>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setAddStockDialogOpen(false)} color="secondary">
                        Cancel
                    </Button>
                    <Button onClick={handleConfirmAddStock} color="primary" disabled={!selectedStock}>
                        Confirm
                    </Button>
                </DialogActions>
            </Dialog>

            <Dialog open={openDialog} onClose={handleCloseDialog}>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogContent>
                    <Typography>Are you sure you want to delete this rack level?</Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} color="secondary">
                        Cancel
                    </Button>
                    <Button onClick={handleConfirmDelete} color="primary">
                        Confirm
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default RackLevelDetail;
