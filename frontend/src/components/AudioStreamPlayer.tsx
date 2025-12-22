"use client";

/**
 * Audio player with MSE jitter buffer for voice alerts.
 */
import { useEffect, useRef, useCallback } from "react";
import { useMarketStore } from "@/stores/marketStore";

export function AudioStreamPlayer() {
    const audioRef = useRef<HTMLAudioElement>(null);
    const mediaSource = useRef<MediaSource | null>(null);
    const sourceBuffer = useRef<SourceBuffer | null>(null);
    const isProcessing = useRef(false);

    const { audioQueue, shiftAudioChunk } = useMarketStore();

    const processQueue = useCallback(() => {
        if (
            !sourceBuffer.current ||
            sourceBuffer.current.updating ||
            isProcessing.current
        ) {
            return;
        }

        const chunk = shiftAudioChunk();
        if (!chunk) return;

        isProcessing.current = true;

        try {
            // Cast to ArrayBuffer to fix TypeScript error
            sourceBuffer.current.appendBuffer(chunk.buffer as ArrayBuffer);
        } catch (e) {
            console.error("Audio buffer error:", e);
        } finally {
            isProcessing.current = false;
        }
    }, [shiftAudioChunk]);

    useEffect(() => {
        // Check for MSE support
        if (!("MediaSource" in window)) {
            console.warn("MediaSource not supported, falling back to basic audio");
            return;
        }

        mediaSource.current = new MediaSource();

        if (audioRef.current) {
            audioRef.current.src = URL.createObjectURL(mediaSource.current);

            mediaSource.current.addEventListener("sourceopen", () => {
                try {
                    // ElevenLabs sends MP3
                    sourceBuffer.current =
                        mediaSource.current!.addSourceBuffer("audio/mpeg");
                    sourceBuffer.current.addEventListener("updateend", processQueue);
                } catch (e) {
                    console.error("Failed to create source buffer:", e);
                }
            });
        }

        return () => {
            if (mediaSource.current?.readyState === "open") {
                try {
                    mediaSource.current.endOfStream();
                } catch (e) {
                    // Ignore
                }
            }
        };
    }, [processQueue]);

    // Process queue when new chunks arrive
    useEffect(() => {
        if (audioQueue.length > 0) {
            processQueue();
        }
    }, [audioQueue.length, processQueue]);

    return (
        <audio
            ref={audioRef}
            autoPlay
            className="hidden"
            onError={(e) => console.error("Audio error:", e)}
        />
    );
}
