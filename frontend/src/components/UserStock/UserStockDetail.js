import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import { Typography, CircularProgress, Box, Link as MuiLink, AppBar, Toolbar, Button } from '@mui/material';
import { handleError } from '../ErrorHandler';

const UserStockDetail = () => {
    const { userStockId } = useParams();
    const [userStock, setUserStock] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUserStockDetails = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/user-stocks/${userStockId}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setUserStock(response.data);
            } catch (error) {
                handleError(error, setError);
            } finally {
                setLoading(false);
            }
        };

        fetchUserStockDetails();
    }, [userStockId]);

    if (loading) return <CircularProgress />;
    if (error) return <Typography variant="h6" color="error">{error}</Typography>;
    if (!userStock) return <Typography variant="h6">User stock not found</Typography>;

    return (
        <Box sx={{ p: 3 }}>
            <AppBar position="static">
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                </Toolbar>
            </AppBar>

            <Typography variant="h4" gutterBottom>Stock History Details</Typography>
            <Typography variant="body1">
                Managed By:
                {userStock.user ? (
                    <MuiLink component={Link} to={`/user/${userStock.user.id}`}>
                        {userStock.user.first_name} {userStock.user.last_name}
                    </MuiLink>
                ) : 'N/A'}
            </Typography>
            <Typography variant="body1">Moved At: {new Date(userStock.moved_at).toLocaleDateString()}</Typography>
            <Typography variant="body1">
                Stock: 
                {userStock.stock ? (
                    <MuiLink component={Link} to={`/stock/all/${userStock.stock.id}`}>
                        Stock
                    </MuiLink>
                ) : 'N/A'}
            </Typography>
            <Typography variant="body1">
                Product: 
                <MuiLink component={Link} to={`/product/${userStock.stock.product.id}`}>
                    {userStock.stock.product.name}
                </MuiLink>
            </Typography>
            {/* Waiting Room Links */}
            <Typography variant="body1">
                <strong>From Waiting Room: </strong>
                {userStock.from_waiting_room ? (
                    <MuiLink component={Link} to={`/waiting_room/${userStock.from_waiting_room.id}`}>
                        {userStock.from_waiting_room.name}
                    </MuiLink>
                ) : 'N/A'}
            </Typography>

            <Typography variant="body1">
                <strong>To Waiting Room: </strong>
                {userStock.to_waiting_room ? (
                    <MuiLink component={Link} to={`/waiting_room/${userStock.to_waiting_room.id}`}>
                        {userStock.to_waiting_room.name}
                    </MuiLink>
                ) : 'N/A'}
            </Typography>

            {/* Rack Level Slot Links */}
            <Typography variant="body1">
                <strong>From Rack Slot: </strong>
                {userStock.from_rack_level_slot ? (
                    <MuiLink component={Link} to={`/rack-level-slot/${userStock.from_rack_level_slot.id}`}>
                        {userStock.from_rack_level_slot.description}
                    </MuiLink>
                ) : 'N/A'}
            </Typography>

            <Typography variant="body1">
                <strong>To Rack Slot: </strong>
                {userStock.to_rack_level_slot ? (
                    <MuiLink component={Link} to={`/rack-level-slot/${userStock.to_rack_level_slot.id}`}>
                        {userStock.to_rack_level_slot.description}
                    </MuiLink>
                ) : 'N/A'}
            </Typography>

            {/* Issue Details */}
            <Typography variant="body1">
                <strong>Issue: </strong>
                {userStock.issue ? (
                    <MuiLink component={Link} to={`/issue/${userStock.issue.id}`}>
                        Issue
                    </MuiLink>
                ) : 'N/A'}
            </Typography>

            {/* Timestamps */}
            <Typography variant="body1">
                <strong>Created At: </strong> {new Date(userStock.stock.created_at).toLocaleDateString()}
            </Typography>

            {/* Additional details if needed */}
            <Typography variant="body1">
                <strong>Reception: </strong>
                {userStock.reception ? (
                    <MuiLink component={Link} to={`/reception/${userStock.reception.id}`}>
                        Reception
                    </MuiLink>
                ) : 'N/A'}
            </Typography>
        </Box>
    );
};

export default UserStockDetail;
