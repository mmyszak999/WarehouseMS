import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  CircularProgress, Typography, Grid, Card, CardContent, Box, AppBar, Toolbar, Button, Dialog, DialogTitle,
  DialogContent, DialogActions, FormControl, RadioGroup, FormControlLabel, Radio, Select, MenuItem, List, ListItem, ListItemText
} from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const RackLevelSlotDetail = ({ themeMode }) => {
  const { rackLevelSlotId } = useParams();
  const navigate = useNavigate();
  const [rackLevelSlot, setRackLevelSlot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isStaff = AuthService.getUserRole();
  const canMoveStocks = AuthService.canMoveStocks();

  // State related to adding stock
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

  const fetchRackLevelSlotDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setRackLevelSlot(response.data);
    } catch (error) {
      handleError(error, setError); // Handle errors
    } finally {
      setLoading(false);
    }
  };

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
    try {
      const response = await axios.get(`http://localhost:8000/api/racks/${rackId}/rack_levels/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setRackLevels(response.data.results);
    } catch (error) {
      handleError(error, setError);
    }
  }, [token]);

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

  const handleAddStock = () => {
    setAddStockDialogOpen(true);
    setFetchedStocks([]);
  };

  const handleConfirmAddStock = async () => {
    if (selectedStock) {
      try {
        await axios.patch(`http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}/add-stock`, {
          id: selectedStock.id,
          source_type: stockSourceType,
          source_id: stockSourceType === 'waitingRoom' ? selectedSourceWaitingRoom : selectedRackLevel
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setAddStockDialogOpen(false);
        setSelectedStock(null);
        fetchRackLevelSlotDetails();
      } catch (error) {
        handleError(error, setError);
      }
    }
  };

  useEffect(() => {
    fetchRackLevelSlotDetails();
    fetchWaitingRooms();
    fetchSections();
  }, [rackLevelSlotId, fetchWaitingRooms, fetchSections]);

  const handleActivateDeactivate = async () => {
    const url = rackLevelSlot.is_active
      ? `http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}/deactivate`
      : `http://localhost:8000/api/rack-level-slots/${rackLevelSlotId}/activate`;

    try {
      await axios.patch(url, {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      fetchRackLevelSlotDetails();
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  if (!rackLevelSlot) {
    return <Typography variant="h6" color="error">Rack Level Slot not found</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <Button
              color="inherit"
              onClick={() => navigate(`/rack-level-slot/${rackLevelSlotId}/update`)}
            >
              Update Rack Level Slot
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12}>
          <Card className={`card ${themeMode}`} sx={{ padding: 3 }}>
            <CardContent>
              <Typography variant="h4" gutterBottom>
                {rackLevelSlot.description}
              </Typography>
              <Typography variant="body1">Slot number in the rack level: {rackLevelSlot.rack_level_slot_number}</Typography>
              <Typography variant="body1">Active: {rackLevelSlot.is_active ? 'Yes' : 'No'}</Typography>
              <Typography variant="body1">Created At: {new Date(rackLevelSlot.created_at).toLocaleDateString()}</Typography>

              {isStaff && (
                <Button
                  variant="contained"
                  color={rackLevelSlot.is_active ? 'error' : 'success'}
                  onClick={handleActivateDeactivate}
                  sx={{ mb: 2 }}
                >
                  {rackLevelSlot.is_active ? 'Deactivate' : 'Activate'}
                </Button>
              )}

              {rackLevelSlot.stock && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Stock Information:
                  </Typography>
                  <Typography variant="body1">Product Name: {rackLevelSlot.stock.product.name}</Typography>
                  <Typography variant="body1">Product Description: {rackLevelSlot.stock.product.description}</Typography>
                  <Typography variant="body1">Weight: {rackLevelSlot.stock.weight}</Typography>
                  <Typography variant="body1">Product Count: {rackLevelSlot.stock.product_count}</Typography>
                </>
              )}

              {/* Add Stock Button */}
              {(isStaff || canMoveStocks) && 
  rackLevelSlot.is_active && !rackLevelSlot.stock && (
    <Button 
      onClick={handleAddStock} 
      variant="contained" 
      color="primary" 
      sx={{ mt: 3 }}>
      Add Stock
    </Button>
)}

            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Stock Dialog */}
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
            <Select
              value={selectedSourceWaitingRoom}
              onChange={(e) => {
                setSelectedSourceWaitingRoom(e.target.value);
                fetchStocks(e.target.value, 'waitingRoom');
              }}
              displayEmpty
              fullWidth
              sx={{ mt: 2 }}
            >
              <MenuItem value="" disabled>Select Waiting Room</MenuItem>
              {sourceWaitingRooms.map(room => (
                <MenuItem key={room.id} value={room.id}>
                  {room.name} (Available Stock Weight: {room.available_stock_weight}, Available Slots: {room.available_slots})
                </MenuItem>
              ))}
            </Select>
          )}

          {stockSourceType === 'rackLevel' && (
            <>
              <Select
                value={selectedSection}
                onChange={(e) => {
                  setSelectedSection(e.target.value);
                  fetchRacks(e.target.value);
                }}
                displayEmpty
                fullWidth
                sx={{ mt: 2 }}
              >
                <MenuItem value="" disabled>Select Section</MenuItem>
                {sections.map(section => (
                  <MenuItem key={section.id} value={section.id}>
                    {section.section_name} (Available Weight: {section.available_weight}, Max Weight: {section.max_weight}, Max Racks: {section.max_racks})
                  </MenuItem>
                ))}
              </Select>

              <Select
                value={selectedRack}
                onChange={(e) => {
                  setSelectedRack(e.target.value);
                  fetchRackLevels(e.target.value);
                }}
                displayEmpty
                fullWidth
                sx={{ mt: 2 }}
              >
                <MenuItem value="" disabled>Select Rack</MenuItem>
                {racks.map(rack => (
                  <MenuItem key={rack.id} value={rack.id}>
                    Rack: {rack.rack_name} (Available Weight: {rack.available_weight}, Max Weight: {rack.max_weight}, Max Levels: {rack.max_levels})
                  </MenuItem>
                ))}
              </Select>

              <Select
                value={selectedRackLevel}
                onChange={(e) => {
                  setSelectedRackLevel(e.target.value);
                  fetchStocks(e.target.value, 'rackLevel');
                }}
                displayEmpty
                fullWidth
                sx={{ mt: 2 }}
              >
                <MenuItem value="" disabled>Select Rack Level</MenuItem>
                {rackLevels.map(level => (
                  <MenuItem key={level.id} value={level.id}>
                    Level #{level.rack_level_number} (Available Weight: {level.available_weight}, Available Slots: {level.available_slots}, Max Slots: {level.max_slots})
                  </MenuItem>
                ))}
              </Select>
            </>
          )}

          {/* Stock List */}
          <List>
            {fetchedStocks.map(stock => (
              <ListItem
                key={stock.id}
                button
                selected={selectedStock && selectedStock.id === stock.id}
                onClick={() => setSelectedStock(stock)}
              >
                <ListItemText primary={`${stock.product.name} (Weight: ${stock.weight}, Count: ${stock.product_count})`} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddStockDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmAddStock} disabled={!selectedStock} color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RackLevelSlotDetail;
