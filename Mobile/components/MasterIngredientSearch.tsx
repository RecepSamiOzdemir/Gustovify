import { View, Text, TextInput, TouchableOpacity, FlatList, ActivityIndicator } from 'react-native';
import { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventory';
import { MasterIngredient } from '../types';

interface MasterIngredientSearchProps {
    onSelect: (ingredient: MasterIngredient, isNew: boolean) => void;
    initialValue?: string;
}

export default function MasterIngredientSearch({ onSelect, initialValue = '' }: MasterIngredientSearchProps) {
    const [query, setQuery] = useState(initialValue);
    const [results, setResults] = useState<MasterIngredient[]>([]);
    const [loading, setLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (query.length >= 2) {
                handleSearch(query);
            } else {
                setResults([]);
            }
        }, 500);

        return () => clearTimeout(timeoutId);
    }, [query]);

    const handleSearch = async (text: string) => {
        try {
            setLoading(true);
            const data = await inventoryService.searchMaster(text);
            setResults(data);
            setShowResults(true);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = (item: MasterIngredient) => {
        setQuery(item.name);
        setShowResults(false);
        onSelect(item, false);
    };

    const handleNew = () => {
        setShowResults(false);
        // Create a temporary master ingredient object for new item
        const newItem: MasterIngredient = { id: 0, name: query };
        onSelect(newItem, true);
    };

    return (
        <View className="relative z-50">
            <Text className="text-gray-600 mb-2 font-medium">Ürün Adı</Text>
            <TextInput
                className="w-full bg-gray-50 p-4 rounded-xl border border-gray-200 text-lg"
                placeholder="Örn: Domates"
                value={query}
                onChangeText={(text) => {
                    setQuery(text);
                    setShowResults(true);
                }}
                onBlur={() => {
                    // Slight delay to allow click on result
                    setTimeout(() => {
                        if (query && results.length === 0) {
                            handleNew();
                        }
                    }, 200);
                }}
            />

            {showResults && (query.length >= 2) && (
                <View className="absolute top-24 left-0 right-0 bg-white rounded-xl shadow-lg border border-gray-100 max-h-48 z-50">
                    {loading ? (
                        <ActivityIndicator className="p-4" color="#F97316" />
                    ) : (
                        <FlatList
                            data={results}
                            keyExtractor={(item) => item.id.toString()}
                            renderItem={({ item }) => (
                                <TouchableOpacity
                                    className="p-3 border-b border-gray-100"
                                    onPress={() => handleSelect(item)}
                                >
                                    <Text className="text-gray-800">{item.name}</Text>
                                    {item.category && <Text className="text-xs text-gray-400">{item.category.name}</Text>}
                                </TouchableOpacity>
                            )}
                            ListEmptyComponent={
                                <TouchableOpacity className="p-3" onPress={handleNew}>
                                    <Text className="text-orange-500 font-medium">"{query}" yeni olarak ekle</Text>
                                </TouchableOpacity>
                            }
                        />
                    )}
                </View>
            )}
        </View>
    );
}
