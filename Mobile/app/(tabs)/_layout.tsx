import { Tabs } from 'expo-router';
import { View, Text } from 'react-native';

export default function TabsLayout() {
    return (
        <Tabs screenOptions={{ tabBarActiveTintColor: '#f97316' }}>
            <Tabs.Screen name="dashboard" options={{ title: 'Ana Sayfa', headerShown: false }} />
            <Tabs.Screen name="inventory" options={{ title: 'Kiler', headerShown: false }} />
            <Tabs.Screen name="shopping" options={{ title: 'Alışveriş', headerShown: false }} />
            <Tabs.Screen name="recipes" options={{ title: 'Tarifler', headerShown: false }} />
            <Tabs.Screen name="profile" options={{ title: 'Profil', headerShown: false }} />
        </Tabs>
    );
}
