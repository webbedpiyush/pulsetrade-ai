/**
 * Backend API service
 */
import { API_URL } from "@/lib/constants";

/**
 * Trigger a demo alert (for hackathon presentation)
 */
export async function triggerDemoAlert(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/debug/trigger`, {
        method: "POST",
    });
    return response.json();
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
}
