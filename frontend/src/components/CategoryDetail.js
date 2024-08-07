// src/components/CategoryDetail.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { CircularProgress, Typography, Box } from '@mui/material';
import AuthService from '../services/AuthService';

const CategoryDetail = ({ themeMode }) => {
  const { categoryId } = useParams();
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isStaff = AuthService.getUserRole() === 'staff';

  useEffect(() => {
    const fetchCategory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/categories/${categoryId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setCategory(response.data);
      } catch (error) {
        setError('Error fetching category details');
        console.error('Error fetching category details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategory();
  }, [categoryId]);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography variant="h6" color="error">{String(error)}</Typography>;
  }

  return (
    <Box className={`category-detail ${themeMode}`}>
      <Typography variant="h4" gutterBottom>Category Detail</Typography>
      <Typography variant="h6">Name: {category.name}</Typography>
      <Typography variant="body1">Created At: {category.created_at}</Typography>
    </Box>
  );
};

export default CategoryDetail;
