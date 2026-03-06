import { api } from './api';
import { Recipe, RecipeCreate, RecipeUpdate } from '../types';

export { Recipe, RecipeCreate, RecipeUpdate };

export const recipeService = {
    getAll: async (token?: string): Promise<Recipe[]> => {
        return api.get('/recipes/', token);
    },

    create: async (recipe: RecipeCreate) => {
        return api.post('/recipes/', recipe);
    },
    update: async (id: number, recipe: RecipeUpdate) => {
        return api.put(`/recipes/${id}`, recipe);
    },
    delete: async (id: number) => {
        return api.delete(`/recipes/${id}`);
    },
    getSuggestions: async () => {
        return api.get('/recipes/suggest');
    },
    scrape: async (url: string) => {
        return api.post('/recipes/scrape', { url });
    },
    checkStock: async (id: number) => {
        return api.get(`/recipes/${id}/check-stock`);
    },
    cookRecipe: async (id: number, targetServings?: number) => {
        const url = targetServings ? `/recipes/${id}/cook?target_servings=${targetServings}` : `/recipes/${id}/cook`;
        return api.post(url, {});
    }
};
