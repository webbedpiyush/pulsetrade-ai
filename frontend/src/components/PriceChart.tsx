"use client";

/**
 * Real-time price chart using TradingView Lightweight Charts.
 * Updated with shadcn/ui Card and themed styling.
 */
import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, LineSeries, UTCTimestamp, ColorType } from "lightweight-charts";
import { useMarketStore } from "@/stores/marketStore";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Maximize2, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

export function PriceChart() {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);

    const { selectedSymbol, priceHistory } = useMarketStore();
    const history = priceHistory[selectedSymbol] || [];

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Themed colors
        const backgroundColor = "rgba(15, 23, 42, 0)"; // Transparent to let card bg show
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
            color: "#38bdf8", // brand-400 (Sky Blue)
            lineWidth: 2,
            crosshairMarkerVisible: true,
            // areaStyle logic if we switched to AreaSeries
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

    // Update chart data
    useEffect(() => {
        if (seriesRef.current && history.length > 0) {
            const chartData = history.map(h => ({
                time: h.time as UTCTimestamp,
                value: h.value
            }));
            seriesRef.current.setData(chartData);
        }
    }, [history]);

    return (
        <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b border-white/5">
                <div className="flex flex-col">
                    <CardTitle className="text-xl font-medium text-white flex items-center gap-2">
                        {selectedSymbol}
                        <Badge variant="outline" className="ml-2 border-brand-500/30 text-brand-300 bg-brand-500/10 hover:bg-brand-500/20">
                            LIVE
                        </Badge>
                    </CardTitle>
                    <CardDescription className="text-slate-500 text-xs">
                        Real-time visualization from NIFTY 50 feed
                    </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-white">
                        <Activity className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-white">
                        <Maximize2 className="w-4 h-4" />
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="p-0 flex-1 min-h-[400px]">
                {/* Chart Container */}
                <div ref={chartContainerRef} className="w-full h-full" />
            </CardContent>
        </Card>
    );
}
