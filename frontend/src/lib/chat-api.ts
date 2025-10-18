/**
 * Chat API Client
 * Provides typed methods for interacting with chat endpoints
 */

import type { ChatMode, ChatResponse, ChatSessionInfo } from "@/types/chat";

import { ApiError } from "./api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Create a new chat session
 * @param mode - Chat mode ("normal" or "admin")
 * @param username - Username in format "User_12345"
 */
export async function createChatSession(
  mode: ChatMode,
  username: string
): Promise<ChatSessionInfo> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ mode, username }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `Failed to create session: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    return (await response.json()) as ChatSessionInfo;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

/**
 * Send a message in chat session
 * @param sessionId - Session identifier
 * @param message - User message
 * @param mode - Chat mode
 */
export async function sendMessage(
  sessionId: string,
  message: string,
  mode: ChatMode
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        mode,
      }),
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to send message: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    return (await response.json()) as ChatResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

/**
 * Delete a chat session
 * @param sessionId - Session identifier
 */
export async function deleteChatSession(sessionId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/session/${sessionId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to delete session: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

