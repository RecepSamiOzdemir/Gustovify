import { Stack } from 'expo-router';

export default function InventoryLayout() {
    return (
        <Stack
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="index" />
            <Stack.Screen
                name="add"
                options={{
                    title: 'Yeni Ürün Ekle',
                    headerShown: true,
                    presentation: 'modal',
                }}
            />
        </Stack>
    );
}
