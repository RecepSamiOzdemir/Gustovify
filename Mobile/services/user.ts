import { api } from './api';
import { User, UserUpdate, Allergen, DietaryPreference } from '../types';

export { User, UserUpdate };

export const userService = {
    getProfile: async (): Promise<User> => {
        return api.get('/users/me');
    },

    updateProfile: async (data: UserUpdate): Promise<User> => {
        return api.put('/users/me', data);
    },

    getAllergens: async (): Promise<Allergen[]> => {
        return api.get('/utils/allergens');
    },

    getPreferences: async (): Promise<DietaryPreference[]> => {
        return api.get('/utils/preferences');
    }
};
