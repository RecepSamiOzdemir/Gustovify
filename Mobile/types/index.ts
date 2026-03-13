export interface Category {
    id: number;
    name: string;
    icon?: string;
}

export interface Allergen {
    id: number;
    name: string;
}

export interface DietaryPreference {
    id: number;
    name: string;
}

export interface MasterIngredient {
    id: number;
    name: string;
    category_id?: number;
    category?: Category;
    is_verified?: boolean;
}

export interface User {
    id: number;
    email: string;
    is_active: boolean;
    full_name?: string;
    city?: string;
    age?: number;
    gender?: string;
    dietary_preferences?: string; // Legacy string (JSON)
    allergies?: string; // Legacy string (CSV)
    avatar_url?: string;
    cooking_level?: string;

    // New Relations
    related_allergens?: Allergen[];
    related_preferences?: DietaryPreference[];
    allergen_ids?: number[]; // For update payload
    preference_ids?: number[]; // For update payload
}

export interface UserUpdate {
    password?: string;
    full_name?: string;
    city?: string;
    age?: number;
    gender?: string;
    cooking_level?: string;
    avatar_url?: string;

    // New Update Fields
    allergen_ids?: number[];
    preference_ids?: number[];
}

export interface InventoryItem {
    id: number;
    amount: number;
    unit: string;
    expiry_date?: string;
    user_id: number;
    ingredient_id: number;

    // Computed/Relations
    name?: string; // From MasterIngredient
    category?: string; // From MasterIngredient
    master_ingredient?: MasterIngredient;
}

export interface InventoryCreate {
    name: string;
    amount: number;
    unit: string;
    category?: string; // For auto-creation/update of master
    expiry_date?: string;
}

export interface InventoryUpdate {
    amount?: number;
    unit?: string;
    category?: string;
    expiry_date?: string;
}

export interface RecipeIngredient {
    id: number;
    amount: number;
    unit: string;
    is_special_unit?: boolean;
    name?: string; // Computed
    ingredient_id: number;
    master_ingredient?: MasterIngredient;
}

export interface Recipe {
    id: number;
    title: string;
    instructions: string[];
    servings: number;
    ingredients: RecipeIngredient[];
    user_id?: number;
}

export interface RecipeCreateIngredient {
    name: string;
    amount: number;
    unit: string;
    is_special_unit?: boolean;
}

export interface RecipeCreate {
    title: string;
    instructions: string[];
    servings: number;
    ingredients: RecipeCreateIngredient[];
}

export interface RecipeUpdate {
    title?: string;
    instructions?: string[];
    servings?: number;
    ingredients?: RecipeCreateIngredient[];
}

export interface ShoppingListItem {
    id: number;
    amount: number;
    unit: string;
    is_checked: boolean;
    user_id: number;
    ingredient_id: number;
    name?: string;
    category?: string;
    master_ingredient?: MasterIngredient;
}

export interface ShoppingListCreate {
    name: string;
    amount: number;
    unit: string;
    category?: string;
}

export interface ShoppingListUpdate {
    amount?: number;
    unit?: string;
    is_checked?: boolean;
    category?: string;
}

