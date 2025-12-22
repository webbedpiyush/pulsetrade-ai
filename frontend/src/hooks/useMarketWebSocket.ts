"use client";

/**
 * WebSocket hook for connecting to PulseTrade backend.
 * Handles automatic reconnection and message parsing.
 */
import { useEffect, useRef, useCallback } from "react";
import { useMarketStore } from "@/stores/marketStore";

const WS_URL = "ws://localhost:8000/ws/market";

export function useMarketWebSocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const {
        setConnected,
        updateTick,
        addPricePoint,
        setAnalysis,
        pushAudioChunk,
        addAlert,
    } = useMarketStore();

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        console.log("Connecting to WebSocket...");
        const ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            console.log("WebSocket connected!");
            setConnected(true);
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected. Reconnecting in 3s...");
            setConnected(false);
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.onmessage = (event) => {
            // Handle binary data (audio)
            if (event.data instanceof Blob) {
                event.data.arrayBuffer().then((buffer) => {
                    pushAudioChunk(new Uint8Array(buffer));
                });
                return;
            }

            // Handle JSON data
            try {
                const data = JSON.parse(event.data);

                if (data.type === "tick") {
                    updateTick(data);
                    addPricePoint(data.symbol, data.price);

                    // Log breakouts
                    if (data.breakout) {
                        addAlert(data.symbol, data.direction, data.price);
                    }
                } else if (data.type === "analysis") {
                    setAnalysis({
                        symbol: data.symbol,
                        text: data.text,
                        timestamp: Date.now(),
                    });
                }
            } catch (e) {
                console.error("Failed to parse message:", e);
            }
        };

        wsRef.current = ws;
    }, [
        setConnected,
        updateTick,
        addPricePoint,
        setAnalysis,
        pushAudioChunk,
        addAlert,
    ]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        wsRef.current?.close();
        wsRef.current = null;
    }, []);

    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return { connect, disconnect };
}
