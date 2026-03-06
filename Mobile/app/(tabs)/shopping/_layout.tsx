import { Stack } from 'expo-router';

export default function ShoppingLayout() {
    return (
        <Stack>
            <Stack.Screen name="index" options={{ headerShown: false }} />
            <Stack.Screen name="add" options={{ headerShown: false, presentation: 'modal' }} />
        </Stack>
    );
}
