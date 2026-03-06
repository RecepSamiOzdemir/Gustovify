import { api } from './api';
import { Recipe } from './recipes';

export interface RecipeSuggestion extends Recipe {
    missing_count: number;
}

export const aiService = {
    getSuggestions: async (token?: string) => {
        return api.get('/recipes/suggest', token);
    }
};
