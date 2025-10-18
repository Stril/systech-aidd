/**
 * User storage utilities for managing usernames in localStorage
 */

import type { ChatMode } from "@/types/chat";

/**
 * Generate unique username like "User_12345"
 * Uses random 5-digit number
 */
export function generateUsername(): string {
  const randomNumber = Math.floor(10000 + Math.random() * 90000);
  return `User_${randomNumber}`;
}

/**
 * Get username for specific mode from localStorage
 * Keys: "chat_username_normal", "chat_username_admin"
 */
export function getUsernameForMode(mode: ChatMode): string | null {
  const key = `chat_username_${mode}`;
  return localStorage.getItem(key);
}

/**
 * Save username for specific mode to localStorage
 */
export function setUsernameForMode(mode: ChatMode, username: string): void {
  const key = `chat_username_${mode}`;
  localStorage.setItem(key, username);
}

/**
 * Clear all usernames from localStorage
 */
export function clearUsernames(): void {
  localStorage.removeItem("chat_username_normal");
  localStorage.removeItem("chat_username_admin");
}

/**
 * Validate username format (User_NNNNN)
 */
export function validateUsername(username: string): boolean {
  const pattern = /^User_\d{5}$/;
  return pattern.test(username);
}

