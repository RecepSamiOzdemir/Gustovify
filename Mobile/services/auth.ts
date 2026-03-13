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
        await Storage.setItem('refreshToken', data.refresh_token);
        return data;
    },

    register: async (email: string, password: string) => {
        return api.post('/auth/register', { email, password });
    },

    logout: async () => {
        const refreshToken = await Storage.getItem('refreshToken');
        if (refreshToken) {
            try {
                await api.post('/auth/logout', { refresh_token: refreshToken });
            } catch (_) { /* ignore logout errors */ }
        }
        await Storage.deleteItem('token');
        await Storage.deleteItem('refreshToken');
    },

    refreshToken: async (): Promise<string | null> => {
        const refreshToken = await Storage.getItem('refreshToken');
        if (!refreshToken) return null;

        try {
            const response = await fetch(`${API_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (!response.ok) return null;

            const data = await response.json();
            await Storage.setItem('token', data.access_token);
            await Storage.setItem('refreshToken', data.refresh_token);
            return data.access_token;
        } catch {
            return null;
        }
    }
};
