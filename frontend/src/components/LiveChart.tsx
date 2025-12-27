"use client";

import { useEffect, useRef, memo } from "react";
import { createChart, IChartApi, ISeriesApi, LineSeries, LineData, Time } from "lightweight-charts";
import { useCryptoStore } from "@/stores/cryptoStore";

/**
 * Real-time line chart using TradingView Lightweight Charts v4.
 * Uses refs for updates to avoid React re-renders.
 */
export const LiveChart = memo(function LiveChart() {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);

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
                mode: 1,
            },
        });

        // v4 API: use addSeries with LineSeries
        const lineSeries = chart.addSeries(LineSeries, {
            color: "#10b981",
            lineWidth: 2,
            crosshairMarkerVisible: true,
            crosshairMarkerRadius: 4,
        });

        chartRef.current = chart;
        seriesRef.current = lineSeries as ISeriesApi<"Line">;

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

    // Track last time to avoid duplicate timestamp errors
    const lastTimeRef = useRef<number>(0);
    // Track current symbol to detect changes
    const currentSymbolRef = useRef<string>(selectedSymbol);

    // Reset chart when symbol changes
    useEffect(() => {
        if (currentSymbolRef.current !== selectedSymbol) {
            // Symbol changed - reset everything
            currentSymbolRef.current = selectedSymbol;
            lastTimeRef.current = 0;

            // Clear existing chart data
            if (seriesRef.current) {
                seriesRef.current.setData([]);
            }
        }
    }, [selectedSymbol]);

    // Update chart with new trades
    useEffect(() => {
        const trade = trades[selectedSymbol];
        if (!trade || !seriesRef.current) return;

        const timeInSeconds = Math.floor(trade.time / 1000);

        // Lightweight Charts requires strictly increasing timestamps
        // Skip updates with same or older timestamps
        if (timeInSeconds <= lastTimeRef.current) {
            return;
        }

        lastTimeRef.current = timeInSeconds;

        try {
            seriesRef.current.update({
                time: timeInSeconds as Time,
                value: trade.price,
            });
        } catch (e) {
            // Ignore chart update errors (e.g., out-of-order data)
            console.debug("[Chart] Update skipped:", e);
        }
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
