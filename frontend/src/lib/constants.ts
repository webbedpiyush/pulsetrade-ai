/**
 * Application constants
 */

// WebSocket
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Tracked symbols
export const TRACKED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"] as const;
export type TrackedSymbol = (typeof TRACKED_SYMBOLS)[number];

// Trigger thresholds
export const RSI_OVERBOUGHT = 80;
export const RSI_OVERSOLD = 20;
export const VOLUME_SPIKE_MULTIPLIER = 5;
export const PRICE_CHANGE_THRESHOLD = 0.01; // 1%

// Cooldown periods (ms)
export const ALERT_COOLDOWN = 5 * 60 * 1000; // 5 minutes
