import { drizzle } from 'drizzle-orm/expo-sqlite';
import { openDatabaseSync } from 'expo-sqlite';
import * as schema from './schema';

let dbInstance: any;

try {
    const expoDb = openDatabaseSync('gustovify.db');
    dbInstance = drizzle(expoDb, { schema });
} catch (error) {
    console.warn("Database initialization failed (Web Fallback Active):", error);
    dbInstance = null;
}

export const db = dbInstance;
