import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { UNITS, MARKET_UNITS } from '../constants/Units';

interface UnitSelectorProps {
    selectedUnit: string;
    onSelect: (unit: string) => void;
    isMarket?: boolean;
}

export default function UnitSelector({ selectedUnit, onSelect, isMarket = false }: UnitSelectorProps) {
    const unitsToShow = isMarket ? MARKET_UNITS : UNITS;

    return (
        <View>
            <Text className="text-gray-600 mb-2 font-medium">Birim</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-row">
                {unitsToShow.map((unit) => (
                    <TouchableOpacity
                        key={unit}
                        onPress={() => onSelect(unit)}
                        className={`mr-2 px-4 py-3 rounded-xl border ${selectedUnit === unit
                            ? 'bg-orange-500 border-orange-500'
                            : 'bg-gray-50 border-gray-200'
                            }`}
                    >
                        <Text className={`font-medium ${selectedUnit === unit ? 'text-white' : 'text-gray-600'
                            }`}>
                            {unit}
                        </Text>
                    </TouchableOpacity>
                ))}
            </ScrollView>
        </View>
    );
}
