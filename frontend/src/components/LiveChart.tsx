"use client";

import { useEffect, useRef, memo } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from "lightweight-charts";
import { useCryptoStore } from "@/stores/cryptoStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * Real-time candlestick chart using TradingView Lightweight Charts.
 * Uses refs for updates to avoid React re-renders.
 */
export const LiveChart = memo(function LiveChart() {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

    const { selectedSymbol, trades } = useCryptoStore();

    // Initialize chart
    useEffect(() => {
        if (!containerRef.current) return;

        const chart = createChart(containerRef.current, {
            layout: {
                background: { color: "transparent" },
                textColor: "#94a3b8",
            },
            grid: {
                vertLines: { color: "#1e293b" },
                horzLines: { color: "#1e293b" },
            },
            width: containerRef.current.clientWidth,
            height: containerRef.current.clientHeight,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: "#1e293b",
            },
            rightPriceScale: {
                borderColor: "#1e293b",
            },
            crosshair: {
                mode: 1, // Magnet mode
            },
        });

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: "#10b981",
            downColor: "#ef4444",
            borderUpColor: "#10b981",
            borderDownColor: "#ef4444",
            wickUpColor: "#10b981",
            wickDownColor: "#ef4444",
        });

        chartRef.current = chart;
        seriesRef.current = candlestickSeries;

        // Handle resize
        const handleResize = () => {
            if (containerRef.current) {
                chart.applyOptions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight,
                });
            }
        };

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
            chart.remove();
        };
    }, []);

    // Update chart with new trades (using ref to avoid re-renders)
    useEffect(() => {
        const trade = trades[selectedSymbol];
        if (!trade || !seriesRef.current) return;

        const time = Math.floor(trade.time / 1000) as Time;
        const price = trade.price;

        // For demo, create candle from trade
        const candle: CandlestickData = {
            time,
            open: price * 0.999,
            high: price * 1.001,
            low: price * 0.998,
            close: price,
        };

        seriesRef.current.update(candle);
    }, [trades, selectedSymbol]);

    return (
        <div className="h-full w-full flex flex-col">
            <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm text-emerald-400">
                    {selectedSymbol}
                </span>
                <span className="text-xs text-slate-400">
                    {trades[selectedSymbol]
                        ? `$${trades[selectedSymbol].price.toLocaleString()}`
                        : "Loading..."
                    }
                </span>
            </div>
            <div ref={containerRef} className="flex-1 min-h-[200px]" />
        </div>
    );
});
