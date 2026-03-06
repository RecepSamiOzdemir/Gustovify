import { View, Text, TouchableOpacity } from 'react-native';
import { Colors } from '../constants/Colors';

interface EmptyStateProps {
    title: string;
    message: string;
    actionLabel?: string;
    onAction?: () => void;
    icon?: string; // Emoji
}

export default function EmptyState({ title, message, actionLabel, onAction, icon = '🔍' }: EmptyStateProps) {
    return (
        <View className="flex-1 justify-center items-center p-8 bg-gray-50 min-h-[300px]">
            <Text className="text-6xl mb-4">{icon}</Text>
            <Text className="text-xl font-bold text-gray-800 text-center mb-2">{title}</Text>
            <Text className="text-gray-500 text-center mb-6 leading-5">{message}</Text>

            {actionLabel && onAction && (
                <TouchableOpacity
                    onPress={onAction}
                    className="bg-orange-500 px-6 py-3 rounded-xl shadow-sm shadow-orange-200 active:bg-orange-600"
                >
                    <Text className="text-white font-bold">{actionLabel}</Text>
                </TouchableOpacity>
            )}
        </View>
    );
}
