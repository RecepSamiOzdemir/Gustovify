import { View, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView, Modal, Platform } from 'react-native';
import { useState, useEffect } from 'react';
import { router, useLocalSearchParams } from 'expo-router';
import { recipeService } from '../../../services/recipes';
import UnitSelector from '../../../components/UnitSelector';
import * as Clipboard from 'expo-clipboard';

// Basit bir benzersiz ID oluşturucu
const generateId = () => Math.random().toString(36).substr(2, 9);

interface IngredientInput {
    id: string;
    name: string;
    amount: string;
    unit: string;
}

export default function AddRecipe() {
    const params = useLocalSearchParams();

    // Form State
    const [title, setTitle] = useState('');
    const [servings, setServings] = useState('');
    const [instructions, setInstructions] = useState('');
    const [ingredients, setIngredients] = useState<IngredientInput[]>([
        { id: generateId(), name: '', amount: '', unit: 'adet' }
    ]);

    // Loading State
    const [loading, setLoading] = useState(false);
    const [scraping, setScraping] = useState(false);

    // Unit Selection Modal State
    const [showUnitModal, setShowUnitModal] = useState(false);
    const [activeIngredientId, setActiveIngredientId] = useState<string | null>(null);

    // Import Modal State
    const [showImportModal, setShowImportModal] = useState(false);
    const [importUrl, setImportUrl] = useState('');
    const [hasHandledImport, setHasHandledImport] = useState(false);

    useEffect(() => {
        if (params.showImport === 'true' && !hasHandledImport) {
            setShowImportModal(true);
            setHasHandledImport(true);
            checkClipboard();
            // Parametreyi temizle ki tekrar tetiklenmesin
            router.setParams({ showImport: undefined });
        }
    }, [params, hasHandledImport]);

    const checkClipboard = async () => {
        const content = await Clipboard.getStringAsync();
        if (content && (content.startsWith('http://') || content.startsWith('https://'))) {
            setImportUrl(content);
        }
    };

    const handleImport = async () => {
        if (!importUrl) return;

        setScraping(true);
        try {
            const data = await recipeService.scrape(importUrl);

            setTitle(data.title);
            setServings(data.servings.toString());
            setInstructions(data.instructions.join('\n'));

            if (data.ingredients && data.ingredients.length > 0) {
                setIngredients(data.ingredients.map((ing: any) => ({
                    id: generateId(),
                    name: ing.name,
                    amount: ing.amount.toString(),
                    unit: ing.unit
                })));
            }

            setShowImportModal(false);
            Alert.alert('Başarılı', 'Tarif bilgileri çekildi! Lütfen eksik alanları kontrol edin.');
        } catch (error: any) {
            Alert.alert('Hata', 'Tarif çekilemedi: ' + error.message);
        } finally {
            setScraping(false);
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

    const handleCreate = async () => {
        if (!title || !servings || !instructions) {
            Alert.alert('Hata', 'Lütfen başlık, porsiyon ve yapılışı doldurun.');
            return;
        }

        const validIngredients = ingredients.filter(i => i.name && i.amount && i.unit);
        if (validIngredients.length === 0) {
            Alert.alert('Hata', 'En az bir tam malzeme girmelisiniz.');
            return;
        }

        setLoading(true);
        try {
            await recipeService.create({
                title,
                servings: parseInt(servings),
                instructions: [instructions], // Backend liste bekliyor
                ingredients: validIngredients.map(i => ({
                    name: i.name,
                    amount: parseFloat(i.amount), // Virgül/Nokta kontrolü eklenebilir
                    unit: i.unit,
                    is_special_unit: false
                }))
            });
            Alert.alert('Başarılı', 'Tarif oluşturuldu!', [
                { text: 'Tamam', onPress: () => router.back() }
            ]);
        } catch (error: any) {
            Alert.alert('Hata', 'Tarif oluşturulamadı: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <View className="flex-1 bg-white p-6 pt-12">
            <View className="flex-row items-center mb-6 justify-between">
                <View className="flex-row items-center">
                    <TouchableOpacity onPress={() => router.back()} className="mr-4">
                        <Text className="text-2xl text-orange-500">←</Text>
                    </TouchableOpacity>
                    <Text className="text-3xl font-bold text-gray-900">Yeni Tarif</Text>
                </View>
                <TouchableOpacity onPress={() => setShowImportModal(true)} className="bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100">
                    <Text className="text-blue-600 font-bold text-xs">🌐 Web'den Al</Text>
                </TouchableOpacity>
            </View>

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
                    onPress={handleCreate}
                    disabled={loading}
                    className={`w-full py-4 rounded-2xl items-center mb-10 shadow-lg shadow-orange-200 ${loading ? 'bg-orange-300' : 'bg-orange-500'}`}>
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text className="text-white font-bold text-lg">Tarifi Kaydet</Text>
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

            {/* Import URL Modal */}
            <Modal visible={showImportModal} transparent animationType="slide">
                <View className="flex-1 bg-black/50 justify-end">
                    <View className="bg-white p-6 rounded-t-3xl h-1/2">
                        <View className="flex-row justify-between items-center mb-6">
                            <Text className="text-2xl font-bold text-gray-900">Web'den Ekle</Text>
                            <TouchableOpacity onPress={() => setShowImportModal(false)}>
                                <Text className="text-gray-500 font-bold text-lg">Kapat</Text>
                            </TouchableOpacity>
                        </View>

                        <Text className="text-gray-500 mb-2">Tarif Linki</Text>
                        <TextInput
                            className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg mb-4"
                            placeholder="https://..."
                            value={importUrl}
                            onChangeText={setImportUrl}
                            autoCapitalize="none"
                            autoCorrect={false}
                        />

                        <TouchableOpacity
                            onPress={handleImport}
                            disabled={scraping}
                            className={`w-full py-4 rounded-2xl items-center shadow-lg shadow-blue-200 ${scraping ? 'bg-blue-300' : 'bg-blue-500'}`}>
                            {scraping ? (
                                <ActivityIndicator color="#fff" />
                            ) : (
                                <Text className="text-white font-bold text-lg">Tarifi Getir</Text>
                            )}
                        </TouchableOpacity>

                        <Text className="text-gray-400 text-center mt-4 text-xs">
                            Desteklenen siteler: AllRecipies, Yemek.com, Nefis Yemek Tarifleri ve Schema.org destekli tüm siteler.
                        </Text>
                    </View>
                </View>
            </Modal>
        </View>
    );
}
