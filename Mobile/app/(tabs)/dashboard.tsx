import { View, Text, FlatList, ActivityIndicator, RefreshControl } from 'react-native';
import { useState, useCallback } from 'react';
import { useFocusEffect, router } from 'expo-router';
import { recipeService, Recipe } from '../../services/recipes';
import RecipeCard from '../../components/RecipeCard';
import { RecipeSuggestion } from '../../services/ai';

export default function Dashboard() {
    const [suggestions, setSuggestions] = useState<RecipeSuggestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchSuggestions = async () => {
        try {
            const data = await recipeService.getSuggestions();
            setSuggestions(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            fetchSuggestions();
        }, [])
    );

    const onRefresh = () => {
        setRefreshing(true);
        fetchSuggestions();
    };

    if (loading) {
        return (
            <View className="flex-1 justify-center items-center bg-white">
                <ActivityIndicator size="large" color="#f97316" />
            </View>
        );
    }

    return (
        <View className="flex-1 bg-white px-4 pt-12">
            <View className="mb-6">
                <Text className="text-3xl font-bold text-gray-900">Bugün Ne Pişirsem?</Text>
                <Text className="text-gray-500 mt-1">Kilerindeki malzemelere göre öneriler</Text>
            </View>

            <FlatList
                data={suggestions}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                    <RecipeCard
                        item={item}
                        onPressDetail={() => router.push(`/recipes/${item.id}`)}
                    />
                )}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#f97316']} />
                }
                ListEmptyComponent={
                    <View className="items-center justify-center py-10">
                        <Text className="text-gray-400 text-lg text-center">
                            Henüz bir öneri yok.{'\n'}Kilerine malzeme ekle veya yeni tarifler oluştur!
                        </Text>
                    </View>
                }
                contentContainerStyle={{ paddingBottom: 20 }}
                showsVerticalScrollIndicator={false}
            />
        </View>
    );
}
