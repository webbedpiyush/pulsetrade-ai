"use client";

/**
 * Alert feed showing recent breakouts and AI analysis.
 * Updated with shadcn/ui Card and ScrollArea.
 */
import { useMarketStore } from "@/stores/marketStore";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Mic, Zap, TrendingUp, TrendingDown, Brain } from "lucide-react";
import { cn } from "@/lib/utils";

export function AlertFeed() {
    const { alerts, latestAnalysis, connected } = useMarketStore();

    return (
        <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 h-full flex flex-col">
            <CardHeader className="py-4 border-b border-white/5 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                    <Mic className="w-5 h-5 text-brand-400" /> Intelligence Feed
                </CardTitle>
                <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Gemini Live</span>
                    <div
                        className={cn("w-2 h-2 rounded-full shadow-[0_0_8px_1px]",
                            connected ? "bg-green-500 shadow-green-500/50 animate-pulse" : "bg-red-500 shadow-red-500/50"
                        )}
                    />
                </div>
            </CardHeader>

            <CardContent className="p-0 flex-1 relative overflow-hidden">
                <ScrollArea className="h-full max-h-[calc(100vh-200px)] p-4">
                    {/* Latest AI Analysis Highlight */}
                    <AnimatePresence>
                        {latestAnalysis && (
                            <motion.div
                                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                className="bg-gradient-to-br from-indigo-900/40 via-purple-900/20 to-slate-900/40 rounded-xl p-4 mb-6 border border-indigo-500/30 shadow-[0_0_20px_-5px_rgba(99,102,241,0.3)] relative overflow-hidden"
                            >
                                <div className="absolute top-0 right-0 p-2">
                                    <Brain className="w-12 h-12 text-indigo-500/10 rotate-12" />
                                </div>
                                <div className="flex items-center gap-2 mb-2">
                                    <Badge variant="secondary" className="bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 text-[10px] border-indigo-500/20">
                                        <Zap className="w-3 h-3 mr-1 fill-current" /> GEMINI ANALYSIS
                                    </Badge>
                                    <span className="text-xs font-mono text-indigo-400">{latestAnalysis.symbol}</span>
                                </div>
                                <p className="text-sm text-slate-200 leading-relaxed font-light">
                                    {latestAnalysis.text}
                                </p>
                                <div className="mt-3 flex items-center gap-2">
                                    <div className="h-0.5 w-full bg-indigo-500/20 rounded-full overflow-hidden">
                                        <div className="h-full w-1/3 bg-indigo-500 animate-loading-bar" />
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Alert Stream */}
                    <div className="space-y-3">
                        <div className="text-xs font-semibold text-slate-600 uppercase tracking-widest pl-1 mb-2">Recent Signals</div>
                        <AnimatePresence initial={false}>
                            {alerts.map((alert, idx) => (
                                <motion.div
                                    key={`${alert.symbol}-${alert.time}`}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    transition={{ duration: 0.3 }}
                                    className={cn(
                                        "p-3 rounded-lg border flex items-center justify-between group hover:shadow-lg transition-all",
                                        alert.direction === "UP"
                                            ? "bg-green-500/5 border-green-500/20 hover:border-green-500/40"
                                            : "bg-red-500/5 border-red-500/20 hover:border-red-500/40"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={cn(
                                            "w-8 h-8 rounded-lg flex items-center justify-center border",
                                            alert.direction === "UP" ? "bg-green-500/10 border-green-500/20 text-green-400" : "bg-red-500/10 border-red-500/20 text-red-400"
                                        )}>
                                            {alert.direction === "UP" ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-bold text-slate-200">
                                                    {alert.symbol.replace("NSE:", "")}
                                                </span>
                                                <span className="text-[10px] text-slate-500 font-mono">
                                                    {new Date(alert.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                </span>
                                            </div>
                                            <div className="text-xs text-slate-400 font-medium">
                                                Price: <span className="text-slate-200 text-mono">₹{alert.price.toFixed(2)}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <Badge variant="outline" className={cn("text-[10px]",
                                        alert.direction === "UP" ? "border-green-500/30 text-green-400" : "border-red-500/30 text-red-400"
                                    )}>
                                        {alert.direction}
                                    </Badge>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {alerts.length === 0 && !latestAnalysis && (
                            <div className="flex flex-col items-center justify-center py-12 text-slate-600">
                                <Mic className="w-8 h-8 mb-2 opacity-20" />
                                <p className="text-sm">Listening for market moves...</p>
                            </div>
                        )}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
