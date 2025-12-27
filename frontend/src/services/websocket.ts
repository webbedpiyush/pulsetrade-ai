/**
 * WebSocket service wrapper for crypto stream
 */
import type { TradeEvent, AlertEvent, AnalysisEvent, WSMessage } from "@/types";

export type MessageHandler = {
    onTrade?: (trade: TradeEvent) => void;
    onAlert?: (alert: AlertEvent) => void;
    onAnalysis?: (analysis: AnalysisEvent) => void;
    onAudio?: (audio: Blob) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
};

export class CryptoWebSocket {
    private ws: WebSocket | null = null;
    private url: string;
    private handlers: MessageHandler;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 1000;

    constructor(url: string, handlers: MessageHandler) {
        this.url = url;
        this.handlers = handlers;
    }

    connect(): void {
        if (this.ws?.readyState === WebSocket.OPEN) return;

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log("[WS] Connected to", this.url);
            this.reconnectAttempts = 0;
            this.handlers.onConnect?.();
        };

        this.ws.onmessage = async (event) => {
            // Binary data = audio
            if (event.data instanceof Blob) {
                this.handlers.onAudio?.(event.data);
                return;
            }

            // JSON data
            try {
                const message: WSMessage = JSON.parse(event.data);

                switch (message.type) {
                    case "trade":
                        this.handlers.onTrade?.(message.data as TradeEvent);
                        break;
                    case "alert":
                        this.handlers.onAlert?.(message.data as AlertEvent);
                        break;
                    case "analysis":
                        this.handlers.onAnalysis?.(message.data as AnalysisEvent);
                        break;
                }
            } catch (error) {
                console.error("[WS] Parse error:", error);
            }
        };

        this.ws.onclose = () => {
            console.log("[WS] Disconnected");
            this.handlers.onDisconnect?.();
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error("[WS] Error:", error);
        };
    }

    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error("[WS] Max reconnect attempts reached");
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
    }

    disconnect(): void {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    get isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}
