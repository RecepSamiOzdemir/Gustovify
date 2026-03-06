import { Platform } from 'react-native';

const localhost = Platform.select({
    android: '127.0.0.1', // Changed from localhost to 127.0.0.1 for adb reverse reliability
    ios: '192.168.2.108',
    web: 'localhost',
    default: 'localhost',
});

export const API_URL = `http://${localhost}:8000`;
