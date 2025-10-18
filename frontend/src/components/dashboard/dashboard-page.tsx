"use client";

/**
 * Dashboard Page Component
 * Main dashboard component with state management
 */

import { useEffect, useState } from "react";

import { ActivityChart } from "@/components/dashboard/activity-chart";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { getStats } from "@/lib/api";
import type { Period, StatsResponse } from "@/types/api";

interface DashboardPageProps {
  initialStats: StatsResponse;
}

export function DashboardPage({ initialStats }: DashboardPageProps): JSX.Element {
  const [period, setPeriod] = useState<Period>(initialStats.period);
  const [stats, setStats] = useState<StatsResponse>(initialStats);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    // Skip loading on initial mount since we have initialStats
    if (isInitialLoad) {
      setIsInitialLoad(false);
      return;
    }

    // Load new data when period changes
    const loadStats = async (): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        const newStats = await getStats(period);
        setStats(newStats);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load stats");
        console.error("Failed to load stats:", err);
      } finally {
        setIsLoading(false);
      }
    };

    void loadStats();
  }, [period, isInitialLoad]);

  const handlePeriodChange = (newPeriod: Period): void => {
    setPeriod(newPeriod);
  };

  if (error) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
          <p className="text-lg font-semibold text-destructive">
            Error loading dashboard
          </p>
          <p className="mt-2 text-sm text-muted-foreground">{error}</p>
          <button
            onClick={() => setPeriod(period)}
            className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <StatsCards summary={stats.summary} />
      <ActivityChart
        activityData={stats.activity_chart}
        period={period}
        onPeriodChange={handlePeriodChange}
        isLoading={isLoading}
      />
    </div>
  );
}

