/**
 * Stats Cards Component
 * Displays 4 key metrics in card layout
 */

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatNumber } from "@/lib/formatters";
import type { StatsSummary } from "@/types/api";

interface StatsCardsProps {
  summary: StatsSummary;
}

export function StatsCards({ summary }: StatsCardsProps): JSX.Element {
  const stats = [
    {
      title: "Total Conversations",
      value: summary.total_conversations,
      description: "Total number of conversations",
    },
    {
      title: "Active Users",
      value: summary.active_users,
      description: "Number of active users",
    },
    {
      title: "Avg. Conversation Length",
      value: summary.average_conversation_length,
      description: "Average messages per conversation",
      decimals: 1,
    },
    {
      title: "Total Messages",
      value: summary.total_messages,
      description: "Total number of messages",
    },
  ];

  return (
    <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs sm:text-sm">{stat.title}</CardDescription>
            <CardTitle className="text-2xl font-bold sm:text-3xl md:text-4xl">
              {stat.decimals
                ? stat.value.toFixed(stat.decimals)
                : formatNumber(stat.value)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground sm:text-sm">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

