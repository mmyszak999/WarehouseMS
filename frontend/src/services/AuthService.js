import axios from 'axios';
import {jwtDecode} from 'jwt-decode';
import { handleError } from '../components/ErrorHandler';

const API_URL = 'http://localhost:8000/api/users';

class AuthService {
    async login(email, password) {
        try {
            const response = await axios.post(`${API_URL}/login`, { email, password });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('is_staff', response.data.is_staff.toString());
                localStorage.setItem('can_recept_stocks', response.data.can_recept_stocks.toString());
                localStorage.setItem('can_move_stocks', response.data.can_move_stocks.toString());
                localStorage.setItem('can_issue_stocks', response.data.can_issue_stocks.toString());
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
        localStorage.removeItem('can_recept_stocks');
        localStorage.removeItem('can_move_stocks');
        localStorage.removeItem('can_issue_stocks');
    }

    getCurrentUser() {
        const token = localStorage.getItem('token');
        if (token) {
            return jwtDecode(token);
        }
        return null;
    }

    getUserRole() {
        return localStorage.getItem('is_staff') === 'True';
    }

    canReceptStocks() {
        return localStorage.getItem('can_recept_stocks') === 'True';
    }

    canMoveStocks() {
        return localStorage.getItem('can_move_stocks') === 'True';
    }

    canIssueStocks() {
        return localStorage.getItem('can_issue_stocks') === 'True';
    }
}

export default new AuthService();
