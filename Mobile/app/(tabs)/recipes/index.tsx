import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Modal, Platform, Alert, TextInput } from 'react-native';
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { recipeService, Recipe } from '../../../services/recipes';
import { aiService, RecipeSuggestion } from '../../../services/ai';
import RecipeCard from '../../../components/RecipeCard';
import EmptyState from '../../../components/EmptyState';
import { Colors } from '../../../constants/Colors';

export default function Recipes() {
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [loading, setLoading] = useState(true);
    const [suggestions, setSuggestions] = useState<RecipeSuggestion[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    const filteredRecipes = recipes.filter(recipe =>
        recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        recipe.ingredients.some(ing => (ing.name || ing.master_ingredient?.name || '').toLowerCase().includes(searchQuery.toLowerCase()))
    );

    const fetchRecipes = async () => {
        try {
            setLoading(true);
            const data = await recipeService.getAll();
            setRecipes(data);
        } catch (error: any) {
            Alert.alert('Hata', 'Tarifler yüklenemedi: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const handeAiSuggest = async () => {
        try {
            setAiLoading(true);
            const data = await aiService.getSuggestions();
            setSuggestions(data);
            setShowSuggestions(true);
        } catch (error: any) {
            Alert.alert('Hata', 'Öneri alınamadı: ' + error.message);
        } finally {
            setAiLoading(false);
        }
    };

    useEffect(() => {
        fetchRecipes();
    }, []);

    const confirmDelete = (id: number) => {
        if (Platform.OS === 'web') {
            if (window.confirm('Bu tarifi silmek istediğinize emin misiniz?')) {
                handleDelete(id);
            }
        } else {
            Alert.alert('Tarifi Sil', 'Bu tarifi silmek istediğinize emin misiniz?', [
                { text: 'Vazgeç', style: 'cancel' },
                {
                    text: 'Sil',
                    style: 'destructive',
                    onPress: () => handleDelete(id)
                }
            ]);
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await recipeService.delete(id);
            setRecipes(recipes.filter(r => r.id !== id));
        } catch (error: any) {
            Alert.alert('Hata', 'Silinemedi: ' + error.message);
        }
    };

    const renderItem = ({ item }: { item: Recipe | RecipeSuggestion }) => (
        <RecipeCard
            item={item}
            onPressDetail={() => router.push({ pathname: '/(tabs)/recipes/[id]', params: { id: item.id } })}
            onPressDelete={!('missing_count' in item) ? () => confirmDelete(item.id) : undefined}
        />
    );

    return (
        <View className="flex-1 bg-gray-50 p-4 pt-12">
            <View className="flex-row justify-between items-center mb-4">
                <Text className="text-3xl font-bold text-gray-900">Tarifler</Text>
                <View className="flex-row gap-2">
                    <TouchableOpacity onPress={() => router.push({ pathname: '/(tabs)/recipes/add', params: { showImport: 'true' } })} className="bg-blue-100 p-2 rounded-full border border-blue-200">
                        <Text>🌐</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={handeAiSuggest} className="bg-purple-100 p-2 rounded-full border border-purple-200">
                        <Text>✨ AI</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={fetchRecipes} className="bg-gray-200 p-2 rounded-full">
                        <Text>🔄</Text>
                    </TouchableOpacity>
                </View>
            </View>

            {/* Search Bar */}
            <View className="bg-white p-3 rounded-xl border border-gray-200 flex-row items-center shadow-sm mb-4">
                <Text className="mr-2 text-gray-400">🔍</Text>
                <TextInput
                    placeholder="Tarif veya malzeme ara..."
                    className="flex-1 text-lg"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                />
                {searchQuery.length > 0 && (
                    <TouchableOpacity onPress={() => setSearchQuery('')}>
                        <Text className="text-gray-400 font-bold">✕</Text>
                    </TouchableOpacity>
                )}
            </View>

            <Modal visible={showSuggestions} animationType="slide" presentationStyle="pageSheet">
                <View className="flex-1 bg-white p-4 pt-6">
                    <View className="flex-row justify-between items-center mb-4">
                        <Text className="text-2xl font-bold text-purple-600">✨ Şefin Önerileri</Text>
                        <TouchableOpacity onPress={() => setShowSuggestions(false)} className="bg-gray-200 p-2 rounded-full">
                            <Text className="font-bold">Kapat</Text>
                        </TouchableOpacity>
                    </View>
                    <Text className="text-gray-500 mb-4">Eldeki malzemelere göre en uygun tarifler:</Text>
                    <FlatList
                        data={suggestions}
                        keyExtractor={(item) => item.id.toString()}
                        renderItem={renderItem}
                        ListEmptyComponent={
                            <EmptyState
                                title="Öneri Bulunamadı"
                                message="Eldeki malzemelerle yapılabilecek bir tarif bulamadık. Kilerinize yeni ürünler eklemeyi deneyin."
                            />
                        }
                    />
                </View>
            </Modal>

            {loading || aiLoading ? (
                <ActivityIndicator size="large" color={Colors.primary.DEFAULT} />
            ) : (
                <FlatList
                    data={filteredRecipes}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderItem}
                    ListEmptyComponent={
                        <EmptyState
                            title="Henüz Tarif Yok"
                            message="Kendi tariflerinizi ekleyerek başlayın veya AI asistanın size önermesini isteyin!"
                            actionLabel="İlk Tarifini Ekle"
                            onAction={() => router.push('/(tabs)/recipes/add')}
                        />
                    }
                    contentContainerStyle={{ paddingBottom: 100 }}
                />
            )}

            <TouchableOpacity
                onPress={() => router.push('/(tabs)/recipes/add')}
                className="bg-orange-500 w-full py-4 rounded-2xl items-center mt-4 shadow-lg shadow-orange-300 absolute bottom-6 self-center">
                <Text className="text-white font-bold text-lg">Yeni Tarif Oluştur (+)</Text>
            </TouchableOpacity>
        </View>
    );
}
