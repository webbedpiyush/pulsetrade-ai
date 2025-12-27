"use client";

import { useCryptoStore } from "@/stores/cryptoStore";

/**
 * AI Pulse visualization with glowing circle and transcript.
 */
export function AIPulse() {
    const { isSpeaking, latestAnalysis } = useCryptoStore();

    return (
        <div className="flex flex-col h-full relative z-10">
            {/* Glowing Pulse Circle */}
            <div className="flex-1 flex items-center justify-center">
                <div
                    className={`
            w-20 h-20 rounded-full transition-all duration-500
            ${isSpeaking
                            ? "bg-emerald-500 shadow-[0_0_60px_20px_rgba(16,185,129,0.6)] animate-pulse scale-110"
                            : "bg-emerald-500/30 shadow-[0_0_20px_5px_rgba(16,185,129,0.2)]"
                        }
          `}
                />
            </div>

            {/* Transcript Box */}
            <div className="mt-4 p-3 rounded-lg bg-slate-800/50 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Latest voice transcript:</p>
                <p className="text-sm text-white line-clamp-3">
                    {latestAnalysis?.text || "Waiting for market signals..."}
                </p>
            </div>
        </div>
    );
}
