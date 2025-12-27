"use client";

import { useCryptoStore } from "@/stores/cryptoStore";
import { TRACKED_SYMBOLS } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";

const SYMBOL_NAMES: Record<string, string> = {
    BTCUSDT: "Bitcoin",
    ETHUSDT: "Ethereum",
    SOLUSDT: "Solana",
};

const SYMBOL_ICONS: Record<string, string> = {
    BTCUSDT: "₿",
    ETHUSDT: "Ξ",
    SOLUSDT: "◎",
};

/**
 * Market overview showing all tracked assets.
 */
export function MarketOverview() {
    const { trades, selectedSymbol, setSelectedSymbol } = useCryptoStore();

    return (
        <div className="space-y-2">
            {/* Header */}
            <div className="grid grid-cols-3 text-xs text-slate-500 px-2">
                <span>Name</span>
                <span className="text-right">Price</span>
                <span className="text-right">Change</span>
            </div>

            {/* Assets */}
            {TRACKED_SYMBOLS.map((symbol) => {
                const trade = trades[symbol];
                const isSelected = selectedSymbol === symbol;
                // Mock change for demo (would come from backend in production)
                const change = trade ? ((trade.price % 10) - 5) / 2 : 0;

                return (
                    <button
                        key={symbol}
                        onClick={() => setSelectedSymbol(symbol)}
                        className={`
              w-full grid grid-cols-3 items-center p-2 rounded-lg 
              transition-colors text-left
              ${isSelected
                                ? "bg-emerald-500/20 ring-1 ring-emerald-500/50"
                                : "bg-slate-800/50 hover:bg-slate-800"
                            }
            `}
                    >
                        <div className="flex items-center gap-2">
                            <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-lg
                ${symbol === "BTCUSDT" ? "bg-amber-500/20 text-amber-400" :
                                    symbol === "ETHUSDT" ? "bg-purple-500/20 text-purple-400" :
                                        "bg-cyan-500/20 text-cyan-400"}
              `}>
                                {SYMBOL_ICONS[symbol]}
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white">
                                    {symbol.replace("USDT", "")}
                                </p>
                                <p className="text-xs text-slate-500">
                                    {SYMBOL_NAMES[symbol]}
                                </p>
                            </div>
                        </div>

                        <span className="text-sm text-right font-mono text-white">
                            {trade ? `$${trade.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : "—"}
                        </span>

                        <div className="flex justify-end">
                            <Badge variant={change >= 0 ? "default" : "destructive"} className="font-mono">
                                {change >= 0 ? "+" : ""}{change.toFixed(2)}%
                            </Badge>
                        </div>
                    </button>
                );
            })}
        </div>
    );
}
