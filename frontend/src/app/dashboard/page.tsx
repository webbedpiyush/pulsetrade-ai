"use client";

import { LiveChart } from "@/components/LiveChart";
import { AIPulse } from "@/components/AIPulse";
import { MarketOverview } from "@/components/MarketOverview";
import { KafkaLogs } from "@/components/KafkaLogs";
import { WebSocketProvider, useWebSocket } from "@/providers/WebSocketProvider";
import { triggerDemoAlert } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function DashboardContent() {
    const { isConnected } = useWebSocket();

    const handleForceAlert = async () => {
        try {
            await triggerDemoAlert();
        } catch (error) {
            console.error("Failed to trigger alert:", error);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 p-4 text-slate-100">
            {/* Header */}
            <header className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                        ✦ PulseTrade AI: Crypto Edition
                    </h1>
                    <Badge variant={isConnected ? "default" : "secondary"}>
                        {isConnected ? "● LIVE" : "○ Connecting..."}
                    </Badge>
                </div>
                <div className="flex gap-2">
                    <Button
                        onClick={handleForceAlert}
                        variant="destructive"
                        size="sm"
                        className="font-bold"
                    >
                        🚨 FORCE ALERT
                    </Button>
                </div>
            </header>

            {/* Main Grid Layout - Bento Style */}
            <div className="grid h-[calc(100vh-100px)] grid-cols-12 grid-rows-6 gap-4">

                {/* 1. Real Time Chart (Top Left - Large) */}
                <div className="col-span-8 row-span-4 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
                    <div className="flex items-center justify-between mb-2">
                        <h2 className="text-sm font-semibold text-slate-400">Real Time Chart</h2>
                        <span className="text-xs text-emerald-400">● LIVE</span>
                    </div>
                    <div className="h-[calc(100%-24px)]">
                        <LiveChart />
                    </div>
                </div>

                {/* 2. AI Pulse (Top Right - Medium) */}
                <div className="col-span-4 row-span-2 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent pointer-events-none" />
                    <h2 className="text-sm font-semibold text-slate-400 mb-2 relative z-10">
                        AI Pulse (Gemini + ElevenLabs)
                    </h2>
                    <AIPulse />
                </div>

                {/* 3. Market Overview (Middle Right - Medium) */}
                <div className="col-span-4 row-span-2 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
                    <h2 className="text-sm font-semibold text-slate-400 mb-2">Market Overview</h2>
                    <MarketOverview />
                </div>

                {/* 4. Live Trade Stream / Kafka Logs (Bottom - Wide) */}
                <div className="col-span-12 row-span-2 rounded-xl border border-slate-800 bg-slate-950 shadow-inner overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
                        <h2 className="text-sm font-semibold text-slate-400">Live Trade Stream (Kafka)</h2>
                        <span className="text-xs text-cyan-400 font-mono">topic: crypto-trades</span>
                    </div>
                    <div className="h-[calc(100%-40px)]">
                        <KafkaLogs />
                    </div>
                </div>

            </div>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <WebSocketProvider>
            <DashboardContent />
        </WebSocketProvider>
    );
}
