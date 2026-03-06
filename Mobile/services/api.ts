import { API_URL } from '../constants/Config';

export const api = {
    get: async (endpoint: string, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers,
        });
        return handleResponse(response);
    },

    post: async (endpoint: string, body: any, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse(response);
    },

    put: async (endpoint: string, body: any, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse(response);
    },

    delete: async (endpoint: string, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'DELETE',
            headers,
        });
        return handleResponse(response);
    },
};

import { Storage } from './storage';

async function getHeaders(token?: string): Promise<HeadersInit> {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };

    if (!token) {
        try {
            const storedToken = await Storage.getItem('token');
            console.log('Stored Token:', storedToken ? 'Found' : 'Not Found');
            if (storedToken) {
                token = storedToken;
            }
        } catch (error) {
            console.log('Token okuma hatası:', error);
        }
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function handleResponse(response: Response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Bir hata oluştu');
    }
    return response.json();
}
