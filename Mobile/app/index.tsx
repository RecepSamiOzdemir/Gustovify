import { View, Text, TouchableOpacity, Image } from 'react-native';
import { Link, router } from 'expo-router';
import React from 'react';

export default function Landing() {
    return (
        <View className="flex-1 items-center justify-center bg-white px-6">
            <View className="items-center mb-10">
                <Text className="text-5xl font-bold text-orange-500 mb-2">Gustovify</Text>
                <Text className="text-gray-500 text-lg text-center">Akıllı Mutfak ve Envanter Yönetimi</Text>
            </View>

            <TouchableOpacity
                onPress={() => router.push('/(auth)/login')}
                className="bg-orange-500 w-full py-4 rounded-2xl items-center shadow-lg shadow-orange-200 mb-4">
                <Text className="text-white font-bold text-lg">Giriş Yap</Text>
            </TouchableOpacity>

            <TouchableOpacity
                onPress={() => router.push('/(auth)/register')}
                className="bg-white border-2 border-orange-500 w-full py-4 rounded-2xl items-center mb-8">
                <Text className="text-orange-500 font-bold text-lg">Kayıt Ol</Text>
            </TouchableOpacity>

            <Link href="/(tabs)/dashboard" className="mt-4 text-gray-400 text-sm">
                [Geliştirici Modu: Ana Sayfaya Git]
            </Link>
        </View>
    );
}

//cd Backend
//& c:/Users/recep/Gustovify/Backend/venv/Scripts/Activate.ps1  # Sanal ortamı aktif et (Windows)
//uvicorn main:app --reload


//cd Mobile
//npx expo start

//Telefonunu kabloyla bağladığında, telefonunun localhost:8000 adresini bilgisayarının localhost:8000 adresine yönlendirmek için şu komutu çalıştırman gerekiyor:
//adb reverse tcp:8000 tcp:8000
