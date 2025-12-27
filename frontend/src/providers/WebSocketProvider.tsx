"use client";

import { createContext, useContext, useEffect, useRef, ReactNode } from "react";
import { CryptoWebSocket } from "@/services/websocket";
import { useCryptoStore } from "@/stores/cryptoStore";
import { WS_URL } from "@/lib/constants";

interface WebSocketContextType {
    isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType>({
    isConnected: false,
});

export function useWebSocket() {
    return useContext(WebSocketContext);
}

interface WebSocketProviderProps {
    children: ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
    const wsRef = useRef<CryptoWebSocket | null>(null);
    const {
        connected,
        setConnected,
        updateTrade,
        addAlert,
        setAnalysis,
        setIsSpeaking
    } = useCryptoStore();

    useEffect(() => {
        // Create WebSocket connection
        wsRef.current = new CryptoWebSocket(WS_URL, {
            onConnect: () => setConnected(true),
            onDisconnect: () => setConnected(false),
            onTrade: (trade) => updateTrade(trade),
            onAlert: (alert) => addAlert(alert),
            onAnalysis: (analysis) => setAnalysis(analysis),
            onAudio: async (blob) => {
                // Play audio
                setIsSpeaking(true);
                const url = URL.createObjectURL(blob);
                const audio = new Audio(url);
                audio.onended = () => {
                    setIsSpeaking(false);
                    URL.revokeObjectURL(url);
                };
                await audio.play();
            },
        });

        wsRef.current.connect();

        return () => {
            wsRef.current?.disconnect();
        };
    }, [setConnected, updateTrade, addAlert, setAnalysis, setIsSpeaking]);

    return (
        <WebSocketContext.Provider value={{ isConnected: connected }}>
            {children}
        </WebSocketContext.Provider>
    );
}
