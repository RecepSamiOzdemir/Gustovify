import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert, Image } from 'react-native';
import { useEffect, useState } from 'react';
import { router } from 'expo-router';
import { api } from '../../../services/api';
import EmptyState from '../../../components/EmptyState';
import { Colors } from '../../../constants/Colors';

interface Suggestion {
    id: number;
    title: string;
    instructions: string[];
    servings: number;
    missing_count: number;
    ingredients: any[];
}

export default function SuggestRecipes() {
    const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchSuggestions = async () => {
        try {
            setLoading(true);
            const data = await api.get('/recipes/suggest');
            setSuggestions(data);
        } catch (error: any) {
            Alert.alert('Hata', 'Öneriler alınamadı: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSuggestions();
    }, []);

    const renderItem = ({ item }: { item: Suggestion }) => (
        <TouchableOpacity
            onPress={() => router.push(`/(tabs)/recipes/${item.id}`)}
            className="bg-white rounded-2xl p-4 mb-4 shadow-sm border border-gray-100"
        >
            <View className="flex-row justify-between items-start">
                <View className="flex-1">
                    <Text className="text-lg font-bold text-gray-800 mb-1">{item.title}</Text>
                    <Text className="text-gray-500 text-sm mb-2">{item.servings} Kişilik</Text>

                    <View className={`self-start px-2 py-1 rounded-lg ${item.missing_count === 0 ? 'bg-green-100' : 'bg-orange-100'}`}>
                        <Text className={`text-xs font-bold ${item.missing_count === 0 ? 'text-green-700' : 'text-orange-700'}`}>
                            {item.missing_count === 0 ? 'Pro' : `${item.missing_count} Eksik Malzeme`}
                        </Text>
                    </View>
                </View>
                <Text className="text-2xl">🍽️</Text>
            </View>
        </TouchableOpacity>
    );

    return (
        <View className="flex-1 bg-gray-50 p-4 pt-12">
            <View className="flex-row items-center mb-6">
                <TouchableOpacity onPress={() => router.back()} className="mr-4 bg-gray-200 p-2 rounded-full">
                    <Text>←</Text>
                </TouchableOpacity>
                <Text className="text-2xl font-bold text-gray-900">Ne Pişirsem?</Text>
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={Colors.primary.DEFAULT} />
            ) : (
                <FlatList
                    data={suggestions}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderItem}
                    ListEmptyComponent={
                        <EmptyState
                            title="Öneri Bulunamadı"
                            message="Kilerinizdeki malzemelerle eşleşen tarif bulunamadı. Daha fazla malzeme eklemeyi deneyin."
                            actionLabel="Malzeme Ekle"
                            onAction={() => router.push('/(tabs)/inventory/add')}
                            icon="🍳"
                        />
                    }
                />
            )}
        </View>
    );
}
