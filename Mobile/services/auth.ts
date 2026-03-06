import { api } from './api';
import { API_URL } from '../constants/Config';
import { Storage } from './storage';

export const authService = {
    login: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
        });

        if (!response.ok) {
            throw new Error('Giriş başarısız');
        }

        const data = await response.json();
        await Storage.setItem('token', data.access_token);
        return data;
    },

    register: async (email: string, password: string) => {
        return api.post('/auth/register', { email, password });
    },

    logout: async () => {
        await Storage.deleteItem('token');
    }
};
