import React, { useState, useEffect } from 'react';
import { TextField, Button, Typography, Container, MenuItem } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { handleError } from '../ErrorHandler';

const CreateRack = ({ themeMode }) => {
  const [rackName, setRackName] = useState('');
  const [maxWeight, setMaxWeight] = useState(0);
  const [maxLevels, setMaxLevels] = useState(0);
  const [sectionId, setSectionId] = useState('');
  const [sections, setSections] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSections = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/sections/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        setSections(response.data.results || []);
      } catch (error) {
        handleError(error, setError);
      }
    };

    fetchSections();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/racks/', {
        rack_name: rackName,
        max_weight: maxWeight,
        max_levels: maxLevels,
        section_id: sectionId,
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      navigate('/racks');
    } catch (error) {
      handleError(error, setError);
    }
  };

  return (
    <Container maxWidth="sm" className={`container ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Create Rack</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Rack Name"
          fullWidth
          value={rackName}
          onChange={(e) => setRackName(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          label="Max Weight"
          type="number"
          fullWidth
          value={maxWeight}
          onChange={(e) => setMaxWeight(parseFloat(e.target.value))}
          margin="normal"
          required
        />
        <TextField
          label="Max Levels"
          type="number"
          fullWidth
          value={maxLevels}
          onChange={(e) => setMaxLevels(parseInt(e.target.value))}
          margin="normal"
          required
        />
        <TextField
          select
          label="Select Section"
          fullWidth
          value={sectionId}
          onChange={(e) => setSectionId(e.target.value)}
          margin="normal"
          required
        >
          {sections.map((section) => (
            <MenuItem key={section.id} value={section.id}>
              {section.section_name} (Available Weight: {section.available_weight}, Available Racks: {section.available_racks})
            </MenuItem>
          ))}
        </TextField>
        {error && <Typography color="error">{error}</Typography>}
        <Button type="submit" variant="contained" color="primary" fullWidth>
          Create Rack
        </Button>
      </form>
    </Container>
  );
};

export default CreateRack;
