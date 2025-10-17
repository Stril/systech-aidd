/**
 * API Types - TypeScript interfaces matching backend Pydantic models
 * Based on api/models.py
 */

export type Period = "day" | "week";

export interface StatsSummary {
  total_conversations: number;
  active_users: number;
  average_conversation_length: number;
  total_messages: number;
}

export interface ActivityPoint {
  date: string;
  hour: number | null;
  message_count: number;
  conversation_count: number;
}

export interface RecentConversationItem {
  id: number;
  user_id: number;
  username: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface TopUserItem {
  user_id: number;
  username: string | null;
  first_name: string | null;
  conversation_count: number;
  message_count: number;
}

export interface StatsResponse {
  period: Period;
  summary: StatsSummary;
  activity_chart: ActivityPoint[];
  recent_conversations: RecentConversationItem[];
  top_users: TopUserItem[];
}

export interface HealthResponse {
  status: string;
}
