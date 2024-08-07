// src/components/CategoriesList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { List, ListItem, ListItemText, CircularProgress, Typography, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import AuthService from '../services/AuthService';

const CategoriesList = ({ themeMode }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isStaff = AuthService.getUserRole();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/categories?size=100&page=1', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setCategories(response.data.results);
      } catch (error) {
        setError('Error fetching categories');
        console.error('Error fetching categories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{String(error)}</Typography>;
  }

  return (
    <Box className={`categories-list ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Categories</Typography>
      <List>
        {categories.map((category) => (
          <ListItem key={category.id}>
            {isStaff ? (
              <ListItemText
                primary={<Link to={`/category/${category.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>{category.name}</Link>}
              />
            ) : (
              <ListItemText primary={category.name} />
            )}
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default CategoriesList;
