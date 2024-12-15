import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Box, Button, CircularProgress, MenuItem, Select, TextField, Typography } from '@mui/material';
import { handleError } from '../ErrorHandler';

const CreateRackLevel = () => {
  const [sections, setSections] = useState([]);
  const [racks, setRacks] = useState([]);
  const [selectedSection, setSelectedSection] = useState('');
  const [selectedRack, setSelectedRack] = useState('');
  const [rackLevelData, setRackLevelData] = useState({
    rack_level_number: 0,
    description: '',
    max_weight: 0,
    max_slots: 0,
    rack_id: '',
  });
  const [loadingSections, setLoadingSections] = useState(true);
  const [loadingRacks, setLoadingRacks] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSections = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/sections/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setSections(response.data.results);
      } catch (error) {
        handleError(error, setError);
      } finally {
        setLoadingSections(false);
      }
    };
    fetchSections();
  }, []);

  useEffect(() => {
    if (selectedSection) {
      const fetchRacks = async () => {
        setLoadingRacks(true);
        try {
          const response = await axios.get(`http://localhost:8000/api/sections/${selectedSection}/racks`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
          });
          setRacks(response.data.results);
        } catch (error) {
          handleError(error, setError);
        } finally {
          setLoadingRacks(false);
        }
      };
      fetchRacks();
    }
  }, [selectedSection]);

  const handleSectionChange = (event) => {
    setSelectedSection(event.target.value);
    setSelectedRack('');
    setRacks([]);
  };

  const handleRackChange = (event) => {
    const rackId = event.target.value;
    setSelectedRack(rackId);
    setRackLevelData({ ...rackLevelData, rack_id: rackId });
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setRackLevelData({ ...rackLevelData, [name]: value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/rack_levels/', rackLevelData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      navigate(`/rack-levels`);
    } catch (error) {
      handleError(error, setError);
    }
  };

  if (loadingSections) {
    return <CircularProgress />;
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h4">Create Rack Level</Typography>

      {error && <Typography variant="h6" color="error">{error}</Typography>}

      <Select
        fullWidth
        value={selectedSection}
        onChange={handleSectionChange}
        displayEmpty
        sx={{ mt: 2, mb: 2 }}
      >
        <MenuItem value="" disabled>Select Section</MenuItem>
        {sections.map((section) => (
          <MenuItem key={section.id} value={section.id}>
            {section.section_name} (Available Weight: {section.available_weight}, Available Racks: {section.available_racks})
          </MenuItem>
        ))}
      </Select>

      {loadingRacks ? (
        <CircularProgress />
      ) : (
        <Select
          fullWidth
          value={selectedRack}
          onChange={handleRackChange}
          displayEmpty
          disabled={!selectedSection}
          sx={{ mt: 2, mb: 2 }}
        >
          <MenuItem value="" disabled>Select Rack</MenuItem>
          {racks.map((rack) => (
            <MenuItem key={rack.id} value={rack.id}>
              {rack.rack_name} (Available Weight: {rack.available_weight}, Available Levels: {rack.available_levels})
            </MenuItem>
          ))}
        </Select>
      )}

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          name="rack_level_number"
          label="Rack Level Number"
          type="number"
          value={rackLevelData.rack_level_number}
          onChange={handleInputChange}
          sx={{ mt: 2 }}
        />
        <TextField
          fullWidth
          name="description"
          label="Description"
          value={rackLevelData.description}
          onChange={handleInputChange}
          sx={{ mt: 2 }}
        />
        <TextField
          fullWidth
          name="max_weight"
          label="Max Weight"
          type="number"
          value={rackLevelData.max_weight}
          onChange={handleInputChange}
          sx={{ mt: 2 }}
        />
        <TextField
          fullWidth
          name="max_slots"
          label="Max Slots"
          type="number"
          value={rackLevelData.max_slots}
          onChange={handleInputChange}
          sx={{ mt: 2 }}
        />
        <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
          Create Rack Level
        </Button>
      </form>
    </Box>
  );
};

export default CreateRackLevel;
