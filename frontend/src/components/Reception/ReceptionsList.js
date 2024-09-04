import React, { useState, useEffect } from 'react';
import { Container, Typography, List, ListItem, ListItemText, CircularProgress } from '@mui/material';
import axios from 'axios';

const ReceptionsList = ({ themeMode }) => {
  const [receptions, setReceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReceptions = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/receptions');
        setReceptions(response.data.results); // Assuming response contains a "results" field
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReceptions();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">Error: {error}</Typography>;

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        List of Receptions
      </Typography>
      <List>
        {receptions.map((reception) => (
          <ListItem key={reception.id}>
            <ListItemText
              primary={`Reception ID: ${reception.id}`}
              secondary={`Date: ${new Date(reception.reception_date).toLocaleDateString()} - Description: ${reception.description || 'N/A'}`}
            />
          </ListItem>
        ))}
      </List>
    </Container>
  );
};

export default ReceptionsList;
