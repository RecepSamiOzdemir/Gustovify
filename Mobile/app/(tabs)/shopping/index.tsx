import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert, TextInput, Platform } from 'react-native';
import { useState, useCallback } from 'react';
import { shoppingService, ShoppingListItem } from '../../../services/shopping';
import { router, useFocusEffect } from 'expo-router';
import { Colors } from '../../../constants/Colors';
import EmptyState from '../../../components/EmptyState';

export default function ShoppingList() {
    const [items, setItems] = useState<ShoppingListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [moving, setMoving] = useState(false);

    const fetchList = async () => {
        try {
            setLoading(true);
            const data = await shoppingService.getAll();
            setItems(data);
        } catch (error: any) {
            if (error.message && (error.message.includes('401') || error.message.includes('auth'))) {
                Alert.alert('Oturum Süresi Doldu', 'Lütfen tekrar giriş yapın', [
                    { text: 'Tamam', onPress: () => router.replace('/(auth)/login') }
                ]);
            } else {
                Alert.alert('Hata', 'Liste yüklenemedi: ' + error.message);
            }
        } finally {
            setLoading(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            fetchList();
        }, [])
    );

    const toggleCheck = async (item: ShoppingListItem) => {
        try {
            // Optimistic rendering
            setItems(items.map(i => i.id === item.id ? { ...i, is_checked: !i.is_checked } : i));
            await shoppingService.update(item.id, { is_checked: !item.is_checked });
        } catch (error: any) {
            // Revert on error
            setItems(items.map(i => i.id === item.id ? { ...i, is_checked: item.is_checked } : i));
            Alert.alert('Hata', 'Durum güncellenemedi: ' + error.message);
        }
    };

    const confirmDelete = (id: number) => {
        if (Platform.OS === 'web') {
            if (window.confirm('Bu ürünü listeden silmek istediğinize emin misiniz?')) {
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
            await shoppingService.delete(id);
            setItems(items.filter(i => i.id !== id));
        } catch (error: any) {
            Alert.alert('Hata', 'Silinemedi: ' + error.message);
        }
    };

    const handleBulkMove = async () => {
        const checkedItems = items.filter(i => i.is_checked);
        if (checkedItems.length === 0) {
            Alert.alert('Uyarı', 'Lütfen kilere taşımak için en az bir ürün seçin (işaretleyin).');
            return;
        }

        try {
            setMoving(true);
            const response = await shoppingService.bulkMoveToInventory();
            Alert.alert('Başarılı', response.message || 'Ürünler kilere taşındı.');
            fetchList();
        } catch (error: any) {
            Alert.alert('Hata', 'Taşıma işlemi başarısız: ' + error.message);
        } finally {
            setMoving(false);
        }
    };

    const renderItem = ({ item }: { item: ShoppingListItem }) => (
        <View className="bg-white p-4 mb-3 rounded-2xl shadow-sm border border-gray-100 flex-row items-center justify-between mx-4">
            <View className="flex-row items-center flex-1">
                <TouchableOpacity
                    onPress={() => toggleCheck(item)}
                    className={`w-6 h-6 rounded border mr-3 items-center justify-center ${item.is_checked ? 'bg-indigo-500 border-indigo-500' : 'border-gray-300'}`}
                >
                    {item.is_checked && <Text className="text-white text-xs font-bold">✓</Text>}
                </TouchableOpacity>

                <View className="flex-1">
                    <Text className={`text-lg font-bold ${item.is_checked ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
                        {item.name || item.master_ingredient?.name}
                    </Text>
                    <Text className="text-gray-500 text-sm">
                        {item.amount} {item.unit}
                    </Text>
                </View>
            </View>

            <TouchableOpacity
                onPress={() => confirmDelete(item.id)}
                className="p-2 bg-red-50 rounded-lg ml-2"
            >
                <Text className="text-red-500 font-bold">🗑️</Text>
            </TouchableOpacity>
        </View>
    );

    return (
        <View className="flex-1 bg-gray-50 pt-12">
            <View className="px-4 mb-4">
                <Text className="text-3xl font-bold text-gray-900 mb-2">Alışveriş Listesi</Text>
                <Text className="text-gray-500 mb-4">Eksik malzemelerinizi ekleyin, aldıklarınızı işaretleyip kilere taşıyın.</Text>
            </View>

            {loading ? (
                <View className="flex-1 justify-center items-center">
                    <ActivityIndicator size="large" color={Colors.primary.DEFAULT} />
                </View>
            ) : (
                <FlatList
                    data={items}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderItem}
                    ListEmptyComponent={
                        <EmptyState
                            title="Listeniz Boş"
                            message="Alınacak hiçbir malzemeniz görünmüyor. Her şey tamam!"
                            icon="🛒"
                        />
                    }
                    contentContainerStyle={{ paddingBottom: 100 }}
                />
            )}

            {/* Bottom Floating CTA Buttons */}
            <View className="absolute bottom-6 w-full self-center px-4 gap-3">
                {items.some(i => i.is_checked) && (
                    <TouchableOpacity
                        className="bg-indigo-600 py-4 rounded-2xl items-center shadow-lg shadow-indigo-300 w-full mb-1"
                        onPress={handleBulkMove}
                        disabled={moving}
                    >
                        {moving ? (
                            <ActivityIndicator color="white" />
                        ) : (
                            <Text className="text-white font-bold text-lg">Seçilileri Kilere Taşı ({items.filter(i => i.is_checked).length})</Text>
                        )}
                    </TouchableOpacity>
                )}

                <TouchableOpacity
                    onPress={() => router.push('/(tabs)/shopping/add')}
                    className="bg-orange-500 w-full py-4 rounded-2xl items-center shadow-lg shadow-orange-300">
                    <Text className="text-white font-bold text-lg">Listeye Yeni Ürün Ekle (+)</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}
