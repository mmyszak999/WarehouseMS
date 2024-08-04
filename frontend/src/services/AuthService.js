// src/services/AuthService.js
import axios from 'axios';
import * as jwt from 'jwt-decode'; // Import wszystkiego jako jwt

const API_URL = 'http://localhost:8000/api/users';

class AuthService {
    async login(email, password) {
        try {
            const response = await axios.post(`${API_URL}/login`, { email, password });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
            }
            return response.data;
        } catch (error) {
            if (error.response) {
                // Serwer odpowiedział z kodem stanu innym niż 2xx
                throw new Error(error.response.data.detail || 'Login failed');
            } else if (error.request) {
                // Żądanie zostało wysłane, ale nie otrzymano odpowiedzi
                throw new Error('No response from server');
            } else {
                // Coś innego poszło nie tak
                throw new Error('An unexpected error occurred');
            }
        }
    }

    logout() {
        localStorage.removeItem('token');
    }

    getCurrentUser() {
        const token = localStorage.getItem('token');
        if (token) {
            return jwt.jwtDecode(token);
        }
        return null;
    }
}

export default new AuthService();
