"use client";

/**
 * PulseTrade AI - Main Dashboard
 * Redesigned with shadcn/ui and modern layout.
 */
import { UserButton, SignedIn } from "@clerk/nextjs";
import { useMarketWebSocket } from "@/hooks/useMarketWebSocket";
import { useMarketStore } from "@/stores/marketStore";
import { PriceChart } from "@/components/PriceChart";
import { TickerGrid } from "@/components/TickerGrid";
import { AlertFeed } from "@/components/AlertFeed";
import { AudioStreamPlayer } from "@/components/AudioStreamPlayer";
import { PortfolioManager } from "@/components/PortfolioManager";
import { Button } from "@/components/ui/button";
import { Bell, Search, Settings } from "lucide-react";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
    // Initialize WebSocket connection
    useMarketWebSocket();

    const { connected } = useMarketStore();

    return (
        <div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-brand-500/30">
            {/* Minimal Header */}
            <header className="h-16 border-b border-white/5 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-[1600px] mx-auto px-4 h-full flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center font-serif font-bold text-lg text-white shadow-lg shadow-brand-500/20 group-hover:shadow-brand-500/40 transition-all">P</div>
                            <span className="font-serif font-bold text-lg tracking-tight text-white hidden md:block">PulseTrade AI</span>
                        </Link>

                        <nav className="hidden md:flex items-center gap-1">
                            <Button variant="ghost" className="text-slate-400 hover:text-white hover:bg-white/5 h-8 text-sm">Overview</Button>
                            <Button variant="ghost" className="text-white bg-white/5 h-8 text-sm">Markets</Button>
                            <Button variant="ghost" className="text-slate-400 hover:text-white hover:bg-white/5 h-8 text-sm">Screener</Button>
                        </nav>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Status Indicator */}
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-white/5">
                            <div className={`w-2 h-2 rounded-full shadow-[0_0_8px_1px] ${connected ? "bg-emerald-500 shadow-emerald-500/50" : "bg-red-500 shadow-red-500/50"}`} />
                            <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400">
                                {connected ? "System Online" : "Disconnected"}
                            </span>
                        </div>

                        <div className="h-4 w-px bg-white/10 hidden sm:block" />

                        <div className="flex items-center gap-2">
                            <Button variant="ghost" size="icon" className="h-9 w-9 text-slate-400 hover:text-white relative">
                                <Bell className="w-4 h-4" />
                                <span className="absolute top-2 right-2 w-2 h-2 bg-brand-500 rounded-full border-2 border-slate-900" />
                            </Button>
                            <UserButton
                                appearance={{
                                    elements: {
                                        avatarBox: "w-8 h-8 ring-2 ring-white/10 hover:ring-brand-500/50 transition-all"
                                    }
                                }}
                            />
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content Dashboard Grid */}
            <main className="max-w-[1600px] mx-auto px-4 py-8">
                <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)] min-h-[800px]">

                    {/* Left Column (Lists & Controls) - 3 cols */}
                    <div className="col-span-12 lg:col-span-3 flex flex-col gap-6 h-full overflow-hidden">
                        <PortfolioManager />
                        <TickerGrid />
                    </div>

                    {/* Middle Column (Chart) - 6 cols */}
                    <div className="col-span-12 lg:col-span-6 h-full min-h-[400px]">
                        <PriceChart />
                    </div>

                    {/* Right Column (Alerts) - 3 cols */}
                    <div className="col-span-12 lg:col-span-3 h-full overflow-hidden">
                        <AlertFeed />
                    </div>
                </div>
            </main>

            {/* Audio Service */}
            <AudioStreamPlayer />
        </div>
    );
}
