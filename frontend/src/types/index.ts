/**
 * Shared TypeScript types for PulseTrade Crypto Edition
 */

// Trade event from Binance via WebSocket
export interface TradeEvent {
    symbol: string;      // BTCUSDT
    price: number;
    volume: number;
    time: number;        // Unix timestamp (ms)
}

// Alert triggered by technical analysis
export interface AlertEvent {
    symbol: string;
    price: number;
    triggerType: "RSI_HIGH" | "RSI_LOW" | "VOLUME_SPIKE" | "PRICE_LEVEL";
    triggerValue: number;
    message: string;
    time: number;
}

// AI analysis from Gemini
export interface AnalysisEvent {
    symbol: string;
    text: string;
    time: number;
}

// Market data for overview
export interface MarketData {
    symbol: string;
    name: string;
    price: number;
    change: number;      // Percentage
    volume: number;
}

// WebSocket message types
export type WSMessageType = "trade" | "alert" | "analysis" | "audio";

export interface WSMessage {
    type: WSMessageType;
    data: TradeEvent | AlertEvent | AnalysisEvent;
}
