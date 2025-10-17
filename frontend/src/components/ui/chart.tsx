"use client";

/**
 * Chart components for Recharts integration
 * Simplified version inspired by shadcn/ui chart
 */

import * as React from "react";

import { cn } from "@/lib/utils";

const ChartContainer = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => {
  return (
    <div ref={ref} className={cn("w-full", className)} {...props}>
      {children}
    </div>
  );
});
ChartContainer.displayName = "ChartContainer";

const ChartTooltipContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    hideLabel?: boolean;
    label?: string;
    payload?: Array<{
      name?: string;
      value?: string | number | undefined;
      color?: string;
      dataKey?: string;
    }>;
  }
>(({ className, hideLabel = false, label, payload, ...props }, ref) => {
  if (!payload?.length) {
    return null;
  }

  return (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border bg-background p-2 shadow-md",
        className
      )}
      {...props}
    >
      {!hideLabel && label && (
        <div className="mb-1 font-medium text-foreground">{label}</div>
      )}
      <div className="grid gap-1">
        {payload.map((item, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            {item.color && (
              <div
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: item.color }}
              />
            )}
            <span className="text-muted-foreground">{item.name}:</span>
            <span className="font-medium text-foreground">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
});
ChartTooltipContent.displayName = "ChartTooltipContent";

export { ChartContainer, ChartTooltipContent };

