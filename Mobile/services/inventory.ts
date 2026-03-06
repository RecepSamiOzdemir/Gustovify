import { api } from './api';
import { InventoryItem, InventoryCreate, InventoryUpdate } from '../types';

export { InventoryItem }; // Re-export for convenience

export const inventoryService = {
    getAll: async (token?: string): Promise<InventoryItem[]> => {
        return api.get('/inventory/', token);
    },

    add: async (item: InventoryCreate) => {
        return api.post('/inventory/', item);
    },
    update: async (id: number, item: InventoryUpdate) => {
        return api.put(`/inventory/${id}`, item);
    },
    delete: async (id: number) => {
        return api.delete(`/inventory/${id}`);
    },

    searchMaster: async (query: string) => {
        return api.get(`/inventory/search_master?query=${query}`);
    }
};
