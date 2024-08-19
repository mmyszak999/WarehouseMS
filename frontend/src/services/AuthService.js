// src/services/AuthService.js
import axios from 'axios';
import {jwtDecode} from 'jwt-decode'; // Poprawiony import

const API_URL = 'http://localhost:8000/api/users';

class AuthService {
    async login(email, password) {
        try {
            const response = await axios.post(`${API_URL}/login`, { email, password });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('is_staff', response.data.is_staff); // Ensure it's a string
            }
            return response.data;
        } catch (error) {
            console.error('Login error details:', error);
            if (error.response) {
                throw new Error(error.response.data.detail || 'Login failed');
            } else if (error.request) {
                throw new Error('No response from server');
            } else {
                throw new Error('An unexpected error occurred');
            }
        }
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('is_staff');
    }

    getCurrentUser() {
        const token = localStorage.getItem('token');
        if (token) {
            return jwtDecode(token);
        }
        return null;
    }

    getUserRole() {
        return localStorage.getItem('is_staff') === 'True'; // Ensure it's a string comparison
    }
}

export default new AuthService();
