import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <View className="flex-1 items-center justify-center bg-white px-6">
                    <Text className="text-2xl font-bold text-gray-800 mb-2">Bir Hata Olustu</Text>
                    <Text className="text-gray-500 text-center mb-6">
                        Beklenmeyen bir sorun yasandi. Lutfen tekrar deneyin.
                    </Text>
                    <TouchableOpacity
                        onPress={this.handleReset}
                        className="bg-orange-500 px-8 py-3 rounded-xl"
                        activeOpacity={0.8}
                    >
                        <Text className="text-white font-semibold text-base">Tekrar Dene</Text>
                    </TouchableOpacity>
                </View>
            );
        }

        return this.props.children;
    }
}
