import axios from 'axios';
import {jwtDecode} from 'jwt-decode'; // Ensure correct import
import { handleError } from '../components/ErrorHandler';

const API_URL = 'http://localhost:8000/api/users';

class AuthService {
    async login(email, password) {
        try {
            const response = await axios.post(`${API_URL}/login`, { email, password });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('is_staff', response.data.is_staff.toString()); // Store as string
            }
            return response.data;
        } catch (error) {
            handleError(error);
            throw error;
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
        return localStorage.getItem('is_staff') === 'True'; // Ensure proper string comparison
    }
}

export default new AuthService();
