import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Modal, SafeAreaView, ScrollView } from 'react-native';
import { useKeepAwake } from 'expo-keep-awake';
import { StatusBar } from 'expo-status-bar';

interface Ingredient {
    id: string;
    name: string;
    amount: string;
    unit: string;
}

interface CookingModeModalProps {
    visible: boolean;
    onClose: () => void;
    onFinishCooking?: () => void;
    recipeTitle: string;
    instructions: string[];
    ingredients: Ingredient[];
}

export default function CookingModeModal({ visible, onClose, onFinishCooking, recipeTitle, instructions, ingredients }: CookingModeModalProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [checkedIngredients, setCheckedIngredients] = useState<string[]>([]);
    const [showIngredients, setShowIngredients] = useState(false);

    // Ekranın açık kalmasını sağlar
    useKeepAwake();

    useEffect(() => {
        if (visible) {
            setCurrentStep(0);
            setCheckedIngredients([]);
            setShowIngredients(false);
        }
    }, [visible]);

    const toggleIngredient = (id: string) => {
        if (checkedIngredients.includes(id)) {
            setCheckedIngredients(checkedIngredients.filter(i => i !== id));
        } else {
            setCheckedIngredients([...checkedIngredients, id]);
        }
    };

    const handleNext = () => {
        if (currentStep < instructions.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    return (
        <Modal visible={visible} animationType="slide" presentationStyle="fullScreen">
            <View className="flex-1 bg-gray-900">
                <StatusBar style="light" hidden />
                <SafeAreaView className="flex-1">
                    {/* Header */}
                    <View className="flex-row justify-between items-center p-6 pb-2">
                        <View className="flex-1 pr-4">
                            <Text className="text-gray-400 text-sm font-medium uppercase tracking-wider">Pişirme Modu</Text>
                            <Text className="text-white text-xl font-bold truncate" numberOfLines={1}>{recipeTitle}</Text>
                        </View>
                        <TouchableOpacity
                            onPress={onClose}
                            className="bg-gray-800 p-3 rounded-full mb-2"
                        >
                            <Text className="text-gray-300 font-bold text-lg">✕</Text>
                        </TouchableOpacity>
                    </View>

                    {/* Progress Bar */}
                    <View className="h-1 bg-gray-800 w-full mb-8">
                        <View
                            className="h-full bg-orange-500"
                            style={{ width: `${((currentStep + 1) / instructions.length) * 100}%` }}
                        />
                    </View>

                    {/* Content Display */}
                    <View className="flex-1 px-6 justify-center">
                        <View className="bg-gray-800/50 p-4 rounded-xl self-start mb-6 border border-gray-700">
                            <Text className="text-orange-400 font-bold text-lg">
                                ADIM {currentStep + 1} / {instructions.length}
                            </Text>
                        </View>

                        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                            <Text className="text-white text-3xl font-medium leading-10 shadow-sm">
                                {instructions[currentStep]}
                            </Text>
                        </ScrollView>

                        {/* Ingredients Toggle Button */}
                        <TouchableOpacity
                            onPress={() => setShowIngredients(true)}
                            className="bg-gray-800 p-4 rounded-xl flex-row items-center justify-center mb-4 border border-gray-700 active:bg-gray-700"
                        >
                            <Text className="text-orange-400 font-bold mr-2">📋 Malzemeleri Gör</Text>
                        </TouchableOpacity>
                    </View>

                    {/* Ingredients Overlay */}
                    <Modal visible={showIngredients} animationType="slide" transparent>
                        <View className="flex-1 bg-black/80 justify-end">
                            <View className="bg-gray-900 h-3/4 rounded-t-3xl border-t border-gray-700 p-6">
                                <View className="flex-row justify-between items-center mb-6">
                                    <Text className="text-white text-2xl font-bold">Malzeme Listesi</Text>
                                    <TouchableOpacity onPress={() => setShowIngredients(false)}>
                                        <Text className="text-gray-400 font-bold text-lg">Kapat</Text>
                                    </TouchableOpacity>
                                </View>

                                <ScrollView showsVerticalScrollIndicator={false}>
                                    {ingredients.map(ing => (
                                        <TouchableOpacity
                                            key={ing.id}
                                            onPress={() => toggleIngredient(ing.id)}
                                            className="flex-row items-center mb-4 bg-gray-800 p-4 rounded-xl active:bg-gray-700 border border-gray-700"
                                        >
                                            <View className={`w-8 h-8 rounded-full border-2 mr-4 items-center justify-center ${checkedIngredients.includes(ing.id)
                                                ? 'bg-green-500 border-green-500'
                                                : 'border-gray-500'
                                                }`}>
                                                {checkedIngredients.includes(ing.id) && (
                                                    <Text className="text-white font-bold">✓</Text>
                                                )}
                                            </View>
                                            <View className="flex-1">
                                                <Text className={`text-xl ${checkedIngredients.includes(ing.id)
                                                    ? 'text-gray-500 line-through'
                                                    : 'text-white'
                                                    }`}>
                                                    {ing.amount} {ing.unit} <Text className="font-bold">{ing.name}</Text>
                                                </Text>
                                            </View>
                                        </TouchableOpacity>
                                    ))}
                                </ScrollView>
                            </View>
                        </View>
                    </Modal>

                    {/* Controls */}
                    <View className="p-8 pb-12 flex-row gap-4">
                        <TouchableOpacity
                            onPress={handlePrev}
                            disabled={currentStep === 0}
                            className={`flex-1 py-6 rounded-2xl items-center border ${currentStep === 0
                                ? 'bg-gray-800 border-gray-800 opacity-50'
                                : 'bg-gray-800 border-gray-600 active:bg-gray-700'
                                }`}
                        >
                            <Text className={`font-bold text-lg ${currentStep === 0 ? 'text-gray-600' : 'text-white'}`}>
                                ← Geri
                            </Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            onPress={currentStep === instructions.length - 1 ? (onFinishCooking || onClose) : handleNext}
                            className={`flex-2 bg-orange-500 py-6 rounded-2xl items-center shadow-lg shadow-orange-900 active:bg-orange-600 flex-grow-[2]`}
                        >
                            <Text className="text-white font-bold text-xl">
                                {currentStep === instructions.length - 1 ? 'Bitir 🎉' : 'İleri →'}
                            </Text>
                        </TouchableOpacity>
                    </View>
                </SafeAreaView>
            </View>
        </Modal>
    );
}
