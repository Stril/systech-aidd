/**
 * Typing Indicator Component
 * Shows animated dots when assistant is typing
 */

export function TypingIndicator(): JSX.Element {
  return (
    <div className="flex items-center gap-1 rounded-xl bg-muted px-4 py-3">
      <div className="h-2 w-2 animate-pulse rounded-full bg-foreground"></div>
      <div className="h-2 w-2 animate-pulse rounded-full bg-foreground delay-150"></div>
      <div className="h-2 w-2 animate-pulse rounded-full bg-foreground delay-300"></div>
    </div>
  );
}

