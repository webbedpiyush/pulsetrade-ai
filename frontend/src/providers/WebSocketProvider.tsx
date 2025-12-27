"use client";

import { createContext, useContext, useEffect, useRef, ReactNode, useState } from "react";
import { CryptoWebSocket } from "@/services/websocket";
import { useCryptoStore } from "@/stores/cryptoStore";
import { WS_URL } from "@/lib/constants";
import type { AnalysisEvent } from "@/types";

interface WebSocketContextType {
    isConnected: boolean;
    isAudioUnlocked: boolean;
    unlockAudio: () => void;
}

const WebSocketContext = createContext<WebSocketContextType>({
    isConnected: false,
    isAudioUnlocked: false,
    unlockAudio: () => { },
});

export function useWebSocket() {
    return useContext(WebSocketContext);
}

interface WebSocketProviderProps {
    children: ReactNode;
}

// Queue item that pairs audio with its analysis text
interface QueuedAudio {
    blob: Blob;
    analysis: AnalysisEvent | null;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
    const wsRef = useRef<CryptoWebSocket | null>(null);
    // Queue pairs audio blobs with their corresponding analysis text
    const audioQueueRef = useRef<QueuedAudio[]>([]);
    // Pending analysis that's waiting for its audio
    const pendingAnalysisRef = useRef<AnalysisEvent | null>(null);
    const isPlayingRef = useRef(false);
    // Track if user has interacted with the page to enable audio
    const [isAudioUnlocked, setIsAudioUnlocked] = useState(false);
    const audioUnlockedRef = useRef(false);

    // Function to unlock audio - call this on user interaction
    const unlockAudio = () => {
        if (audioUnlockedRef.current) return;

        // Create and play a silent audio to unlock the audio context
        const silentAudio = new Audio("data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA");
        silentAudio.volume = 0;
        silentAudio.play()
            .then(() => {
                audioUnlockedRef.current = true;
                setIsAudioUnlocked(true);
                console.log("[Audio] Unlocked via user interaction");
                // Try to play any queued audio
                playNextAudio();
            })
            .catch(() => {
                // Silent fail - user may not have interacted yet
            });
    };

    const {
        connected,
        setConnected,
        updateTrade,
        addAlert,
        setAnalysis,
        setIsSpeaking
    } = useCryptoStore();

    // Play audio queue one at a time, updating text in sync
    const playNextAudio = async () => {
        // Don't play until user has interacted with the page
        if (!audioUnlockedRef.current) {
            console.log("[Audio] Waiting for user interaction to unlock audio");
            return;
        }

        if (isPlayingRef.current || audioQueueRef.current.length === 0) {
            return;
        }

        isPlayingRef.current = true;
        setIsSpeaking(true);

        const queuedItem = audioQueueRef.current.shift()!;

        // Update the displayed text when audio starts playing
        if (queuedItem.analysis) {
            setAnalysis(queuedItem.analysis);
        }

        const url = URL.createObjectURL(queuedItem.blob);
        const audio = new Audio(url);

        audio.onended = () => {
            URL.revokeObjectURL(url);
            isPlayingRef.current = false;

            if (audioQueueRef.current.length === 0) {
                setIsSpeaking(false);
            }

            // Play next in queue
            playNextAudio();
        };

        audio.onerror = () => {
            URL.revokeObjectURL(url);
            isPlayingRef.current = false;
            setIsSpeaking(false);
            // Try next
            playNextAudio();
        };

        try {
            await audio.play();
        } catch (e) {
            console.error("[Audio] Playback error:", e);
            isPlayingRef.current = false;
            setIsSpeaking(false);
            playNextAudio();
        }
    };

    useEffect(() => {
        // Create WebSocket connection
        wsRef.current = new CryptoWebSocket(WS_URL, {
            onConnect: () => setConnected(true),
            onDisconnect: () => setConnected(false),
            onTrade: (trade) => updateTrade(trade),
            onAlert: (alert) => addAlert(alert),
            onAnalysis: (analysis) => {
                // Store analysis to pair with the next audio blob
                pendingAnalysisRef.current = analysis;
            },
            onAudio: async (blob) => {
                // Pair audio with pending analysis text
                const analysis = pendingAnalysisRef.current;
                pendingAnalysisRef.current = null;

                audioQueueRef.current.push({ blob, analysis });
                console.log(`[Audio] Queued with text, total: ${audioQueueRef.current.length}`);
                playNextAudio();
            },
        });

        wsRef.current.connect();

        return () => {
            wsRef.current?.disconnect();
        };
    }, [setConnected, updateTrade, addAlert, setAnalysis, setIsSpeaking]);

    // Add click listener to unlock audio on first user interaction
    useEffect(() => {
        const handleInteraction = () => {
            unlockAudio();
        };

        document.addEventListener("click", handleInteraction, { once: true });
        document.addEventListener("touchstart", handleInteraction, { once: true });
        document.addEventListener("keydown", handleInteraction, { once: true });

        return () => {
            document.removeEventListener("click", handleInteraction);
            document.removeEventListener("touchstart", handleInteraction);
            document.removeEventListener("keydown", handleInteraction);
        };
    }, []);

    return (
        <WebSocketContext.Provider value={{ isConnected: connected, isAudioUnlocked, unlockAudio }}>
            {children}
        </WebSocketContext.Provider>
    );
}
