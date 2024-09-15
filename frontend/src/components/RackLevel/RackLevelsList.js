import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, TextField, MenuItem, Select, InputLabel, FormControl, Divider
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import AuthService from '../../services/AuthService'; // For role checking
import { handleError } from '../ErrorHandler'; // Error handler

const operatorOptions = [
  { value: 'eq', label: 'Equals (=)' },
  { value: 'ne', label: 'Not Equals (!=)' },
  { value: 'gt', label: 'Greater Than (>)' },
  { value: 'lt', label: 'Less Than (<)' },
  { value: 'ge', label: 'Greater or Equal (>=)' },
  { value: 'le', label: 'Less or Equal (<=)' }
];

const sortOptions = [
  { value: '', label: 'No Sort' },
  { value: 'asc', label: 'Ascending' },
  { value: 'desc', label: 'Descending' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const RackLevelsList = ({ themeMode }) => {
  const [rackLevels, setRackLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [size, setSize] = useState(10);
  const [filters, setFilters] = useState({
    max_weight: { value: '', operator: 'eq', sort: '' },
    max_slots: { value: '', operator: 'eq', sort: '' },
    available_weight: { value: '', operator: 'eq', sort: '' },
    occupied_weight: { value: '', operator: 'eq', sort: '' },
    available_slots: { value: '', operator: 'eq', sort: '' },
    occupied_slots: { value: '', operator: 'eq', sort: '' },
    active_slots: { value: '', operator: 'eq', sort: '' },
    inactive_slots: { value: '', operator: 'eq', sort: '' }
  });

  const navigate = useNavigate();
  const isStaff = AuthService.getUserRole();

  const fetchRackLevels = async (page, size, appliedFilters) => {
    try {
      setLoading(true);
      let endpoint = `http://localhost:8000/api/rack_levels/?page=${page}&size=${size}`;

      // Append filter and sort params
      for (const [key, filter] of Object.entries(appliedFilters)) {
        if (filter.value) {
          endpoint += `&${key}__${filter.operator}=${filter.value}`;
        }
        if (filter.sort) {
          endpoint += `&sort=${key}__${filter.sort}`;
        }
      }

      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setRackLevels(response.data.results);
      setTotalPages(Math.ceil(response.data.total / size));
    } catch (error) {
      handleError(error, setError); 
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRackLevels(page, size, filters);
  }, [page, size]);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleSizeChange = (event) => {
    setSize(event.target.value);
    setPage(1); 
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const [field, type] = name.split('.');
    setFilters(prevFilters => ({
      ...prevFilters,
      [field]: { ...prevFilters[field], [type]: value }
    }));
  };

  const handleFilterApply = () => {
    fetchRackLevels(page, size, filters);
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {isStaff && (
            <Button color="inherit" component={Link} to="/rack-level/create">
              Create Rack Level
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {/* Filters Section */}
        <Grid item xs={12} md={4}>
          <Box sx={{ padding: 2, borderRight: '1px solid #ddd' }}>
            <Typography variant="h6" gutterBottom>Filters</Typography>
            <Divider sx={{ mb: 2 }} />

            {Object.entries(filters).map(([key, filter]) => (
              <Box key={key} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  <strong>{key.replace(/_/g, ' ')}</strong>
                </Typography>
                <Grid container spacing={2}>
                  {/* Value Input */}
                  <Grid item xs={12}>
                    <TextField
                      label={key.replace(/_/g, ' ')}
                      name={`${key}.value`}
                      value={filter.value}
                      onChange={handleFilterChange}
                      fullWidth
                    />
                  </Grid>
                  {/* Operator Select */}
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Operator</InputLabel>
                      <Select
                        name={`${key}.operator`}
                        value={filter.operator}
                        onChange={handleFilterChange}
                        label="Operator"
                      >
                        {operatorOptions.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  {/* Sort By Select */}
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Sort By</InputLabel>
                      <Select
                        name={`${key}.sort`}
                        value={filter.sort}
                        onChange={handleFilterChange}
                        label="Sort By"
                      >
                        {sortOptions.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>
            ))}
            <Button variant="contained" color="primary" onClick={handleFilterApply}>
              Apply Filters
            </Button>
          </Box>
        </Grid>

        {/* Rack Levels List Section */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {rackLevels.map(level => (
              <Grid item xs={12} key={level.id}>
                <Card className={`card ${themeMode}`}>
                  <CardHeader
                    title={
                      <Typography 
                        variant="h6" 
                        fontWeight="bold"
                        component={Link} 
                        to={`/rack-level/${level.id}`} 
                        style={{ textDecoration: 'none', color: 'inherit' }} 
                      >
                        Rack Level #{level.rack_level_number}
                      </Typography>
                    }
                  />
                  <CardContent>
                    <Typography variant="body1">Max Weight: {level.max_weight}</Typography>
                    <Typography variant="body1">Max Slots: {level.max_slots}</Typography>
                    <Typography variant="body1">Available Weight: {level.available_weight}</Typography>
                    <Typography variant="body1">Occupied Weight: {level.occupied_weight}</Typography>
                    <Typography variant="body1">Available Slots: {level.available_slots}</Typography>
                    <Typography variant="body1">Occupied Slots: {level.occupied_slots}</Typography>
                    <Typography variant="body1">Active Slots: {level.active_slots}</Typography>
                    <Typography variant="body1">Inactive Slots: {level.inactive_slots}</Typography>
                    <Typography variant="body2">Created At: {level.created_at || 'N/A'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Items per page</InputLabel>
              <Select
                value={size}
                onChange={handleSizeChange}
                label="Items per page"
              >
                {pageSizeOptions.map(option => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Pagination count={totalPages} page={page} onChange={handlePageChange} color="primary" />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RackLevelsList;
