import { View, Text, TouchableOpacity } from 'react-native';
import { Colors } from '../constants/Colors';
import { Recipe } from '../services/recipes';
import { RecipeSuggestion } from '../services/ai';

interface RecipeCardProps {
    item: Recipe | RecipeSuggestion;
    onPressDetail: () => void;
    onPressDelete?: () => void;
}

export default function RecipeCard({ item, onPressDetail, onPressDelete }: RecipeCardProps) {
    const isSuggestion = 'missing_count' in item;
    const missingCount = isSuggestion ? (item as RecipeSuggestion).missing_count : 0;

    return (
        <View className="bg-white p-4 rounded-2xl shadow-sm mb-4 border border-gray-100">
            {/* Header */}
            <View className="flex-row justify-between items-start mb-3">
                <Text className="text-lg font-bold text-gray-800 flex-1 mr-2 leading-6">
                    {item.title}
                </Text>
                <View className="flex-row gap-1 items-center">
                    {isSuggestion && (
                        <View className={`px-2 py-1 rounded-lg ${missingCount === 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                            <Text className={`font-bold text-xs ${missingCount === 0 ? 'text-green-700' : 'text-red-700'}`}>
                                {missingCount === 0 ? 'Tamam!' : `${missingCount} Eksik`}
                            </Text>
                        </View>
                    )}
                    <View className="bg-orange-100 px-2 py-1 rounded-lg">
                        <Text className="text-orange-600 font-bold text-xs">{item.servings} Kişilik</Text>
                    </View>
                </View>
            </View>

            {/* Instructions Preview */}
            <Text className="text-gray-500 mb-4 text-sm leading-5" numberOfLines={2}>
                {item.instructions.join(' ')}
            </Text>

            {/* Footer / Actions */}
            <View className="flex-row items-center justify-between border-t border-gray-50 pt-3">
                <View className="bg-gray-100 px-2 py-1 rounded-md">
                    <Text className="text-xs text-gray-500 font-medium">
                        {item.ingredients.length} Malzeme
                    </Text>
                </View>

                <View className="flex-row gap-3 items-center">
                    {onPressDelete && !isSuggestion && (
                        <TouchableOpacity onPress={onPressDelete} className="p-1">
                            <Text className="text-red-500 font-semibold text-sm">Sil</Text>
                        </TouchableOpacity>
                    )}
                    <TouchableOpacity onPress={onPressDetail} className="bg-orange-50 px-3 py-1.5 rounded-lg border border-orange-100">
                        <Text className="text-orange-600 font-bold text-sm">Tarife Git →</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </View>
    );
}
