import { api } from './api';
import { ShoppingListItem, ShoppingListCreate, ShoppingListUpdate } from '../types';

export { ShoppingListItem };

export const shoppingService = {
    getAll: async (token?: string): Promise<ShoppingListItem[]> => {
        const data = await api.get('/shopping-list/', token);
        return data.items ?? data;
    },

    add: async (item: ShoppingListCreate) => {
        return api.post('/shopping-list/', item);
    },

    update: async (id: number, item: ShoppingListUpdate) => {
        return api.put(`/shopping-list/${id}`, item);
    },

    delete: async (id: number) => {
        return api.delete(`/shopping-list/${id}`);
    },

    bulkMoveToInventory: async () => {
        return api.post('/shopping-list/bulk-move', {});
    }
};
