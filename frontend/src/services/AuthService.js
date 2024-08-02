// src/services/AuthService.js
import axios from 'axios';
import * as jwt from 'jwt-decode'; // Import wszystkiego jako jwt

const API_URL = 'http://localhost:8000/api/users';

class AuthService {
    async login(email, password) {
        const response = await axios.post(`${API_URL}/login`, { email, password });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
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
