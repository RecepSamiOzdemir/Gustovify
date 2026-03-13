import { API_URL } from '../constants/Config';
import { Storage } from './storage';

let isRefreshing = false;

export const api = {
    get: async (endpoint: string, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers,
        });
        return handleResponse(response, 'GET', endpoint);
    },

    post: async (endpoint: string, body: any, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse(response, 'POST', endpoint, body);
    },

    put: async (endpoint: string, body: any, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse(response, 'PUT', endpoint, body);
    },

    delete: async (endpoint: string, token?: string) => {
        const headers = await getHeaders(token);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'DELETE',
            headers,
        });
        return handleResponse(response, 'DELETE', endpoint);
    },
};

async function getHeaders(token?: string): Promise<HeadersInit> {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };

    if (!token) {
        try {
            const storedToken = await Storage.getItem('token');
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

async function handleResponse(response: Response, method: string, endpoint: string, body?: any) {
    if (response.status === 401 && !isRefreshing) {
        isRefreshing = true;
        try {
            const { authService } = await import('./auth');
            const newToken = await authService.refreshToken();
            if (newToken) {
                // Retry the original request with the new token
                const retryHeaders = await getHeaders(newToken);
                const retryOptions: RequestInit = {
                    method,
                    headers: retryHeaders,
                };
                if (body && (method === 'POST' || method === 'PUT')) {
                    retryOptions.body = JSON.stringify(body);
                }
                const retryResponse = await fetch(`${API_URL}${endpoint}`, retryOptions);
                if (retryResponse.ok) {
                    return retryResponse.json();
                }
            }
        } finally {
            isRefreshing = false;
        }
        throw new Error('Oturum süresi doldu, lütfen tekrar giriş yapın');
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Bir hata oluştu');
    }
    return response.json();
}
