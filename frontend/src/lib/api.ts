/**
 * API Client for backend communication
 * Provides typed methods for interacting with FastAPI backend
 */

import type { HealthResponse, Period, StatsResponse } from "@/types/api";

// Use different URLs for server-side (Docker) and client-side (browser)
// Server-side: use Docker service name 'api'
// Client-side: use localhost for browser
const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.API_URL || "http://api:8000" // Server-side (SSR in Docker)
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // Client-side (browser)

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(
        `API request failed: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

/**
 * Check API health status
 */
export async function checkApiHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>(`${API_BASE_URL}/health`);
}

/**
 * Get statistics for specified period
 * @param period - Statistics period ("day" or "week")
 */
export async function getStats(period: Period): Promise<StatsResponse> {
  return fetchJson<StatsResponse>(`${API_BASE_URL}/api/stats?period=${period}`);
}

export { ApiError };
