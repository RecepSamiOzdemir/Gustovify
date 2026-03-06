import { View, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useState } from 'react';
import { router } from 'expo-router';
import { shoppingService } from '../../../services/shopping';
import UnitSelector from '../../../components/UnitSelector';
import MasterIngredientSearch from '../../../components/MasterIngredientSearch';

export default function AddShoppingItem() {
    const [name, setName] = useState('');
    const [amount, setAmount] = useState('');
    const [unit, setUnit] = useState('adet');
    const [category, setCategory] = useState('');
    const [loading, setLoading] = useState(false);

    const handleAdd = async () => {
        if (!name || !amount || !unit) {
            Alert.alert('Hata', 'Lütfen İsim, Miktar ve Birim alanlarını doldurun.');
            return;
        }

        setLoading(true);
        try {
            await shoppingService.add({
                name,
                amount: parseFloat(amount),
                unit,
                category
            });
            Alert.alert('Başarılı', 'Ürün listeye eklendi', [
                { text: 'Tamam', onPress: () => router.back() }
            ]);
        } catch (error: any) {
            Alert.alert('Hata', 'Ekleme başarısız: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <View className="flex-1 bg-white p-6 pt-12">
            <View className="flex-row items-center mb-8">
                <TouchableOpacity onPress={() => router.back()} className="mr-4">
                    <Text className="text-2xl text-orange-500">←</Text>
                </TouchableOpacity>
                <Text className="text-3xl font-bold text-gray-900">Listeye Ekle</Text>
            </View>

            <View className="space-y-4">
                <View className="z-50 border-b border-gray-100 pb-2">
                    <MasterIngredientSearch
                        onSelect={(item, isNew) => {
                            setName(item.name);
                            if (!isNew && item.category) {
                                setCategory(item.category.name);
                            }
                        }}
                    />
                </View>

                {/* If user types custom name and clears search, we need a way to let them know. MasterIngredientSearch handles both. */}

                <View className="flex-row items-end justify-between z-10 mt-4">
                    <View className="flex-1 mr-4">
                        <Text className="text-gray-600 mb-2 font-medium">Miktar</Text>
                        <TextInput
                            className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                            placeholder="0"
                            keyboardType="numeric"
                            value={amount}
                            onChangeText={setAmount}
                        />
                    </View>

                    <View className="flex-1">
                        <UnitSelector selectedUnit={unit} onSelect={setUnit} isMarket={true} />
                    </View>
                </View>

                <View className="mt-4">
                    <Text className="text-gray-600 mb-2 font-medium">Kategori</Text>
                    <TextInput
                        className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                        placeholder="Örn: Sebze, Bakliyat..."
                        value={category}
                        onChangeText={setCategory}
                    />
                </View>
            </View>

            <TouchableOpacity
                onPress={handleAdd}
                disabled={loading}
                className={`w-full py-4 rounded-2xl items-center mt-8 shadow-lg shadow-orange-200 ${loading ? 'bg-orange-300' : 'bg-orange-500'}`}>
                {loading ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <Text className="text-white font-bold text-lg">Ekle</Text>
                )}
            </TouchableOpacity>
        </View>
    );
}
