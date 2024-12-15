import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Typography, Card, CardContent, CardHeader, CircularProgress, Grid, AppBar, Toolbar, Button, Box, Pagination, TextField, MenuItem, Select, InputLabel, FormControl, Divider
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

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

const SectionsList = ({ themeMode }) => {
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [size, setSize] = useState(10);
  const [filters, setFilters] = useState({
    available_weight: { value: '', operator: 'eq', sort: '' },
    occupied_weight: { value: '', operator: 'eq', sort: '' },
    reserved_weight: { value: '', operator: 'eq', sort: '' },
    weight_to_reserve: { value: '', operator: 'eq', sort: '' },
    available_racks: { value: '', operator: 'eq', sort: '' },
    occupied_racks: { value: '', operator: 'eq', sort: '' }
  });

  const navigate = useNavigate();
  const isStaff = AuthService.getUserRole();

  const fetchSections = async (page, size, appliedFilters) => {
    try {
      setLoading(true);
      let endpoint = `http://localhost:8000/api/sections/?page=${page}&size=${size}`;

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
      setSections(response.data.results);
      setTotalPages(Math.ceil(response.data.total / size));
    } catch (error) {
      handleError(error, setError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSections(page, size, filters);
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
    fetchSections(page, size, filters);
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
            <Button color="inherit" component={Link} to="/section/create">
              Create Section
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Grid container spacing={3} sx={{ mt: 3 }}>
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
                  <Grid item xs={12}>
                    <TextField
                      label={key.replace(/_/g, ' ')}
                      name={`${key}.value`}
                      value={filter.value}
                      onChange={handleFilterChange}
                      fullWidth
                    />
                  </Grid>
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

        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {sections.map(section => (
              <Grid item xs={12} key={section.id}>
                <Card className={`card ${themeMode}`}>
                  <CardHeader
                    title={
                        <Typography 
                        variant="h6" 
                        fontWeight="bold"
                        component={Link} 
                        to={`/section/${section.id}`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                      >
                        {section.section_name || 'Unnamed Section'}
                      </Typography>                      
                    }
                  />
                  <CardContent>
                    <Typography variant="body1">Max Weight: {section.max_weight}</Typography>
                    <Typography variant="body1">Max Racks: {section.max_racks}</Typography>
                    <Typography variant="body1">Available Weight: {section.available_weight}</Typography>
                    <Typography variant="body1">Occupied Weight: {section.occupied_weight}</Typography>
                    <Typography variant="body1">Reserved Weight: {section.reserved_weight}</Typography>
                    <Typography variant="body1">Weight to Reserve: {section.weight_to_reserve}</Typography>
                    <Typography variant="body1">Available Racks: {section.available_racks}</Typography>
                    <Typography variant="body1">Occupied Racks: {section.occupied_racks}</Typography>
                    <Typography variant="body2">Created At: {section.created_at || 'N/A'}</Typography>
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
            <Pagination
              count={totalPages}
              page={page}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SectionsList;
