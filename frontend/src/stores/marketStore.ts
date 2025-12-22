"use client";

/**
 * Market data store using Zustand.
 * Manages real-time tick data, alerts, and audio streaming.
 */
import { create } from "zustand";

interface Tick {
  symbol: string;
  price: number;
  volume: number;
  breakout: boolean;
  direction: string;
  sma_5: number;
  volatility: number;
  timestamp?: number;
}

interface Analysis {
  symbol: string;
  text: string;
  timestamp: number;
}

interface MarketStore {
  // Connection state
  connected: boolean;
  setConnected: (connected: boolean) => void;

  // Tick data
  ticks: Record<string, Tick>;
  updateTick: (tick: Tick) => void;

  // Price history for charts
  priceHistory: Record<string, { time: number; value: number }[]>;
  addPricePoint: (symbol: string, price: number) => void;

  // AI Analysis
  latestAnalysis: Analysis | null;
  setAnalysis: (analysis: Analysis) => void;

  // Audio queue for MSE jitter buffer
  audioQueue: Uint8Array[];
  pushAudioChunk: (chunk: Uint8Array) => void;
  shiftAudioChunk: () => Uint8Array | undefined;

  // Breakout alerts
  alerts: { symbol: string; direction: string; price: number; time: number }[];
  addAlert: (symbol: string, direction: string, price: number) => void;

  // Selected symbol for chart
  selectedSymbol: string;
  setSelectedSymbol: (symbol: string) => void;
}

export const useMarketStore = create<MarketStore>((set, get) => ({
  // Connection
  connected: false,
  setConnected: (connected) => set({ connected }),

  // Ticks
  ticks: {},
  updateTick: (tick) =>
    set((state) => ({
      ticks: { ...state.ticks, [tick.symbol]: tick },
    })),

  // Price history (last 100 points per symbol)
  priceHistory: {},
  addPricePoint: (symbol, price) =>
    set((state) => {
      const history = state.priceHistory[symbol] || [];
      const newPoint = { time: Date.now() / 1000, value: price };
      const updated = [...history, newPoint].slice(-100);
      return {
        priceHistory: { ...state.priceHistory, [symbol]: updated },
      };
    }),

  // Analysis
  latestAnalysis: null,
  setAnalysis: (analysis) => set({ latestAnalysis: analysis }),

  // Audio queue
  audioQueue: [],
  pushAudioChunk: (chunk) =>
    set((state) => ({
      audioQueue: [...state.audioQueue, chunk],
    })),
  shiftAudioChunk: () => {
    const { audioQueue } = get();
    if (audioQueue.length === 0) return undefined;
    const [first, ...rest] = audioQueue;
    set({ audioQueue: rest });
    return first;
  },

  // Alerts
  alerts: [],
  addAlert: (symbol, direction, price) =>
    set((state) => ({
      alerts: [
        { symbol, direction, price, time: Date.now() },
        ...state.alerts,
      ].slice(0, 50),
    })),

  // Selected symbol
  selectedSymbol: "NSE:RELIANCE",
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
}));
