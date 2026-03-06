import { Stack } from 'expo-router';

export default function RecipesLayout() {
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
                    title: 'Yeni Tarif Ekle',
                    headerShown: true,
                    presentation: 'modal',
                }}
            />
            <Stack.Screen
                name="[id]"
                options={{
                    title: 'Tarif Detayı',
                    headerShown: true,
                }}
            />
        </Stack>
    );
}
