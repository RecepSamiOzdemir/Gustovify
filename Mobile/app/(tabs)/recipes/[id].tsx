import { View, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView, Modal } from 'react-native';
import { useState, useEffect } from 'react';
import { router, useLocalSearchParams, useNavigation } from 'expo-router';
import { recipeService, Recipe } from '../../../services/recipes';
import UnitSelector from '../../../components/UnitSelector';
import CookingModeModal from '../../../components/CookingModeModal';
import ConfirmModal, { useConfirm } from '../../../components/ConfirmModal';

// Basit bir benzersiz ID oluşturucu
const generateId = () => Math.random().toString(36).substr(2, 9);

interface IngredientInput {
    id: string;
    name: string;
    amount: string;
    unit: string;
}

export default function RecipeDetail() {
    const { id } = useLocalSearchParams();
    const navigation = useNavigation();

    // Mode State
    const [isEditing, setIsEditing] = useState(false);

    // Form State
    const [title, setTitle] = useState('');
    const [servings, setServings] = useState('');
    const [instructions, setInstructions] = useState('');
    const [ingredients, setIngredients] = useState<IngredientInput[]>([]);

    // Loading State
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Unit Selection Modal State
    const [showUnitModal, setShowUnitModal] = useState(false);
    const [activeIngredientId, setActiveIngredientId] = useState<string | null>(null);

    // Cooking Mode State
    const [showCookingMode, setShowCookingMode] = useState(false);
    const [checkingStock, setCheckingStock] = useState(false);

    // Web-compatible confirm dialog
    const { confirmState, showConfirm, hideConfirm } = useConfirm();

    useEffect(() => {
        fetchRecipeDetails();
    }, [id]);

    useEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <TouchableOpacity onPress={() => setIsEditing(!isEditing)} className="mr-2">
                    <Text className="text-orange-500 font-bold text-lg">
                        {isEditing ? 'İptal' : 'Düzenle'}
                    </Text>
                </TouchableOpacity>
            ),
            title: isEditing ? 'Tarifi Düzenle' : title || 'Tarif Detayı'
        });
    }, [navigation, isEditing, title]);

    const fetchRecipeDetails = async () => {
        try {
            const recipes = await recipeService.getAll();
            const recipe = recipes.find((r: Recipe) => r.id === Number(id));

            if (recipe) {
                setTitle(recipe.title);
                setServings(recipe.servings.toString());
                setInstructions(recipe.instructions.join('\n'));
                setIngredients(recipe.ingredients.map((ing: any) => ({
                    id: generateId(),
                    name: ing.name,
                    amount: ing.amount.toString(),
                    unit: ing.unit
                })));
            } else {
                Alert.alert('Hata', 'Tarif bulunamadı');
                router.back();
            }
        } catch (error: any) {
            Alert.alert('Hata', 'Tarif yüklenemedi: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const addIngredient = () => {
        setIngredients([...ingredients, { id: generateId(), name: '', amount: '', unit: 'adet' }]);
    };

    const removeIngredient = (id: string) => {
        if (ingredients.length > 1) {
            setIngredients(ingredients.filter(i => i.id !== id));
        }
    };

    const updateIngredient = (id: string, field: keyof IngredientInput, value: string) => {
        setIngredients(ingredients.map(i =>
            i.id === id ? { ...i, [field]: value } : i
        ));
    };

    const openUnitSelector = (id: string) => {
        setActiveIngredientId(id);
        setShowUnitModal(true);
    };

    const selectUnit = (unit: string) => {
        if (activeIngredientId) {
            updateIngredient(activeIngredientId, 'unit', unit);
        }
        setShowUnitModal(false);
        setActiveIngredientId(null);
    };

    const handleUpdate = async () => {
        if (!title || !servings || !instructions) {
            Alert.alert('Hata', 'Lütfen başlık, porsiyon ve yapılışı doldurun.');
            return;
        }

        const validIngredients = ingredients.filter(i => i.name && i.amount && i.unit);
        if (validIngredients.length === 0) {
            Alert.alert('Hata', 'En az bir tam malzeme girmelisiniz.');
            return;
        }

        setSaving(true);
        try {
            await recipeService.update(Number(id), {
                title,
                servings: parseInt(servings),
                instructions: [instructions],
                ingredients: validIngredients.map(i => ({
                    name: i.name,
                    amount: parseFloat(i.amount),
                    unit: i.unit,
                    is_special_unit: false
                }))
            });
            Alert.alert('Başarılı', 'Tarif güncellendi!');
            setIsEditing(false);
        } catch (error: any) {
            Alert.alert('Hata', 'Tarif güncellenemedi: ' + error.message);
        } finally {
            setSaving(false);
        }
    };

    const handleFinishCooking = () => {
        setShowCookingMode(false);
        showConfirm(
            'Tebrikler! 🎉',
            'Pişirme işlemini tamamladınız. Kullanılan malzemeler kilerinizden düşülsün mü?',
            [
                { text: 'Hayır', style: 'cancel' },
                {
                    text: 'Evet, Düş',
                    onPress: async () => {
                        try {
                            const res = await recipeService.cookRecipe(Number(id), parseInt(servings));
                            showConfirm('Başarılı', res.message || 'Kileriniz başarıyla güncellendi.', [{ text: 'Tamam' }]);
                        } catch (error: any) {
                            showConfirm('Hata', 'Kiler güncellenirken bir sorun oluştu: ' + error.message, [{ text: 'Tamam' }]);
                        }
                    }
                }
            ]
        );
    };

    const handleStartCooking = async () => {
        setCheckingStock(true);
        try {
            const stockInfo = await recipeService.checkStock(Number(id));
            if (!stockInfo.can_cook) {
                const missingText = stockInfo.missing_items.map((m: any) => `- ${m.missing} ${m.unit} ${m.name}`).join('\n');
                showConfirm(
                    'Eksik Malzemeler!',
                    `Kilerinizde şu malzemeler eksik:\n${missingText}\n\nYine de pişirmeye başlamak istiyor musunuz?`,
                    [
                        { text: 'İptal', style: 'cancel' },
                        {
                            text: 'Başla', onPress: () => {
                                setShowCookingMode(true);
                            }
                        }
                    ]
                );
            } else {
                setShowCookingMode(true);
            }
        } catch (error: any) {
            showConfirm('Hata', 'Kiler kontrolü yapılamadı: ' + error?.message, [{ text: 'Tamam' }]);
            setShowCookingMode(true);
        } finally {
            setCheckingStock(false);
        }
    };

    if (loading) {
        return <View className="flex-1 justify-center items-center"><ActivityIndicator size="large" color="#f97316" /></View>;
    }

    // View Mode Render
    if (!isEditing) {
        return (
            <View className="flex-1 bg-white">
                <ScrollView className="flex-1 px-6 pt-6" showsVerticalScrollIndicator={false}>
                    <View className="mb-6">
                        <Text className="text-3xl font-bold text-gray-900 mb-2">{title}</Text>
                        <View className="bg-orange-100 self-start px-3 py-1 rounded-full">
                            <Text className="text-orange-600 font-bold">{servings} Kişilik</Text>
                        </View>
                    </View>

                    <View className="mb-8">
                        <Text className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-100 pb-2">Malzemeler</Text>
                        {ingredients.map((ing) => (
                            <View key={ing.id} className="flex-row items-center mb-3">
                                <View className="w-2 h-2 rounded-full bg-orange-400 mr-3" />
                                <Text className="text-lg text-gray-700 flex-1">
                                    <Text className="font-bold">{ing.amount} {ing.unit}</Text> {ing.name}
                                </Text>
                            </View>
                        ))}
                    </View>

                    <View className="mb-10">
                        <Text className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-100 pb-2">Hazırlanışı</Text>
                        <Text className="text-lg text-gray-600 leading-8">{instructions}</Text>
                    </View>
                </ScrollView>

                <View className="p-6 border-t border-gray-100">
                    <TouchableOpacity
                        className={`w-full py-4 rounded-2xl items-center shadow-lg shadow-orange-200 flex-row justify-center ${checkingStock ? 'bg-orange-400' : 'bg-orange-500 active:bg-orange-600'}`}
                        onPress={handleStartCooking}
                        disabled={checkingStock}
                    >
                        {checkingStock ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text className="text-white font-bold text-xl">Pişirmeye Başla</Text>
                        )}
                    </TouchableOpacity>
                </View>

                <CookingModeModal
                    visible={showCookingMode}
                    onClose={() => setShowCookingMode(false)}
                    onFinishCooking={handleFinishCooking}
                    recipeTitle={title}
                    instructions={instructions.split('\n').filter(i => i.trim() !== '')}
                    ingredients={ingredients.map(i => ({
                        id: i.id,
                        name: i.name,
                        amount: i.amount,
                        unit: i.unit
                    }))}
                />
                <ConfirmModal {...confirmState} onRequestClose={hideConfirm} />
            </View>
        );
    }

    // Edit Mode Render
    return (
        <View className="flex-1 bg-white p-6 pt-2">
            <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
                <View className="space-y-4 mb-6">
                    <View>
                        <Text className="text-gray-600 mb-2 font-medium">Tarif Başlığı</Text>
                        <TextInput
                            className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                            placeholder="Örn: Menemen"
                            value={title}
                            onChangeText={setTitle}
                        />
                    </View>

                    <View>
                        <Text className="text-gray-600 mb-2 font-medium">Kaç Kişilik?</Text>
                        <TextInput
                            className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                            placeholder="2"
                            keyboardType="numeric"
                            value={servings}
                            onChangeText={setServings}
                        />
                    </View>

                    <View>
                        <Text className="text-gray-600 mb-2 font-medium">Malzemeler</Text>
                        {ingredients.map((ing, index) => (
                            <View key={ing.id} className="flex-row mb-2 items-center">
                                <TextInput
                                    className="flex-2 bg-gray-50 p-3 rounded-l-xl border border-gray-200 mr-1"
                                    placeholder="Malzeme"
                                    value={ing.name}
                                    onChangeText={(t) => updateIngredient(ing.id, 'name', t)}
                                    style={{ flex: 2 }}
                                />
                                <TextInput
                                    className="flex-1 bg-gray-50 p-3 border-y border-gray-200 mr-1"
                                    placeholder="Miktar"
                                    keyboardType="numeric"
                                    value={ing.amount}
                                    onChangeText={(t) => updateIngredient(ing.id, 'amount', t)}
                                    style={{ flex: 1 }}
                                />
                                <TouchableOpacity
                                    onPress={() => openUnitSelector(ing.id)}
                                    className="flex-1 bg-orange-50 p-3 rounded-r-xl border border-orange-200 mr-2 justify-center"
                                    style={{ flex: 1 }}>
                                    <Text className="text-orange-700 font-medium text-center">{ing.unit || 'Seç'}</Text>
                                </TouchableOpacity>

                                {ingredients.length > 1 && (
                                    <TouchableOpacity onPress={() => removeIngredient(ing.id)}>
                                        <Text className="text-red-500 text-xl font-bold">×</Text>
                                    </TouchableOpacity>
                                )}
                            </View>
                        ))}
                        <TouchableOpacity onPress={addIngredient} className="bg-gray-100 p-2 rounded-lg items-center mt-1">
                            <Text className="text-gray-600 font-bold">+ Malzeme Ekle</Text>
                        </TouchableOpacity>
                    </View>

                    <View>
                        <Text className="text-gray-600 mb-2 font-medium">Hazırlanışı</Text>
                        <TextInput
                            className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                            placeholder="Tarifi buraya yazın..."
                            multiline
                            numberOfLines={4}
                            textAlignVertical="top"
                            value={instructions}
                            onChangeText={setInstructions}
                        />
                    </View>
                </View>

                <TouchableOpacity
                    onPress={handleUpdate}
                    disabled={saving}
                    className={`w-full py-4 rounded-2xl items-center mb-10 shadow-lg shadow-orange-200 ${saving ? 'bg-orange-300' : 'bg-orange-500'}`}>
                    {saving ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text className="text-white font-bold text-lg">Değişiklikleri Kaydet</Text>
                    )}
                </TouchableOpacity>
            </ScrollView>

            <Modal visible={showUnitModal} transparent animationType="fade">
                <View className="flex-1 bg-black/50 justify-center items-center p-4">
                    <View className="bg-white p-6 rounded-2xl w-full max-w-sm">
                        <Text className="text-xl font-bold mb-4 text-center">Birim Seçin</Text>
                        <View className="flex-row flex-wrap justify-center gap-2">
                            <UnitSelector selectedUnit="" onSelect={selectUnit} />
                        </View>
                        <TouchableOpacity
                            onPress={() => setShowUnitModal(false)}
                            className="mt-4 bg-gray-200 p-3 rounded-xl items-center">
                            <Text className="font-bold text-gray-700">İptal</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>
        </View>
    );
}
