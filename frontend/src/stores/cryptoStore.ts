import { create } from "zustand";
import type { TradeEvent, AlertEvent, AnalysisEvent, MarketData } from "@/types";
import { TRACKED_SYMBOLS } from "@/lib/constants";

interface CryptoStore {
    // Connection state
    connected: boolean;
    setConnected: (connected: boolean) => void;

    // Trade data (latest tick per symbol)
    trades: Record<string, TradeEvent>;
    latestTrade: TradeEvent | null; // For log streaming
    updateTrade: (trade: TradeEvent) => void;

    // Alerts history
    alerts: AlertEvent[];
    addAlert: (alert: AlertEvent) => void;

    // AI analysis
    latestAnalysis: AnalysisEvent | null;
    setAnalysis: (analysis: AnalysisEvent) => void;

    // Voice state
    isSpeaking: boolean;
    setIsSpeaking: (speaking: boolean) => void;

    // Selected symbol for chart
    selectedSymbol: string;
    setSelectedSymbol: (symbol: string) => void;
}

export const useCryptoStore = create<CryptoStore>((set) => ({
    // Connection
    connected: false,
    setConnected: (connected) => set({ connected }),

    // Trades
    trades: {},
    latestTrade: null,
    updateTrade: (trade) =>
        set((state) => ({
            trades: { ...state.trades, [trade.symbol]: trade },
            latestTrade: trade,
        })),

    // Alerts
    alerts: [],
    addAlert: (alert) =>
        set((state) => ({
            alerts: [alert, ...state.alerts].slice(0, 50), // Keep last 50
        })),

    // Analysis
    latestAnalysis: null,
    setAnalysis: (analysis) => set({ latestAnalysis: analysis }),

    // Voice
    isSpeaking: false,
    setIsSpeaking: (speaking) => set({ isSpeaking: speaking }),

    // Selected symbol
    selectedSymbol: TRACKED_SYMBOLS[0],
    setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
}));
