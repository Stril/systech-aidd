import { describe, expect, it } from "vitest";

import {
  formatDate,
  formatDateTime,
  formatHour,
  formatNumber,
  formatPercentage,
  formatShortDate,
  getInitials,
} from "@/lib/formatters";

describe("formatters", () => {
  describe("formatNumber", () => {
    it("should format number with thousand separators", () => {
      expect(formatNumber(1234)).toBe("1,234");
      expect(formatNumber(1234567)).toBe("1,234,567");
      expect(formatNumber(0)).toBe("0");
      expect(formatNumber(999)).toBe("999");
    });
  });

  describe("formatDate", () => {
    it("should format date string to readable format", () => {
      expect(formatDate("2025-10-17")).toBe("17 Oct 2025");
      expect(formatDate("2025-01-01")).toBe("01 Jan 2025");
      expect(formatDate("2025-12-31")).toBe("31 Dec 2025");
    });
  });

  describe("formatDateTime", () => {
    it("should format datetime string to readable format", () => {
      expect(formatDateTime("2025-10-17T10:15:00")).toBe("17 Oct 2025, 10:15");
      expect(formatDateTime("2025-01-01T00:00:00")).toBe("01 Jan 2025, 00:00");
      expect(formatDateTime("2025-12-31T23:59:00")).toBe("31 Dec 2025, 23:59");
    });
  });

  describe("formatPercentage", () => {
    it("should format number as percentage", () => {
      expect(formatPercentage(12.5)).toBe("12.5%");
      expect(formatPercentage(0)).toBe("0.0%");
      expect(formatPercentage(100)).toBe("100.0%");
      expect(formatPercentage(99.99)).toBe("100.0%");
    });
  });

  describe("getInitials", () => {
    it("should get initials from name", () => {
      expect(getInitials("Alice Wonder")).toBe("AW");
      expect(getInitials("Bob")).toBe("B");
      expect(getInitials("John David Smith")).toBe("JD");
      expect(getInitials("")).toBe("");
    });

    it("should return uppercase initials", () => {
      expect(getInitials("alice wonder")).toBe("AW");
      expect(getInitials("bob smith")).toBe("BS");
    });
  });

  describe("formatHour", () => {
    it("should format hour for chart axis", () => {
      expect(formatHour(0)).toBe("00:00");
      expect(formatHour(9)).toBe("09:00");
      expect(formatHour(13)).toBe("13:00");
      expect(formatHour(23)).toBe("23:00");
    });
  });

  describe("formatShortDate", () => {
    it("should format short date for chart axis", () => {
      expect(formatShortDate("2025-10-17")).toBe("Oct 17");
      expect(formatShortDate("2025-01-01")).toBe("Jan 01");
      expect(formatShortDate("2025-12-31")).toBe("Dec 31");
    });
  });
});

