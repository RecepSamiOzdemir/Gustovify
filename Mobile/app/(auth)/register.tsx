import { View, Text, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { useState } from 'react';
import { authService } from '../../services/auth';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRegister = async () => {
        if (!email || !password) {
            Alert.alert('Hata', 'Lütfen tüm alanları doldurun');
            return;
        }

        setLoading(true);
        try {
            await authService.register(email, password);
            Alert.alert('Başarılı', 'Kayıt olundu! Giriş yapabilirsiniz.', [
                { text: 'Tamam', onPress: () => router.back() }
            ]);
        } catch (error: any) {
            Alert.alert('Kayıt Hatası', error.message || 'Bir sorun oluştu');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View className="flex-1 items-center justify-center bg-white p-6">
            <Text className="text-3xl font-bold mb-8 text-orange-500">Kayıt Ol</Text>

            <TextInput
                className="w-full bg-gray-100 p-4 rounded-xl mb-4 border border-gray-200"
                placeholder="E-posta"
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                keyboardType="email-address"
            />

            <TextInput
                className="w-full bg-gray-100 p-4 rounded-xl mb-6 border border-gray-200"
                placeholder="Şifre"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
            />

            <TouchableOpacity
                onPress={handleRegister}
                disabled={loading}
                className={`w-full py-4 rounded-xl items-center shadow-lg shadow-orange-200 ${loading ? 'bg-orange-300' : 'bg-orange-500'}`}>
                {loading ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <Text className="text-white font-bold text-lg">Kayıt Ol</Text>
                )}
            </TouchableOpacity>

            <TouchableOpacity onPress={() => router.back()} className="mt-6">
                <Text className="text-gray-500">Zaten hesabın var mı? <Text className="text-orange-500 font-bold">Giriş Yap</Text></Text>
            </TouchableOpacity>
        </View>
    );
}
