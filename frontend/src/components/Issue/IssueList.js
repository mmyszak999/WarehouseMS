import React, { useState, useEffect } from 'react';
import { Container, Typography, List, ListItem, ListItemText, CircularProgress, AppBar, Toolbar, Button, Box, Grid, TextField, FormControl, Divider, MenuItem, Select, InputLabel } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { format } from 'date-fns';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const sortOptions = [
  { value: '', label: 'No Sort' },
  { value: 'asc', label: 'Ascending' },
  { value: 'desc', label: 'Descending' }
];

const pageSizeOptions = [5, 10, 15, 20, 25, 50, 100];

const IssuesList = ({ themeMode }) => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const [filterInputs, setFilterInputs] = useState({
    issue_date: { value: { start: null, end: null }, sort: '' },
    description: { value: '', operator: 'eq', sort: '' }
  });

  const [filters, setFilters] = useState({
    issue_date: { value: { start: null, end: null }, sort: '' },
    description: { value: '', operator: 'eq', sort: '' }
  });

  const token = localStorage.getItem('token');
  const canIssueStocks = AuthService.canIssueStocks();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchIssues = async () => {
      try {
        setLoading(true);
        let endpoint = `http://localhost:8000/api/issues/?page=${page}&size=${size}`;

        if (filters.issue_date.value.start) {
          const startDate = format(filters.issue_date.value.start, 'yyyy-MM-dd');
          endpoint += `&issue_date__ge=${startDate}`;
        }
        if (filters.issue_date.value.end) {
          const endDate = format(filters.issue_date.value.end, 'yyyy-MM-dd');
          endpoint += `&issue_date__le=${endDate}`;
        }
        if (filters.description.value) {
          endpoint += `&description__${filters.description.operator}=${filters.description.value}`;
        }
        if (filters.issue_date.sort) {
          endpoint += `&sort=issue_date__${filters.issue_date.sort}`;
        }
        if (filters.description.sort) {
          endpoint += `&sort=description__${filters.description.sort}`;
        }

        const response = await axios.get(endpoint, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setIssues(response.data.results);
        setTotalPages(Math.ceil(response.data.total / size)); // Assuming 'total' is the total number of items
      } catch (err) {
        handleError(err, setError);
      } finally {
        setLoading(false);
      }
    };

    fetchIssues();
  }, [page, size, filters]);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleSizeChange = (event) => {
    setSize(event.target.value);
    setPage(1); // Reset to first page whenever size changes
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const [field, type] = name.split('.');
    setFilterInputs(prevInputs => ({
      ...prevInputs,
      [field]: { ...prevInputs[field], [type]: value }
    }));
  };

  const handleDateChange = (name, date) => {
    setFilterInputs(prevInputs => ({
      ...prevInputs,
      issue_date: {
        ...prevInputs.issue_date,
        value: {
          ...prevInputs.issue_date.value,
          [name]: date
        }
      }
    }));
  };

  const handleFilterApply = () => {
    setFilters(filterInputs);
    setPage(1); // Reset to first page whenever filters are applied
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">Error: {error}</Typography>;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" className={`app-bar ${themeMode}`}>
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          {canIssueStocks && (
            <Button color="inherit" component={Link} to="/issue/create">
              Create Issue
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

            {/* Issue Date Filter */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Issue Date Range</strong>
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    selected={filterInputs.issue_date.value.start}
                    onChange={(date) => handleDateChange('start', date)}
                    selectsStart
                    startDate={filterInputs.issue_date.value.start}
                    endDate={filterInputs.issue_date.value.end}
                    placeholderText="Start Date"
                    fullWidth
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    selected={filterInputs.issue_date.value.end}
                    onChange={(date) => handleDateChange('end', date)}
                    selectsEnd
                    startDate={filterInputs.issue_date.value.start}
                    endDate={filterInputs.issue_date.value.end}
                    placeholderText="End Date"
                    fullWidth
                  />
                </Grid>
              </Grid>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Sort Order</InputLabel>
                    <Select
                      name="issue_date.sort"
                      value={filterInputs.issue_date.sort}
                      onChange={handleFilterChange}
                      fullWidth
                    >
                      {sortOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>

            {/* Description Filter */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Description</strong>
              </Typography>
              <TextField
                label="Description"
                name="description.value"
                value={filterInputs.description.value}
                onChange={handleFilterChange}
                fullWidth
              />
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Operator</InputLabel>
                    <Select
                      name="description.operator"
                      value={filterInputs.description.operator}
                      onChange={handleFilterChange}
                      fullWidth
                    >
                      <MenuItem value="eq">Equals</MenuItem>
                      <MenuItem value="ne">Not Equals</MenuItem>
                      <MenuItem value="lt">Less than</MenuItem>
                      <MenuItem value="le">Less or equal than</MenuItem>
                      <MenuItem value="gt">Greater than</MenuItem>
                      <MenuItem value="ge">Greater or equal than</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Sort Order</InputLabel>
                    <Select
                      name="description.sort"
                      value={filterInputs.description.sort}
                      onChange={handleFilterChange}
                      fullWidth
                    >
                      {sortOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>

            <Button variant="contained" color="primary" onClick={handleFilterApply}>
              Apply Filters
            </Button>
          </Box>
        </Grid>

        {/* Issues List Section */}
        <Grid item xs={12} md={8}>
          <Container>
            <Typography variant="h4" gutterBottom>
              List of Issues
            </Typography>
            <List>
            {issues.map((issue) => (
                <ListItem
                key={issue.id}
                button
                component={Link}
                to={`/issue/${issue.id}`} // Navigates to the IssueDetail page
                >
                <ListItemText
                    primary={`Issue Date: ${issue.issue_date}`}
                    secondary={issue.description}
                />
                </ListItem>
            ))}
            </List>

            {/* Pagination */}
            <Box display="flex" justifyContent="center" mt={2}>
              <FormControl sx={{ mr: 2 }}>
                <InputLabel>Page Size</InputLabel>
                <Select value={size} onChange={handleSizeChange}>
                  {pageSizeOptions.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="outlined"
                onClick={(event) => handlePageChange(event, page - 1)}
                disabled={page === 1}
              >
                Previous
              </Button>
              <Button
                variant="outlined"
                onClick={(event) => handlePageChange(event, page + 1)}
                disabled={page === totalPages}
              >
                Next
              </Button>
            </Box>
          </Container>
        </Grid>
      </Grid>
    </Box>
  );
};

export default IssuesList;
