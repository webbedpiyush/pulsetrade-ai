"use client";

import { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useCryptoStore } from "@/stores/cryptoStore";

interface LogEntry {
    s: string;  // Symbol
    p: number;  // Price
    q: number;  // Quantity
    T: number;  // Timestamp
}

/**
 * Live Kafka log stream showing raw trade data.
 * Proof of streaming for Confluent judges.
 */
export function KafkaLogs() {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);
    const { latestTrade } = useCryptoStore();

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    // Subscribe to real trades
    useEffect(() => {
        if (latestTrade) {
            setLogs((prev) => [
                ...prev.slice(-49), // Keep last 50
                {
                    s: latestTrade.symbol,
                    p: latestTrade.price,
                    q: latestTrade.volume,
                    T: latestTrade.time,
                },
            ]);
        }
    }, [latestTrade]);

    return (
        <div
            ref={scrollRef}
            className="h-full overflow-y-auto font-mono text-xs p-4 space-y-0.5"
        >
            {logs.map((log, i) => (
                <div key={i} className="text-slate-400 whitespace-nowrap">
                    <span className="text-slate-600">{"{"}</span>
                    <span className="text-cyan-400">"s"</span>
                    <span className="text-slate-500">: </span>
                    <span className="text-emerald-400">"{log.s}"</span>
                    <span className="text-slate-500">, </span>
                    <span className="text-cyan-400">"p"</span>
                    <span className="text-slate-500">: </span>
                    <span className="text-amber-400">{log.p.toFixed(2)}</span>
                    <span className="text-slate-500">, </span>
                    <span className="text-cyan-400">"q"</span>
                    <span className="text-slate-500">: </span>
                    <span className="text-amber-400">{log.q.toFixed(6)}</span>
                    <span className="text-slate-500">, </span>
                    <span className="text-cyan-400">"T"</span>
                    <span className="text-slate-500">: </span>
                    <span className="text-purple-400">{log.T}</span>
                    <span className="text-slate-600">{"}"}</span>
                </div>
            ))}
            {logs.length === 0 && (
                <div className="text-slate-500 animate-pulse">
                    Connecting to Kafka stream...
                </div>
            )}
        </div>
    );
}
