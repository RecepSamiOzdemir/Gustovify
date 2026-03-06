import { View, Text, TouchableOpacity } from 'react-native';
import { Colors } from '../constants/Colors';
import { Feather } from '@expo/vector-icons';
import { InventoryItem } from '../services/inventory';

interface InventoryItemCardProps {
    item: InventoryItem;
    onPressEdit: () => void;
    onPressDelete: () => void;
}

export default function InventoryItemCard({ item, onPressEdit, onPressDelete }: InventoryItemCardProps) {
    const displayName = item.name || item.master_ingredient?.name || 'Bilinmeyen Ürün';
    const displayCategory = item.category || item.master_ingredient?.category?.name;

    return (
        <View className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-3 flex-row justify-between items-center">

            {/* Icon & Info */}
            <View className="flex-row items-center flex-1">
                <View className="w-10 h-10 bg-orange-50 rounded-full items-center justify-center mr-3">
                    <Text className="text-lg">📦</Text>
                </View>
                <View>
                    <Text className="text-lg font-bold text-gray-800">{displayName}</Text>
                    <Text className="text-gray-500 font-medium">{item.amount} {item.unit}</Text>
                    {displayCategory && <Text className="text-xs text-gray-400 mt-1">{displayCategory}</Text>}
                    {item.expiry_date && <Text className="text-xs text-red-400 mt-0.5">SKT: {item.expiry_date}</Text>}
                </View>
            </View>

            {/* Actions */}
            <View className="flex-row gap-2">
                <TouchableOpacity
                    onPress={onPressEdit}
                    className="p-2 bg-blue-50 rounded-full"
                    activeOpacity={0.7}
                >
                    <Feather name="edit-2" size={18} color="#2563eb" />
                </TouchableOpacity>
                <TouchableOpacity
                    onPress={onPressDelete}
                    className="p-2 bg-red-50 rounded-full"
                    activeOpacity={0.7}
                >
                    <Feather name="trash-2" size={18} color="#dc2626" />
                </TouchableOpacity>
            </View>
        </View>
    );
}
