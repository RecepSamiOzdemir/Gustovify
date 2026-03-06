import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert, Modal, TextInput, Platform } from 'react-native';
import { useEffect, useState } from 'react';
import { inventoryService, InventoryItem } from '../../../services/inventory';
import { router } from 'expo-router';
import UnitSelector from '../../../components/UnitSelector';
import InventoryItemCard from '../../../components/InventoryItemCard';
import EmptyState from '../../../components/EmptyState';
import { Colors } from '../../../constants/Colors';

export default function Inventory() {
    const [items, setItems] = useState<InventoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchInventory = async () => {
        try {
            setLoading(true);
            const data = await inventoryService.getAll();
            setItems(data);
        } catch (error: any) {
            if (error.message && (error.message.includes('401') || error.message.includes('auth'))) {
                Alert.alert('Oturum Süresi Doldu', 'Lütfen tekrar giriş yapın', [
                    { text: 'Tamam', onPress: () => router.replace('/(auth)/login') }
                ]);
            } else {
                Alert.alert('Hata', 'Envanter yüklenemedi: ' + error.message);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInventory();
    }, []);

    // Edit State
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
    const [editAmount, setEditAmount] = useState('');
    const [editUnit, setEditUnit] = useState('');

    const openEditModal = (item: InventoryItem) => {
        setEditingItem(item);
        setEditAmount(item.amount.toString());
        setEditUnit(item.unit);
        setEditModalVisible(true);
    };

    const handleUpdate = async () => {
        if (!editingItem || !editAmount) return;

        try {
            const updatedItem = await inventoryService.update(editingItem.id, {
                amount: parseFloat(editAmount),
                unit: editUnit
            });

            setItems(items.map(i => i.id === editingItem.id ? updatedItem : i));
            setEditModalVisible(false);
            setEditingItem(null);
        } catch (error: any) {
            Alert.alert('Hata', 'Güncellenemedi: ' + error.message);
        }
    };

    const confirmDelete = (id: number) => {
        if (Platform.OS === 'web') {
            if (window.confirm('Bu ürünü silmek istediğinize emin misiniz?')) {
                handleDelete(id);
            }
        } else {
            Alert.alert('Sil', 'Bu ürünü silmek istediğinize emin misiniz?', [
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
            await inventoryService.delete(id);
            setItems(items.filter(i => i.id !== id));
        } catch (error: any) {
            Alert.alert('Hata', 'Silinemedi: ' + error.message);
        }
    };

    // Search State
    const [searchQuery, setSearchQuery] = useState('');

    const filteredItems = items.filter(item => {
        const name = item.name || item.master_ingredient?.name || '';
        const category = item.category || item.master_ingredient?.category?.name || '';
        return name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            category.toLowerCase().includes(searchQuery.toLowerCase());
    });

    const renderItem = ({ item }: { item: InventoryItem }) => (
        <InventoryItemCard
            item={item}
            onPressEdit={() => openEditModal(item)}
            onPressDelete={() => confirmDelete(item.id)}
        />
    );

    return (
        <View className="flex-1 bg-gray-50 p-4 pt-12">
            <View className="px-4 mb-4">
                <Text className="text-3xl font-bold text-gray-900 mb-4">Kilerim</Text>

                {/* Search Bar */}
                <View className="bg-white p-3 rounded-xl border border-gray-200 flex-row items-center shadow-sm">
                    <Text className="mr-2 text-gray-400">🔍</Text>
                    <TextInput
                        placeholder="Ürün veya kategori ara..."
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
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={Colors.primary.DEFAULT} />
            ) : (
                <FlatList
                    data={filteredItems}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderItem}
                    ListEmptyComponent={
                        <EmptyState
                            title="Kileriniz Boş"
                            message="Henüz hiç ürün eklemediniz. Malzemelerinizi ekleyerek tarif önerileri almaya başlayın."
                            actionLabel="İlk Ürünü Ekle"
                            onAction={() => router.push('/(tabs)/inventory/add')}
                            icon="📦"
                        />
                    }
                    contentContainerStyle={{ paddingBottom: 150 }}
                />
            )}

            <View className="absolute bottom-6 w-full self-center px-4 gap-3">
                <TouchableOpacity
                    onPress={() => router.push('/(tabs)/recipes/suggest')}
                    className="bg-indigo-600 w-full py-4 rounded-2xl items-center shadow-lg shadow-indigo-300">
                    <Text className="text-white font-bold text-lg">Ne Pişirsem? 🍳</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    onPress={() => router.push('/(tabs)/inventory/add')}
                    className="bg-orange-500 w-full py-4 rounded-2xl items-center shadow-lg shadow-orange-300">
                    <Text className="text-white font-bold text-lg">Yeni Ürün Ekle (+)</Text>
                </TouchableOpacity>
            </View>

            <Modal visible={editModalVisible} transparent animationType="slide">
                <View className="flex-1 bg-black/50 justify-center items-center p-4">
                    <View className="bg-white p-6 rounded-2xl w-full max-w-sm">
                        <Text className="text-xl font-bold mb-4 text-center">{editingItem?.name || editingItem?.master_ingredient?.name} Düzenle</Text>

                        <View className="mb-4">
                            <Text className="text-gray-600 mb-2">Miktar</Text>
                            <TextInput
                                value={editAmount}
                                onChangeText={setEditAmount}
                                keyboardType="numeric"
                                className="bg-gray-50 p-3 rounded-xl border border-gray-200"
                            />
                        </View>

                        <View className="mb-6 h-20">
                            <UnitSelector selectedUnit={editUnit} onSelect={setEditUnit} />
                        </View>

                        <View className="flex-row gap-2">
                            <TouchableOpacity
                                onPress={() => setEditModalVisible(false)}
                                className="flex-1 bg-gray-200 p-3 rounded-xl items-center">
                                <Text className="font-bold text-gray-700">İptal</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                onPress={handleUpdate}
                                className="flex-1 bg-indigo-500 p-3 rounded-xl items-center">
                                <Text className="font-bold text-white">Kaydet</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </Modal>
        </View>
    );
}
