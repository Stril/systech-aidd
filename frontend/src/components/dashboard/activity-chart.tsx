"use client";

/**
 * Activity Chart Component
 * Displays message and conversation activity over time
 * Supports Day (24 hours) and Week (7 days) periods
 */

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatHour, formatShortDate } from "@/lib/formatters";
import type { ActivityPoint, Period } from "@/types/api";

interface ActivityChartProps {
  activityData: ActivityPoint[];
  period: Period;
  onPeriodChange: (period: Period) => void;
  isLoading?: boolean;
}

export function ActivityChart({
  activityData,
  period,
  onPeriodChange,
  isLoading = false,
}: ActivityChartProps): JSX.Element {
  // Transform data for chart
  const chartData = activityData.map((point) => ({
    label:
      point.hour !== null
        ? formatHour(point.hour)
        : formatShortDate(point.date),
    messages: point.message_count,
    conversations: point.conversation_count,
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-lg sm:text-xl">Activity Chart</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              {period === "day"
                ? "Activity over the last 24 hours"
                : "Activity over the last 7 days"}
            </CardDescription>
          </div>
          <Tabs value={period} onValueChange={(v) => onPeriodChange(v as Period)}>
            <TabsList className="w-full sm:w-auto">
              <TabsTrigger value="day" disabled={isLoading} className="flex-1 text-xs sm:flex-initial sm:text-sm">
                Last 24 hours
              </TabsTrigger>
              <TabsTrigger value="week" disabled={isLoading} className="flex-1 text-xs sm:flex-initial sm:text-sm">
                Last 7 days
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex h-[250px] items-center justify-center sm:h-[350px] md:h-[400px]">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        ) : (
          <ChartContainer className="h-[250px] sm:h-[350px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(217.2 91.2% 59.8%)" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="hsl(217.2 91.2% 59.8%)" stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient id="colorConversations" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(142.1 76.2% 36.3%)" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="hsl(142.1 76.2% 36.3%)" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="label"
                  className="text-xs text-muted-foreground"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis
                  className="text-xs text-muted-foreground"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (!active || !payload) return null;
                    return (
                      <ChartTooltipContent
                        label={String(label ?? "")}
                        payload={payload.map((p) => ({
                          name: p.name === "messages" ? "Messages" : "Conversations",
                          value: String(p.value ?? 0),
                          color: String(p.color ?? ""),
                        }))}
                      />
                    );
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="messages"
                  name="messages"
                  stroke="hsl(217.2 91.2% 59.8%)"
                  fillOpacity={1}
                  fill="url(#colorMessages)"
                />
                <Area
                  type="monotone"
                  dataKey="conversations"
                  name="conversations"
                  stroke="hsl(142.1 76.2% 36.3%)"
                  fillOpacity={1}
                  fill="url(#colorConversations)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  );
}

