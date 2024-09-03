import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, TextField, Button, Typography, CircularProgress } from '@mui/material';
import AuthService from '../../services/AuthService';
import { handleError } from '../ErrorHandler';

const UpdateWaitingRoom = () => {
    const { waitingRoomId } = useParams();
    const [waitingRoom, setWaitingRoom] = useState({ name: '', max_stocks: 0, max_weight: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const isStaff = AuthService.getUserRole();

    useEffect(() => {
        const fetchWaitingRoom = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setWaitingRoom(response.data);
            } catch (error) {
                handleError(error, setError);
            } finally {
                setLoading(false);
            }
        };

        fetchWaitingRoom();
    }, [waitingRoomId]);

    const handleChange = (e) => {
        setWaitingRoom({
            ...waitingRoom,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.patch(`http://localhost:8000/api/waiting_rooms/${waitingRoomId}/`, waitingRoom, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            navigate(`/waiting_room/${waitingRoomId}`);
        } catch (error) {
            handleError(error, setError);
        }
    };

    if (!isStaff) {
        return <Typography variant="h6" color="error">You are not authorized to update this waiting room.</Typography>;
    }

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Typography variant="h6">Update Waiting Room</Typography>
            <TextField
                label="Name"
                name="name"
                value={waitingRoom.name}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <TextField
                label="Max Stocks"
                name="max_stocks"
                type="number"
                value={waitingRoom.max_stocks}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <TextField
                label="Max Weight"
                name="max_weight"
                type="number"
                value={waitingRoom.max_weight}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            {error && (
                <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                    {error}
                </Typography>
            )}
            <Button variant="contained" color="primary" type="submit" sx={{ mt: 2 }}>
                Update
            </Button>
        </Box>
    );
};

export default UpdateWaitingRoom;
