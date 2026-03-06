import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { Platform, View, Text } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { db } from '../db/client';
import { useMigrations } from 'drizzle-orm/expo-sqlite/migrator';
import migrations from '../drizzle/migrations';
import { useDrizzleStudio } from 'expo-drizzle-studio-plugin';
import * as SQLite from 'expo-sqlite';
import '../global.css';

function DbInitializedLayout() {
    const { success, error } = useMigrations(db, migrations);

    if (Platform.OS !== 'web') {
        useDrizzleStudio(SQLite.openDatabaseSync('gustovify.db'));
    }

    if (error) {
        return (
            <View className="flex-1 items-center justify-center bg-red-50">
                <Text className="text-red-600 font-bold px-4 text-center">Veritabanı Hatası: {error.message}</Text>
            </View>
        );
    }

    if (!success) {
        return (
            <View className="flex-1 items-center justify-center bg-white">
                <Text className="text-orange-500 font-bold">Veritabanı Hazırlanıyor...</Text>
            </View>
        );
    }

    return (
        <>
            <StatusBar style="dark" />
            <Stack screenOptions={{ headerShown: false }}>
                <Stack.Screen name="index" />
                <Stack.Screen name="(auth)" />
                <Stack.Screen name="(tabs)" />
            </Stack>
        </>
    );
}

export default function RootLayout() {
    // Web Fallback (No DB)
    if (!db) {
        return (
            <>
                <StatusBar style="dark" />
                <Stack screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="index" />
                    <Stack.Screen name="(auth)" />
                    <Stack.Screen name="(tabs)" />
                </Stack>
            </>
        );
    }

    return <DbInitializedLayout />;
}
