/**
 * Chat API Types - TypeScript interfaces for chat functionality
 */

export type ChatMode = "normal" | "admin";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sqlQuery?: string;
}

export interface ChatSessionInfo {
  session_id: string;
  mode: ChatMode;
}

export interface ChatResponse {
  content: string;
  sql_query?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  mode: ChatMode;
}

export interface ChatSessionCreate {
  mode: ChatMode;
}

