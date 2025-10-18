import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ThemeToggle } from "@/components/theme-toggle";

// Mock next-themes
vi.mock("next-themes", () => ({
  useTheme: () => ({
    theme: "dark",
    setTheme: vi.fn(),
  }),
}));

describe("ThemeToggle", () => {
  it("should render toggle button", async () => {
    render(<ThemeToggle />);

    await waitFor(() => {
      const button = screen.getByRole("button", { name: /toggle theme/i });
      expect(button).toBeInTheDocument();
    });
  });

  it("should show sun icon for dark theme", async () => {
    render(<ThemeToggle />);

    await waitFor(() => {
      const button = screen.getByRole("button", { name: /toggle theme/i });
      expect(button).toBeInTheDocument();
      // Sun icon should be visible for dark theme (to switch to light)
      const svg = button.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });
  });

  it("should be clickable", async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await waitFor(() => {
      const button = screen.getByRole("button", { name: /toggle theme/i });
      expect(button).toBeInTheDocument();
    });

    const button = screen.getByRole("button", { name: /toggle theme/i });
    await user.click(button);
    // Button should remain clickable
    expect(button).toBeEnabled();
  });
});

