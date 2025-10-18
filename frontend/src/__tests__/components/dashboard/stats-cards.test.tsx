import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatsCards } from "@/components/dashboard/stats-cards";
import type { StatsSummary } from "@/types/api";

describe("StatsCards", () => {
  const mockSummary: StatsSummary = {
    total_conversations: 312,
    active_users: 95,
    average_conversation_length: 14.8,
    total_messages: 4618,
  };

  it("should render all 4 stat cards", () => {
    render(<StatsCards summary={mockSummary} />);

    expect(screen.getByText("Total Conversations")).toBeInTheDocument();
    expect(screen.getByText("Active Users")).toBeInTheDocument();
    expect(screen.getByText("Avg. Conversation Length")).toBeInTheDocument();
    expect(screen.getByText("Total Messages")).toBeInTheDocument();
  });

  it("should display formatted numbers for integer values", () => {
    render(<StatsCards summary={mockSummary} />);

    expect(screen.getByText("312")).toBeInTheDocument(); // total_conversations
    expect(screen.getByText("95")).toBeInTheDocument(); // active_users
    expect(screen.getByText("4,618")).toBeInTheDocument(); // total_messages (formatted with comma)
  });

  it("should display decimal for average conversation length", () => {
    render(<StatsCards summary={mockSummary} />);

    expect(screen.getByText("14.8")).toBeInTheDocument();
  });

  it("should display descriptions for each stat", () => {
    render(<StatsCards summary={mockSummary} />);

    expect(screen.getByText("Total number of conversations")).toBeInTheDocument();
    expect(screen.getByText("Number of active users")).toBeInTheDocument();
    expect(screen.getByText("Average messages per conversation")).toBeInTheDocument();
    expect(screen.getByText("Total number of messages")).toBeInTheDocument();
  });

  it("should handle zero values", () => {
    const zeroSummary: StatsSummary = {
      total_conversations: 0,
      active_users: 0,
      average_conversation_length: 0,
      total_messages: 0,
    };

    render(<StatsCards summary={zeroSummary} />);

    const zeroElements = screen.getAllByText("0");
    expect(zeroElements.length).toBeGreaterThan(0);
  });

  it("should handle large numbers", () => {
    const largeSummary: StatsSummary = {
      total_conversations: 1234567,
      active_users: 999999,
      average_conversation_length: 123.456,
      total_messages: 9876543,
    };

    render(<StatsCards summary={largeSummary} />);

    expect(screen.getByText("1,234,567")).toBeInTheDocument();
    expect(screen.getByText("999,999")).toBeInTheDocument();
    expect(screen.getByText("123.5")).toBeInTheDocument(); // rounded to 1 decimal
    expect(screen.getByText("9,876,543")).toBeInTheDocument();
  });
});

