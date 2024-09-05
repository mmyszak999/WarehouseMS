import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, Typography, List, ListItem, ListItemText, CircularProgress, Button, Grid, TextField, MenuItem, Select, InputLabel, FormControl, Divider, Pagination, AppBar, Toolbar } from '@mui/material';
import { Link } from 'react-router-dom';
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

const booleanOptions = [
  { value: '', label: 'No Filter' },
  { value: 'true', label: 'Yes' },
  { value: 'false', label: 'No' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const AllStocksList = ({ themeMode }) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    weight: { value: '', operator: 'eq', sort: '' },
    product_count: { value: '', operator: 'eq', sort: '' },
    is_issued: { value: '' }
  });

  const token = localStorage.getItem('token');

  const fetchStocks = async () => {
    try {
      setLoading(true);
      let endpoint = `http://localhost:8000/api/stocks/all?page=${page}&size=${size}`;

      for (const [key, filter] of Object.entries(filters)) {
        if (filter.value) {
          if (key === 'is_issued') {
            endpoint += `&${key}=${filter.value}`;
          } else {
            endpoint += `&${key}__${filter.operator}=${filter.value}`;
          }
        }
        if (filter.sort) {
          endpoint += `&sort=${key}__${filter.sort}`;
        }
      }

      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setStocks(response.data.results);
      setTotalPages(Math.ceil(response.data.total / size));
    } catch (error) {
      handleError(error, setError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks();
  }, [page, size, filters]);

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

  const handleBooleanFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: { value }
    }));
  };

  const handleFilterApply = () => {
    fetchStocks();
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* AppBar with Home Link */}
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
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
                  {key !== 'is_issued' && (
                    <>
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
                    </>
                  )}
                  {key === 'is_issued' && (
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Is Issued</InputLabel>
                        <Select
                          name="is_issued"
                          value={filter.value}
                          onChange={handleBooleanFilterChange}
                          fullWidth
                        >
                          {booleanOptions.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                  )}
                </Grid>
              </Box>
            ))}
            <Button variant="contained" color="primary" onClick={handleFilterApply}>
              Apply Filters
            </Button>
          </Box>
        </Grid>

        {/* All Stocks List Section */}
        <Grid item xs={12} md={8}>
          <List>
            {stocks.map((stock) => (
              <ListItem key={stock.id}>
                <ListItemText
                  primary={<Link to={`/stock/all/${stock.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    Product: {stock.product.name}
                  </Link>}
                  secondary={`Weight: ${stock.weight}, Product Count: ${stock.product_count}, Recepted by: ${stock.reception?.user.first_name} ${stock.reception?.user.last_name}`}
                />
              </ListItem>
            ))}
          </List>

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

export default AllStocksList;
