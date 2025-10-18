/**
 * Dashboard Page Route
 * Server Component that loads initial data and renders dashboard
 */

import { DashboardLayout } from "@/components/dashboard/dashboard-layout";
import { DashboardPage } from "@/components/dashboard/dashboard-page";
import { getStats } from "@/lib/api";

// Force dynamic rendering (SSR) instead of static generation
export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Dashboard(): Promise<JSX.Element> {
  try {
    // Load initial stats for "day" period
    const initialStats = await getStats("day");

    return (
      <DashboardLayout>
        <DashboardPage initialStats={initialStats} />
      </DashboardLayout>
    );
  } catch (error) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
            <p className="text-lg font-semibold text-destructive">
              Failed to load dashboard
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {error instanceof Error ? error.message : "Unknown error"}
            </p>
            <p className="mt-4 text-xs text-muted-foreground">
              Make sure the API server is running at{" "}
              {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }
}

