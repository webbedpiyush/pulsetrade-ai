"use client";

/**
 * Real-time stock ticker display with market separation.
 * Groups stocks by market (India/US/UK) with visual tabs.
 */
import { useState } from "react";
import { useMarketStore } from "@/stores/marketStore";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ArrowUpRight, ArrowDownRight, Activity, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

// Market configuration
const MARKETS = {
    all: { label: "All", prefix: "", flag: "🌍", currency: "" },
    india: { label: "India", prefix: "NSE:", flag: "🇮🇳", currency: "₹" },
    us: { label: "US", prefix: "NYSE:", flag: "🇺🇸", currency: "$" },
    uk: { label: "UK", prefix: "LSE:", flag: "🇬🇧", currency: "£" },
} as const;

type MarketKey = keyof typeof MARKETS;

function formatPrice(price: number, market: MarketKey): string {
    const currency = MARKETS[market]?.currency || "";
    if (market === "india") {
        return `${currency}${price.toLocaleString("en-IN", { minimumFractionDigits: 1 })}`;
    } else if (market === "uk") {
        // UK prices from LSE might be in pence, display as is
        return `${currency}${price.toLocaleString("en-GB", { minimumFractionDigits: 2 })}`;
    } else if (market === "us") {
        return `${currency}${price.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
    }
    return `${price.toFixed(2)}`;
}

function getMarketFromSymbol(symbol: string): MarketKey {
    if (symbol.startsWith("NSE:") || symbol.startsWith("BSE:")) return "india";
    if (symbol.startsWith("NYSE:") || symbol.startsWith("NASDAQ:")) return "us";
    if (symbol.startsWith("LSE:")) return "uk";
    return "all";
}

export function TickerGrid() {
    const { ticks, selectedSymbol, setSelectedSymbol } = useMarketStore();
    const [activeMarket, setActiveMarket] = useState<MarketKey>("all");

    const tickList = Object.values(ticks);

    // Filter ticks by selected market
    const filteredTicks = activeMarket === "all"
        ? tickList
        : tickList.filter(t => t.symbol.startsWith(MARKETS[activeMarket].prefix));

    // Count by market
    const counts = {
        all: tickList.length,
        india: tickList.filter(t => t.symbol.startsWith("NSE:") || t.symbol.startsWith("BSE:")).length,
        us: tickList.filter(t => t.symbol.startsWith("NYSE:") || t.symbol.startsWith("NASDAQ:")).length,
        uk: tickList.filter(t => t.symbol.startsWith("LSE:")).length,
    };

    if (tickList.length === 0) {
        return (
            <Card className="bg-slate-950/50 border-white/5 shadow-inner">
                <CardHeader>
                    <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                        <Activity className="w-5 h-5 text-brand-400" /> Live Tickers
                    </CardTitle>
                </CardHeader>
                <CardContent>
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
            <CardHeader className="py-3 border-b border-white/5">
                <CardTitle className="text-lg font-medium text-white flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <Globe className="w-5 h-5 text-brand-400" /> Market Feed
                    </span>
                    <span className="text-xs text-slate-500 font-normal">{tickList.length} Active</span>
                </CardTitle>
            </CardHeader>

            {/* Market Tabs */}
            <Tabs value={activeMarket} onValueChange={(v) => setActiveMarket(v as MarketKey)} className="flex-1 flex flex-col">
                <div className="px-4 pt-3 pb-2 border-b border-white/5">
                    <TabsList className="bg-slate-900/50 p-1 h-auto gap-1">
                        {(Object.keys(MARKETS) as MarketKey[]).map((key) => (
                            <TabsTrigger
                                key={key}
                                value={key}
                                className={cn(
                                    "text-xs px-3 py-1.5 data-[state=active]:bg-brand-500/20 data-[state=active]:text-brand-300",
                                    "transition-all"
                                )}
                            >
                                <span className="mr-1">{MARKETS[key].flag}</span>
                                {MARKETS[key].label}
                                <span className="ml-1.5 text-slate-500 text-[10px]">({counts[key]})</span>
                            </TabsTrigger>
                        ))}
                    </TabsList>
                </div>

                <CardContent className="p-0 flex-1 overflow-hidden">
                    <ScrollArea className="h-[400px] w-full p-4">
                        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 gap-3">
                            {filteredTicks.map((tick) => {
                                const market = getMarketFromSymbol(tick.symbol);
                                const displaySymbol = tick.symbol.split(":")[1] || tick.symbol;

                                return (
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
                                        {/* Market badge */}
                                        <div className="absolute top-1 right-1 text-[10px] opacity-50">
                                            {MARKETS[market]?.flag}
                                        </div>

                                        <div className="flex justify-between items-start mb-1">
                                            <span className="text-xs font-semibold text-slate-300 group-hover:text-white truncate max-w-[90px]">
                                                {displaySymbol}
                                            </span>
                                            {tick.breakout && (
                                                <span className={cn(
                                                    "flex h-2 w-2 rounded-full",
                                                    tick.direction === "UP" ? "bg-green-500 shadow-green-500/50" : "bg-red-500 shadow-red-500/50"
                                                )} />
                                            )}
                                        </div>

                                        <div className="flex items-baseline gap-1">
                                            <span className={cn(
                                                "text-sm font-mono font-bold",
                                                tick.direction === "UP" ? "text-green-400" : "text-slate-200"
                                            )}>
                                                {formatPrice(tick.price, market)}
                                            </span>
                                        </div>

                                        <div className="absolute right-2 bottom-2 opacity-20 group-hover:opacity-40 transition-opacity">
                                            {tick.direction === "UP"
                                                ? <ArrowUpRight className="w-8 h-8 text-green-500" />
                                                : <ArrowDownRight className="w-8 h-8 text-red-500" />
                                            }
                                        </div>
                                    </motion.button>
                                );
                            })}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Tabs>
        </Card>
    );
}
