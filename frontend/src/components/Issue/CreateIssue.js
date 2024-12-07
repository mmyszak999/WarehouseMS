import React, { useState, useEffect } from 'react';
import {
  TextField, Button, Box, Typography, Container, MenuItem, AppBar, Toolbar,
  FormControl, InputLabel, Select, CircularProgress, Snackbar, Alert, RadioGroup, FormControlLabel, Radio
} from '@mui/material';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateIssue = () => {
  const [waitingRooms, setWaitingRooms] = useState([]);
  const [sections, setSections] = useState([]);
  const [racks, setRacks] = useState([]);
  const [rackLevels, setRackLevels] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [formData, setFormData] = useState({
    stock_entries: [],
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWaitingRooms = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/waiting_rooms/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        setWaitingRooms(response.data.results || []);
        setLoading(false);
      } catch (error) {
        handleError(error, setError);
        setLoading(false);
      }
    };

    fetchWaitingRooms();
    fetchSections();
  }, []);

  const fetchSections = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/sections/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setSections(response.data.results || []);
    } catch (error) {
      handleError(error, setError);
    }
  };

  const fetchRacks = async (sectionId, index) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/sections/${sectionId}/racks/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setFormData(prevState => {
        const updatedEntries = [...prevState.stock_entries];
        updatedEntries[index] = { ...updatedEntries[index], racks: response.data.results || [] };
        return { ...prevState, stock_entries: updatedEntries };
      });
    } catch (error) {
      handleError(error, setError);
    }
  };

  const fetchRackLevels = async (rackId, index) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/racks/${rackId}/rack_levels/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setFormData(prevState => {
        const updatedEntries = [...prevState.stock_entries];
        updatedEntries[index] = { ...updatedEntries[index], rackLevels: response.data.results || [] };
        return { ...prevState, stock_entries: updatedEntries };
      });
    } catch (error) {
      handleError(error, setError);
    }
  };

  const fetchStocks = async (locationId, isRackLevel, index) => {
    try {
      const endpoint = isRackLevel
        ? `http://localhost:8000/api/rack_levels/${locationId}/slots/`
        : `http://localhost:8000/api/waiting_rooms/${locationId}/`;
  
      const response = await axios.get(endpoint, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
  
      let stocks = [];
      console.log(response.data, "ww");
      if (isRackLevel) {
        response.data.results.forEach(slot => {
          if (slot.stock) {
            stocks.push(slot.stock);
          }
        });
      } else {
        console.log(response.data.stocks, "xx");
        stocks = response.data.stocks || [];
      }
  
      setFormData(prevState => {
        const updatedEntries = [...prevState.stock_entries];
        updatedEntries[index] = {
          ...updatedEntries[index],
          stocks: stocks
        };
        return { ...prevState, stock_entries: updatedEntries };
      });
    } catch (error) {
      handleError(error, setError);
    }
  };
  
  const handleLocationChange = (e, index) => {
    const { value } = e.target;
    const locationType = formData.stock_entries[index].locationType;
  
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      if (locationType === 'waiting_room') {
        updatedEntries[index] = { ...updatedEntries[index], waiting_room_id: value, rack_level_id: '', stock_id: '' };
      } else if (locationType === 'rack_level') {
        updatedEntries[index] = { ...updatedEntries[index], rack_level_id: value, waiting_room_id: '', stock_id: '' };
      }
      return { ...prevState, stock_entries: updatedEntries };
    });
  
    if (value) {
      fetchStocks(value, locationType === 'rack_level', index);
    }
  };  
  
  

  const handleSectionChange = (e, index) => {
    const sectionId = e.target.value;
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      updatedEntries[index] = { ...updatedEntries[index], section_id: sectionId, rack_id: '', rack_level_id: '' };
      return { ...prevState, stock_entries: updatedEntries };
    });
    fetchRacks(sectionId, index);
  };

  const handleRackChange = (e, index) => {
    const rackId = e.target.value;
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      updatedEntries[index] = { ...updatedEntries[index], rack_id: rackId, rack_level_id: '' };
      return { ...prevState, stock_entries: updatedEntries };
    });
    fetchRackLevels(rackId, index);
  };

  const handleRackLevelChange = (e, index) => {
    const rackLevelId = e.target.value;
    setFormData(prevState => {
      const updatedEntries = [...prevState.stock_entries];
      updatedEntries[index] = { ...updatedEntries[index], rack_level_id: rackLevelId, stock_id: '' };
      return { ...prevState, stock_entries: updatedEntries };
    });
    if (rackLevelId) {
      fetchStocks(rackLevelId, true, index);
    }
  };

  const handleAddStock = () => {
    setFormData(prevState => ({
      ...prevState,
      stock_entries: [...prevState.stock_entries, { stock_id: '', locationType: 'waiting_room', waiting_room_id: '', rack_level_id: '', racks: [], rackLevels: [] }]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const dataToSubmit = {
      stock_ids: formData.stock_entries.map(entry => ({
        id: entry.stock_id
      })),
      description: formData.description
    };

    try {
      await axios.post('http://localhost:8000/api/issues/', dataToSubmit, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setSuccess('Issue created successfully!');
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
        <Typography component="h1" variant="h5">Create Issue</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          {loading ? (
            <CircularProgress />
          ) : (
            <>
              {formData.stock_entries.map((entry, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <RadioGroup
                    value={entry.locationType}
                    onChange={(e) => {
                      const newLocationType = e.target.value;
                      setFormData(prevState => ({
                        ...prevState,
                        stock_entries: prevState.stock_entries.map((entry, i) =>
                          i === index ? { ...entry, locationType: newLocationType, waiting_room_id: '', rack_level_id: '', stock_id: '' } : entry
                        )
                      }));
                      setStocks([]);
                    }}
                    sx={{ mb: 2 }}
                  >
                    <FormControlLabel value="waiting_room" control={<Radio />} label="Waiting Room" />
                    <FormControlLabel value="rack_level" control={<Radio />} label="Rack Level" />
                  </RadioGroup>

                  {entry.locationType === 'waiting_room' && (
                    <FormControl fullWidth>
                      <InputLabel id={`waiting_room-label-${index}`}>Waiting Room</InputLabel>
                      <Select
                        labelId={`waiting_room-label-${index}`}
                        value={entry.waiting_room_id}
                        onChange={(e) => handleLocationChange(e, index)}
                      >
                        {waitingRooms.map(room => (
                          <MenuItem key={room.id} value={room.id}>
                            {`Name: ${room.name}, Available slots: ${room.available_slots}, Available Weight: ${room.available_stock_weight}, Max stocks: ${room.max_stocks}`}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}

                  {entry.locationType === 'rack_level' && (
                    <>
                      <FormControl fullWidth>
                        <InputLabel id={`section-label-${index}`}>Section</InputLabel>
                        <Select
                          labelId={`section-label-${index}`}
                          value={entry.section_id || ''}
                          onChange={(e) => handleSectionChange(e, index)}
                        >
                          {sections.map(section => (
                            <MenuItem key={section.id} value={section.id}>
                              {`Name: ${section.section_name}, Available Weight: ${section.available_weight}, Occupied Weight: ${section.occupied_weight}`}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      <FormControl fullWidth>
                        <InputLabel id={`rack-label-${index}`}>Rack</InputLabel>
                        <Select
                          labelId={`rack-label-${index}`}
                          value={entry.rack_id || ''}
                          onChange={(e) => handleRackChange(e, index)}
                        >
                          {entry.racks.map(rack => (
                            <MenuItem key={rack.id} value={rack.id}>
                              Rack: {rack.rack_name} (Available Weight: {rack.available_weight}, Max Weight: {rack.max_weight}, Max Levels: {rack.max_levels})
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      <FormControl fullWidth>
                        <InputLabel id={`rack-level-label-${index}`}>Rack Level</InputLabel>
                        <Select
                          labelId={`rack-level-label-${index}`}
                          value={entry.rack_level_id || ''}
                          onChange={(e) => handleRackLevelChange(e, index)}
                        >
                          {entry.rackLevels.map(level => (
                            <MenuItem key={level.id} value={level.id}>
                              Level #{level.rack_level_number} (Available Weight: {level.available_weight}, Available Slots: {level.available_slots}, Max Slots: {level.max_slots})
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                    </>
                  )}

{entry.stocks && entry.stocks.length > 0 && (
  <FormControl fullWidth>
    <InputLabel id={`stock-label-${index}`}>Stock</InputLabel>
    <Select
      labelId={`stock-label-${index}`}
      value={entry.stock_id || ''}
      onChange={(e) => {
        setFormData(prevState => {
          const updatedEntries = [...prevState.stock_entries];
          updatedEntries[index] = { ...updatedEntries[index], stock_id: e.target.value };
          return { ...prevState, stock_entries: updatedEntries };
        });
      }}
    >
      {entry.stocks.map(stock => (
        <MenuItem key={stock.id} value={stock.id}>
          {`${stock.product.name} (Weight: ${stock.weight}, Count: ${stock.product_count})`}
        </MenuItem>
      ))}
    </Select> 
  </FormControl>
)}

                </Box>
              ))}
              <Button onClick={handleAddStock} variant="contained" color="primary">Add Stock</Button>
              <TextField
                margin="normal"
                fullWidth
                id="description"
                label="Description"
                name="description"
                value={formData.description}
                onChange={(e) => setFormData(prevState => ({ ...prevState, description: e.target.value }))}
                autoComplete="description"
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                Create Issue
              </Button>
            </>
          )}
        </Box>
      </Box>
      {success && <Snackbar open autoHideDuration={6000} onClose={() => setSuccess(null)}><Alert onClose={() => setSuccess(null)} severity="success">{success}</Alert></Snackbar>}
      {error && <Snackbar open autoHideDuration={6000} onClose={() => setError(null)}><Alert onClose={() => setError(null)} severity="error">{error}</Alert></Snackbar>}
    </Container>
  );
};

export default CreateIssue;
