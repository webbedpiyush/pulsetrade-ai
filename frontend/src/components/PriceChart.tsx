"use client";

/**
 * Real-time price chart using TradingView Lightweight Charts.
 * Includes time scale selector (1D/1W/1M/1Y).
 */
import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ISeriesApi, LineSeries, UTCTimestamp, ColorType } from "lightweight-charts";
import { useMarketStore } from "@/stores/marketStore";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Maximize2, Activity, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

// Time scale options (for live streaming data)
const TIME_SCALES = [
    { key: "5M", label: "5m", seconds: 300 },
    { key: "15M", label: "15m", seconds: 900 },
    { key: "1H", label: "1h", seconds: 3600 },
    { key: "ALL", label: "All", seconds: Infinity },
] as const;

type TimeScaleKey = typeof TIME_SCALES[number]["key"];

// Map market prefix to currency symbol
function getCurrencySymbol(symbol: string): string {
    if (symbol.startsWith("NSE:") || symbol.startsWith("BSE:")) return "₹";
    if (symbol.startsWith("NYSE:") || symbol.startsWith("NASDAQ:")) return "$";
    if (symbol.startsWith("LSE:")) return "£";
    return "";
}

function getMarketLabel(symbol: string): string {
    if (symbol.startsWith("NSE:")) return "NSE";
    if (symbol.startsWith("BSE:")) return "BSE";
    if (symbol.startsWith("NYSE:")) return "NYSE";
    if (symbol.startsWith("NASDAQ:")) return "NASDAQ";
    if (symbol.startsWith("LSE:")) return "LSE";
    return "Market";
}

export function PriceChart() {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);
    const [timeScale, setTimeScale] = useState<TimeScaleKey>("5M");

    const { selectedSymbol, priceHistory } = useMarketStore();
    const history = priceHistory[selectedSymbol] || [];

    const currency = getCurrencySymbol(selectedSymbol);
    const marketLabel = getMarketLabel(selectedSymbol);
    const displaySymbol = selectedSymbol.split(":")[1] || selectedSymbol;

    // Get latest price from history
    const latestPrice = history.length > 0 ? history[history.length - 1].value : null;

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Themed colors
        const backgroundColor = "rgba(15, 23, 42, 0)";
        const gridColor = "rgba(255, 255, 255, 0.05)";
        const textColor = "#94a3b8";

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: backgroundColor },
                textColor: textColor,
            },
            grid: {
                vertLines: { color: gridColor },
                horzLines: { color: gridColor },
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
            timeScale: {
                timeVisible: true,
                secondsVisible: true,
                borderColor: gridColor,
            },
            rightPriceScale: {
                borderColor: gridColor,
            },
        });

        const series = chart.addSeries(LineSeries, {
            color: "#38bdf8",
            lineWidth: 2,
            crosshairMarkerVisible: true,
        });

        chartRef.current = chart;
        seriesRef.current = series;

        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
            chart.remove();
        };
    }, []);

    // Update chart data when history or time scale changes
    useEffect(() => {
        if (seriesRef.current && history.length > 0) {
            const selectedScale = TIME_SCALES.find(s => s.key === timeScale);
            const cutoffTime = Date.now() / 1000 - (selectedScale?.seconds || 86400);

            // Filter history based on time scale
            const filteredHistory = history.filter(h => h.time >= cutoffTime);

            const chartData = filteredHistory.map(h => ({
                time: h.time as UTCTimestamp,
                value: h.value
            }));

            seriesRef.current.setData(chartData);

            // Fit content to view
            if (chartRef.current) {
                chartRef.current.timeScale().fitContent();
            }
        }
    }, [history, timeScale]);

    return (
        <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b border-white/5">
                <div className="flex flex-col">
                    <CardTitle className="text-xl font-medium text-white flex items-center gap-2">
                        <span className="text-slate-400 text-sm">{marketLabel}:</span>
                        {displaySymbol}
                        <Badge variant="outline" className="ml-2 border-brand-500/30 text-brand-300 bg-brand-500/10 hover:bg-brand-500/20">
                            LIVE
                        </Badge>
                    </CardTitle>
                    <CardDescription className="text-slate-500 text-xs flex items-center gap-2 mt-1">
                        {latestPrice && (
                            <span className="text-lg font-mono text-white">
                                {currency}{latestPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </span>
                        )}
                        <span className="text-slate-500">Real-time market data</span>
                    </CardDescription>
                </div>

                <div className="flex items-center gap-2">
                    {/* Time Scale Buttons */}
                    <div className="flex bg-slate-900/80 rounded-lg p-0.5 border border-white/5">
                        {TIME_SCALES.map((scale) => (
                            <Button
                                key={scale.key}
                                variant="ghost"
                                size="sm"
                                onClick={() => setTimeScale(scale.key)}
                                className={cn(
                                    "h-7 px-3 text-xs font-medium transition-all",
                                    timeScale === scale.key
                                        ? "bg-brand-500/20 text-brand-300 hover:bg-brand-500/30"
                                        : "text-slate-500 hover:text-white hover:bg-slate-800"
                                )}
                            >
                                {scale.label}
                            </Button>
                        ))}
                    </div>

                    <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-white">
                        <TrendingUp className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-white">
                        <Maximize2 className="w-4 h-4" />
                    </Button>
                </div>
            </CardHeader>

            <CardContent className="p-0 flex-1 min-h-[400px]">
                <div ref={chartContainerRef} className="w-full h-full" />
            </CardContent>
        </Card>
    );
}
