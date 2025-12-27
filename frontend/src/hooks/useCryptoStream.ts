"use client";

import { useEffect, useRef, useCallback } from "react";
import { useCryptoStore } from "@/stores/cryptoStore";
import type { IChartApi } from "lightweight-charts";

/**
 * Hook for consuming crypto stream data
 * Uses refs for chart updates to avoid React re-renders
 */
export function useCryptoStream() {
    const chartRef = useRef<IChartApi | null>(null);
    const { trades, selectedSymbol } = useCryptoStore();

    // Get latest trade for selected symbol
    const latestTrade = trades[selectedSymbol];

    // Update chart without React state
    const updateChart = useCallback(
        (time: number, value: number) => {
            if (chartRef.current) {
                // Chart update logic will be implemented in LiveChart component
            }
        },
        []
    );

    return {
        chartRef,
        latestTrade,
        updateChart,
    };
}
