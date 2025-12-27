"use client";

/**
 * PulseTrade AI - Main Dashboard
 * Redesigned with ShadCN-inspired finance dashboard layout.
 */
import { useState, useEffect } from "react";
import { useMarketWebSocket } from "@/hooks/useMarketWebSocket";
import { useMarketStore } from "@/stores/marketStore";
import { Sidebar } from "@/components/Sidebar";
import { StatCard } from "@/components/StatCard";
import { PriceChart } from "@/components/PriceChart";
import { TickerGrid } from "@/components/TickerGrid";
import { AlertFeed } from "@/components/AlertFeed";
import { AudioStreamPlayer } from "@/components/AudioStreamPlayer";
import { PortfolioManager } from "@/components/PortfolioManager";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    Bell,
    Search,
    Briefcase,
    Activity,
    Wifi,
    WifiOff,
    TrendingUp,
    BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Dashboard() {
    // Initialize WebSocket connection
    useMarketWebSocket();

    const { connected, ticks } = useMarketStore();
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [portfolioCount, setPortfolioCount] = useState(0);

    // Get active stock count
    const activeStocks = Object.keys(ticks).length;

    // Fetch portfolio count
    useEffect(() => {
        async function fetchPortfolios() {
            try {
                const res = await fetch("/api/portfolios");
                if (res.ok) {
                    const data = await res.json();
                    setPortfolioCount(data.length || 0);
                }
            } catch {
                // Silent fail
            }
        }
        fetchPortfolios();
    }, []);

    return (
        <div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-brand-500/30 flex">
            {/* Sidebar */}
            <Sidebar
                collapsed={sidebarCollapsed}
                onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="h-16 border-b border-white/5 bg-slate-950/50 backdrop-blur-md flex items-center justify-between px-6">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <Input
                                type="text"
                                placeholder="Search stocks, portfolios..."
                                className="w-72 pl-10 bg-slate-900/50 border-white/5 text-sm placeholder:text-slate-500 focus:border-brand-500/50 focus:ring-brand-500/20"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Status Indicator */}
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-white/5">
                            {connected ? (
                                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                                <WifiOff className="w-3.5 h-3.5 text-red-400" />
                            )}
                            <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400">
                                {connected ? "Live" : "Offline"}
                            </span>
                            <div
                                className={cn(
                                    "w-2 h-2 rounded-full shadow-[0_0_8px_1px]",
                                    connected
                                        ? "bg-emerald-500 shadow-emerald-500/50 animate-pulse"
                                        : "bg-red-500 shadow-red-500/50"
                                )}
                            />
                        </div>

                        <div className="h-4 w-px bg-white/10" />

                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-9 w-9 text-slate-400 hover:text-white relative"
                        >
                            <Bell className="w-4 h-4" />
                            <span className="absolute top-2 right-2 w-2 h-2 bg-brand-500 rounded-full border-2 border-slate-950" />
                        </Button>
                    </div>
                </header>

                {/* Dashboard Content */}
                <main className="flex-1 overflow-auto p-6">
                    {/* Stat Cards Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <StatCard
                            title="Portfolios"
                            value={portfolioCount}
                            icon={Briefcase}
                            variant="brand"
                            subtitle="Active watchlists"
                            delay={0}
                        />
                        <StatCard
                            title="Stocks Tracked"
                            value={activeStocks}
                            icon={BarChart3}
                            variant="success"
                            subtitle="Real-time monitoring"
                            delay={0.1}
                        />
                        <StatCard
                            title="System Status"
                            value={connected ? "Online" : "Offline"}
                            icon={Activity}
                            variant={connected ? "success" : "warning"}
                            subtitle={connected ? "WebSocket connected" : "Reconnecting..."}
                            delay={0.2}
                        />
                    </div>

                    {/* Main Dashboard Grid */}
                    <div className="grid grid-cols-12 gap-6 min-h-[calc(100vh-280px)]">
                        {/* Left Column - Portfolios */}
                        <div className="col-span-12 xl:col-span-3 space-y-6">
                            <PortfolioManager />
                        </div>

                        {/* Center Column - Chart + Tickers */}
                        <div className="col-span-12 xl:col-span-6 space-y-6">
                            <PriceChart />
                            <TickerGrid />
                        </div>

                        {/* Right Column - Alert Feed */}
                        <div className="col-span-12 xl:col-span-3">
                            <AlertFeed />
                        </div>
                    </div>
                </main>
            </div>

            {/* Audio Service */}
            <AudioStreamPlayer />
        </div>
    );
}
