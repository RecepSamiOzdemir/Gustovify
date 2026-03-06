import { View, Text, TouchableOpacity, ScrollView, Alert, ActivityIndicator, TextInput, Platform } from 'react-native';
import { useState, useEffect } from 'react';
import { router } from 'expo-router';
import { userService } from '../../services/user';
import { User, Allergen, DietaryPreference } from '../../types';
import { authService } from '../../services/auth';
import { Colors } from '../../constants/Colors';

export default function Profile() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    // Dynamic Lists
    const [allAllergens, setAllAllergens] = useState<Allergen[]>([]);
    const [allPreferences, setAllPreferences] = useState<DietaryPreference[]>([]);

    // Selection States
    const [selectedAllergenIds, setSelectedAllergenIds] = useState<number[]>([]);
    const [selectedPreferenceIds, setSelectedPreferenceIds] = useState<number[]>([]);

    // Personal Details State
    const [fullName, setFullName] = useState('');
    const [city, setCity] = useState('');
    const [age, setAge] = useState('');
    const [gender, setGender] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            // Parallel Fetching
            const [userData, allergensData, prefsData] = await Promise.all([
                userService.getProfile(),
                userService.getAllergens(),
                userService.getPreferences()
            ]);

            setUser(userData);
            setAllAllergens(allergensData);
            setAllPreferences(prefsData);

            // Set Personal Details
            setFullName(userData.full_name || '');
            setCity(userData.city || '');
            setAge(userData.age ? userData.age.toString() : '');
            setGender(userData.gender || '');

            // Set Selected Items from Relations
            if (userData.related_allergens) {
                setSelectedAllergenIds(userData.related_allergens.map(a => a.id));
            }
            if (userData.related_preferences) {
                setSelectedPreferenceIds(userData.related_preferences.map(p => p.id));
            }

        } catch (error: any) {
            Alert.alert('Hata', 'Veriler yüklenirken bir sorun oluştu.');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const toggleSelection = (id: number, currentIds: number[], setIds: (ids: number[]) => void) => {
        if (currentIds.includes(id)) {
            setIds(currentIds.filter(item => item !== id));
        } else {
            setIds([...currentIds, id]);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);

            await userService.updateProfile({
                full_name: fullName,
                city: city,
                age: age ? parseInt(age) : undefined,
                gender: gender,
                allergen_ids: selectedAllergenIds,
                preference_ids: selectedPreferenceIds
            });

            Alert.alert('Başarılı', 'Profiliniz ve tercihleriniz güncellendi.');
            setIsEditing(false);
            loadData();
        } catch (error: any) {
            Alert.alert('Hata', 'Güncelleme başarısız: ' + error.message);
        } finally {
            setSaving(false);
        }
    };

    const handleCancel = () => {
        setIsEditing(false);
        loadData();
    };

    const handleLogout = () => {
        if (Platform.OS === 'web') {
            if (window.confirm('Hesabınızdan çıkış yapmak istediğinize emin misiniz?')) {
                performLogout();
            }
        } else {
            Alert.alert(
                'Çıkış Yap',
                'Hesabınızdan çıkış yapmak istediğinize emin misiniz?',
                [
                    { text: 'Vazgeç', style: 'cancel' },
                    {
                        text: 'Çıkış Yap',
                        style: 'destructive',
                        onPress: performLogout
                    }
                ]
            );
        }
    };

    const performLogout = async () => {
        try {
            await authService.logout();
            // Clear any local state if needed
            setUser(null);

            // Navigate to login
            if (router.canGoBack()) {
                // On web, dismissAll might not work as expected or might be aggressive.
                // But performLogout -> replaces to login is standard.
                // We'll just replace.
            }
            router.replace('/(auth)/login');
        } catch (error) {
            console.error('Logout error:', error);
            Alert.alert('Hata', 'Çıkış yapılırken bir sorun oluştu.');
        }
    };

    if (loading) {
        return (
            <View className="flex-1 justify-center items-center bg-gray-50">
                <ActivityIndicator size="large" color={Colors.primary.DEFAULT} />
            </View>
        );
    }

    // Chip Component
    const SelectableChip = ({ label, selected, onPress }: { label: string, selected: boolean, onPress: () => void }) => (
        <TouchableOpacity
            onPress={onPress}
            className={`px-4 py-2 rounded-full mr-2 mb-2 border ${selected
                ? 'bg-orange-100 border-orange-500'
                : 'bg-white border-gray-200'
                }`}
        >
            <Text className={`${selected ? 'text-orange-700 font-medium' : 'text-gray-600'}`}>
                {label} {selected && '✓'}
            </Text>
        </TouchableOpacity>
    );

    return (
        <ScrollView className="flex-1 bg-gray-50 pt-12">
            <View className="px-6 mb-6 flex-row justify-between items-center">
                <View>
                    <Text className="text-3xl font-bold text-gray-900 mb-2">Profil</Text>
                    <Text className="text-gray-500">Hesap ayarlarınızı ve tercihlerinizi yönetin.</Text>
                </View>
                {!isEditing && (
                    <TouchableOpacity onPress={() => setIsEditing(true)} className="bg-orange-100 p-3 rounded-full">
                        <Text className="text-2xl">✏️</Text>
                    </TouchableOpacity>
                )}
            </View>

            {/* User Card */}
            <View className="mx-4 bg-white p-4 rounded-2xl shadow-sm mb-6 flex-row items-center border border-gray-100">
                <View className="w-16 h-16 bg-orange-100 rounded-full items-center justify-center mr-4">
                    <Text className="text-2xl">👤</Text>
                </View>
                <View>
                    <Text className="text-lg font-bold text-gray-900">{fullName || user?.email?.split('@')[0]}</Text>
                    <Text className="text-gray-500">{user?.email}</Text>
                </View>
            </View>

            {/* Personal Details */}
            <View className="mx-4 bg-white p-4 rounded-2xl shadow-sm mb-6 border border-gray-100">
                <Text className="text-lg font-bold text-gray-900 mb-4">Kişisel Bilgiler</Text>

                <View className="mb-4">
                    <Text className="text-gray-500 text-xs uppercase mb-1 ml-1">Ad Soyad</Text>
                    {isEditing ? (
                        <TextInput
                            className="bg-gray-50 p-3 rounded-xl border border-gray-200 text-gray-800"
                            placeholder="Adınız Soyadınız"
                            value={fullName}
                            onChangeText={setFullName}
                        />
                    ) : (
                        <Text className="text-gray-900 text-lg font-medium ml-1">{fullName || '-'}</Text>
                    )}
                </View>

                <View className="flex-row gap-4 mb-4">
                    <View className="flex-1">
                        <Text className="text-gray-500 text-xs uppercase mb-1 ml-1">Yaş</Text>
                        {isEditing ? (
                            <TextInput
                                className="bg-gray-50 p-3 rounded-xl border border-gray-200 text-gray-800"
                                placeholder="Yaş"
                                value={age}
                                onChangeText={setAge}
                                keyboardType="numeric"
                            />
                        ) : (
                            <Text className="text-gray-900 text-lg font-medium ml-1">{age || '-'}</Text>
                        )}
                    </View>
                    <View className="flex-1">
                        <Text className="text-gray-500 text-xs uppercase mb-1 ml-1">Cinsiyet</Text>
                        {isEditing ? (
                            <TextInput
                                className="bg-gray-50 p-3 rounded-xl border border-gray-200 text-gray-800"
                                placeholder="Örn: Kadın"
                                value={gender}
                                onChangeText={setGender}
                            />
                        ) : (
                            <Text className="text-gray-900 text-lg font-medium ml-1">{gender || '-'}</Text>
                        )}
                    </View>
                </View>

                <View>
                    <Text className="text-gray-500 text-xs uppercase mb-1 ml-1">Şehir</Text>
                    {isEditing ? (
                        <TextInput
                            className="bg-gray-50 p-3 rounded-xl border border-gray-200 text-gray-800"
                            placeholder="Yaşadığınız Şehir"
                            value={city}
                            onChangeText={setCity}
                        />
                    ) : (
                        <Text className="text-gray-900 text-lg font-medium ml-1">{city || '-'}</Text>
                    )}
                </View>
            </View>

            {/* Preferences Section */}
            <View className="mx-4 bg-white p-4 rounded-2xl shadow-sm mb-6 border border-gray-100">
                <Text className="text-lg font-bold text-gray-900 mb-2">Beslenme Tercihleri</Text>
                {isEditing && <Text className="text-gray-400 text-sm mb-4">Size uygun olanları seçin.</Text>}

                <View className="flex-row flex-wrap">
                    {isEditing ? (
                        allPreferences.map(pref => (
                            <SelectableChip
                                key={pref.id}
                                label={pref.name}
                                selected={selectedPreferenceIds.includes(pref.id)}
                                onPress={() => toggleSelection(pref.id, selectedPreferenceIds, setSelectedPreferenceIds)}
                            />
                        ))
                    ) : (
                        selectedPreferenceIds.length > 0 ? (
                            allPreferences
                                .filter(p => selectedPreferenceIds.includes(p.id))
                                .map(pref => (
                                    <View key={pref.id} className="bg-green-100 px-4 py-2 rounded-full mr-2 mb-2 border border-green-200">
                                        <Text className="text-green-700 font-medium">{pref.name}</Text>
                                    </View>
                                ))
                        ) : (
                            <Text className="text-gray-500 italic">Tercih belirtilmemiş.</Text>
                        )
                    )}
                </View>
            </View>

            {/* Allergies Section */}
            <View className="mx-4 bg-white p-4 rounded-2xl shadow-sm mb-6 border border-gray-100">
                <Text className="text-lg font-bold text-gray-900 mb-2">Alerjiler</Text>
                {isEditing && <Text className="text-gray-400 text-sm mb-4">Kaçındığınız gıdaları seçin.</Text>}

                <View className="flex-row flex-wrap">
                    {isEditing ? (
                        allAllergens.map(allergen => (
                            <SelectableChip
                                key={allergen.id}
                                label={allergen.name}
                                selected={selectedAllergenIds.includes(allergen.id)}
                                onPress={() => toggleSelection(allergen.id, selectedAllergenIds, setSelectedAllergenIds)}
                            />
                        ))
                    ) : (
                        selectedAllergenIds.length > 0 ? (
                            allAllergens
                                .filter(a => selectedAllergenIds.includes(a.id))
                                .map(allergen => (
                                    <View key={allergen.id} className="bg-red-100 px-4 py-2 rounded-full mr-2 mb-2 border border-red-200">
                                        <Text className="text-red-700 font-medium">{allergen.name}</Text>
                                    </View>
                                ))
                        ) : (
                            <Text className="text-gray-500 italic">Alerji belirtilmemiş.</Text>
                        )
                    )}
                </View>
            </View>

            {/* Action Buttons */}
            <View className="px-4 mb-20 gap-3">
                {isEditing ? (
                    <>
                        <TouchableOpacity
                            onPress={handleSave}
                            disabled={saving}
                            className="bg-indigo-600 py-4 rounded-xl items-center shadow-lg shadow-indigo-200"
                        >
                            {saving ? (
                                <ActivityIndicator color="white" />
                            ) : (
                                <Text className="text-white font-bold text-lg">Kaydet</Text>
                            )}
                        </TouchableOpacity>
                        <TouchableOpacity
                            onPress={handleCancel}
                            disabled={saving}
                            className="bg-gray-200 py-4 rounded-xl items-center"
                        >
                            <Text className="text-gray-700 font-bold text-lg">Vazgeç</Text>
                        </TouchableOpacity>
                    </>
                ) : (
                    <TouchableOpacity
                        onPress={handleLogout}
                        className="bg-red-50 py-4 rounded-xl items-center border border-red-100"
                    >
                        <Text className="text-red-600 font-bold text-lg">Çıkış Yap</Text>
                    </TouchableOpacity>
                )}
            </View>
        </ScrollView>
    );
}
