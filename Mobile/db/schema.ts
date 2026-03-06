import { sqliteTable, integer, text, real } from 'drizzle-orm/sqlite-core';

export const recipes = sqliteTable('recipes', {
    id: integer('id').primaryKey({ autoIncrement: true }),
    title: text('title').notNull(),
    instructions: text('instructions').notNull(), // JSON string as array of strings
    servings: integer('servings').notNull().default(1),
    ingredients: text('ingredients').notNull(), // JSON string as array of ingredient objects
});

export const inventory = sqliteTable('inventory', {
    id: integer('id').primaryKey({ autoIncrement: true }),
    name: text('name').notNull(),
    amount: real('amount').notNull(),
    unit: text('unit').notNull(),
});

export type Recipe = typeof recipes.$inferSelect;
export type NewRecipe = typeof recipes.$inferInsert;

export type InventoryItem = typeof inventory.$inferSelect;
export type NewInventoryItem = typeof inventory.$inferInsert;
