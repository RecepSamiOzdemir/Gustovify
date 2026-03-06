import React from 'react';
import { View, Text, TouchableOpacity, Modal, Platform, Alert } from 'react-native';

interface ConfirmButton {
    text: string;
    style?: 'default' | 'cancel' | 'destructive';
    onPress?: () => void;
}

interface ConfirmModalProps {
    visible: boolean;
    title: string;
    message: string;
    buttons: ConfirmButton[];
    onRequestClose?: () => void;
}

/**
 * Web-compatible alert/confirm bileşeni.
 * Native'de React Native Alert.alert kullanılır,
 * Web'de ise bu Modal bileşeni gösterilir.
 */
export default function ConfirmModal({ visible, title, message, buttons, onRequestClose }: ConfirmModalProps) {
    // Native platformlarda bu bileşen render edilmez (Alert.alert kullanılır)
    if (Platform.OS !== 'web') return null;

    return (
        <Modal
            visible={visible}
            transparent
            animationType="fade"
            onRequestClose={onRequestClose}
        >
            <View className="flex-1 bg-black/60 justify-center items-center px-6">
                <View className="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
                    {/* Başlık */}
                    <View className="px-6 pt-6 pb-2">
                        <Text className="text-xl font-bold text-gray-900 text-center">{title}</Text>
                    </View>

                    {/* Mesaj */}
                    <View className="px-6 pb-6">
                        <Text className="text-gray-600 text-base text-center leading-6 mt-2">{message}</Text>
                    </View>

                    {/* Butonlar */}
                    <View className="border-t border-gray-100">
                        {buttons.map((btn, index) => (
                            <TouchableOpacity
                                key={index}
                                onPress={btn.onPress}
                                className={`py-4 items-center ${index < buttons.length - 1 ? 'border-b border-gray-100' : ''}`}
                                style={{
                                    backgroundColor:
                                        btn.style === 'cancel' ? '#f9fafb' : btn.style === 'destructive' ? '#fff1f2' : '#fff',
                                }}
                            >
                                <Text
                                    className={`text-base font-semibold ${btn.style === 'cancel'
                                            ? 'text-gray-500'
                                            : btn.style === 'destructive'
                                                ? 'text-red-500'
                                                : 'text-orange-500'
                                        }`}
                                >
                                    {btn.text}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>
            </View>
        </Modal>
    );
}

/**
 * Platform bağımsız alert yardımcı fonksiyonu.
 * Web'de ConfirmModal state'ini tetikler, native'de Alert.alert kullanır.
 *
 * Kullanım:
 *   const { confirmState, showConfirm } = useConfirm();
 *   showConfirm('Başlık', 'Mesaj', [{ text: 'Tamam', onPress: () => ... }]);
 *   <ConfirmModal {...confirmState} />
 */
export function useConfirm() {
    const [confirmState, setConfirmState] = React.useState<{
        visible: boolean;
        title: string;
        message: string;
        buttons: ConfirmButton[];
    }>({ visible: false, title: '', message: '', buttons: [] });

    const showConfirm = (title: string, message: string, buttons: ConfirmButton[]) => {
        if (Platform.OS !== 'web') {
            // Native: doğrudan Alert.alert kullan
            Alert.alert(title, message, buttons.map(btn => ({
                text: btn.text,
                style: btn.style,
                onPress: btn.onPress,
            })));
        } else {
            // Web: custom modal göster
            // Butonlara otomatik kapatma ekle
            const wrappedButtons = buttons.map(btn => ({
                ...btn,
                onPress: () => {
                    setConfirmState(s => ({ ...s, visible: false }));
                    btn.onPress?.();
                },
            }));
            setConfirmState({ visible: true, title, message, buttons: wrappedButtons });
        }
    };

    const hideConfirm = () => setConfirmState(s => ({ ...s, visible: false }));

    return { confirmState, showConfirm, hideConfirm };
}
