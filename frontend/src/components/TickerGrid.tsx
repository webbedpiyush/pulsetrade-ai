"use client";

/**
 * Real-time stock ticker display.
 * Updated with shadcn/ui Card and ScrollArea.
 */
import { useMarketStore } from "@/stores/marketStore";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowUpRight, ArrowDownRight, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

export function TickerGrid() {
    const { ticks, selectedSymbol, setSelectedSymbol } = useMarketStore();
    const tickList = Object.values(ticks);

    if (tickList.length === 0) {
        return (
            <Card className="bg-slate-950/50 border-white/5 shadow-inner">
                <CardHeader>
                    <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                        <Activity className="w-5 h-5 text-brand-400" /> Live Tickers
                    </CardTitle>
                    <CardDescription>Waiting for real-time market data...</CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Skeleton */}
                    <div className="grid grid-cols-2 gap-3 opacity-50">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-16 bg-slate-900 rounded-lg animate-pulse" />
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 overflow-hidden h-full flex flex-col">
            <CardHeader className="py-4 border-b border-white/5">
                <CardTitle className="text-lg font-medium text-white flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <Activity className="w-5 h-5 text-brand-400" /> Market Feed
                    </span>
                    <span className="text-xs text-slate-500 font-normal">{tickList.length} Active</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1">
                <ScrollArea className="h-[300px] w-full p-4">
                    <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {tickList.map((tick) => (
                            <motion.button
                                key={tick.symbol}
                                onClick={() => setSelectedSymbol(tick.symbol)}
                                className={cn(
                                    "p-3 rounded-lg text-left transition-all border group relative overflow-hidden",
                                    selectedSymbol === tick.symbol
                                        ? "bg-brand-500/10 border-brand-500/50 shadow-[0_0_15px_-3px_rgba(14,165,233,0.3)]"
                                        : "bg-slate-900/60 border-white/5 hover:border-white/10 hover:bg-slate-800"
                                )}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-semibold text-slate-300 group-hover:text-white truncate max-w-[80px]">
                                        {tick.symbol.replace("NSE:", "")}
                                    </span>
                                    {tick.breakout && (
                                        <span className={cn("flex h-2 w-2 rounded-full", tick.direction === "UP" ? "bg-green-500 shadow-green-500/50" : "bg-red-500 shadow-red-500/50")} />
                                    )}
                                </div>
                                <div className="flex items-baseline gap-1">
                                    <span className={cn(
                                        "text-sm font-mono font-bold",
                                        tick.direction === "UP" ? "text-green-400" : "text-slate-200"
                                    )}>
                                        ₹{tick.price.toLocaleString("en-IN", { minimumFractionDigits: 1 })}
                                    </span>
                                </div>

                                <div className="absolute right-2 bottom-2 opacity-20 group-hover:opacity-40 transition-opacity">
                                    {tick.direction === "UP" ? <ArrowUpRight className="w-8 h-8 text-green-500" /> : <ArrowDownRight className="w-8 h-8 text-red-500" />}
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
