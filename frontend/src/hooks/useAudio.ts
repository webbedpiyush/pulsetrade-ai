"use client";

import { useRef, useCallback } from "react";

/**
 * Hook for audio playback management
 */
export function useAudio() {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const urlRef = useRef<string | null>(null);

    const playAudio = useCallback(async (blob: Blob) => {
        // Clean up previous URL
        if (urlRef.current) {
            URL.revokeObjectURL(urlRef.current);
        }

        // Create new audio
        urlRef.current = URL.createObjectURL(blob);
        audioRef.current = new Audio(urlRef.current);

        try {
            await audioRef.current.play();
        } catch (error) {
            console.error("[Audio] Playback failed:", error);
        }
    }, []);

    const stopAudio = useCallback(() => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
        if (urlRef.current) {
            URL.revokeObjectURL(urlRef.current);
            urlRef.current = null;
        }
    }, []);

    return { playAudio, stopAudio };
}
