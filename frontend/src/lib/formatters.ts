/**
 * Formatting utilities for dashboard
 */

import { format } from "date-fns";

/**
 * Format number with thousand separators
 * @example formatNumber(1234) => "1,234"
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

/**
 * Format date string to readable format
 * @example formatDate("2025-10-17") => "17 Oct 2025"
 */
export function formatDate(date: string): string {
  return format(new Date(date), "dd MMM yyyy");
}

/**
 * Format datetime string to readable format
 * @example formatDateTime("2025-10-17T10:15:00") => "17 Oct 2025, 10:15"
 */
export function formatDateTime(date: string): string {
  return format(new Date(date), "dd MMM yyyy, HH:mm");
}

/**
 * Format number as percentage
 * @example formatPercentage(12.5) => "12.5%"
 */
export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * Get initials from name
 * @example getInitials("Alice Wonder") => "AW"
 * @example getInitials("Bob") => "B"
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((word) => word[0])
    .filter(Boolean)
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Format hour for chart axis (0-23)
 * @example formatHour(0) => "00:00"
 * @example formatHour(13) => "13:00"
 */
export function formatHour(hour: number): string {
  return `${hour.toString().padStart(2, "0")}:00`;
}

/**
 * Format short date for chart axis
 * @example formatShortDate("2025-10-17") => "Oct 17"
 */
export function formatShortDate(date: string): string {
  return format(new Date(date), "MMM dd");
}

