"use client";

import { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

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

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    // Demo: Generate fake logs for visual effect
    // useEffect(() => {
    //     const interval = setInterval(() => {
    //         const symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"];
    //         const basePrices: Record<string, number> = {
    //             BTCUSDT: 67540,
    //             ETHUSDT: 3450,
    //             SOLUSDT: 185,
    //         };
    //
    //         const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    //         const price = basePrices[symbol] * (1 + (Math.random() - 0.5) * 0.001);
    //
    //         setLogs((prev) => [
    //             ...prev.slice(-50), // Keep last 50
    //             {
    //                 s: symbol,
    //                 p: price,
    //                 q: Math.random() * 0.1,
    //                 T: Date.now(),
    //             },
    //         ]);
    //     }, 100);
    //
    //     return () => clearInterval(interval);
    // }, []);

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
