/**
 * Mode Toggle Component
 * Toggles between normal and admin chat modes
 */

import type { ChatMode } from "@/types/chat";

import { Button } from "@/components/ui/button";

interface ModeToggleProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
}

export function ModeToggle({ mode, onModeChange }: ModeToggleProps): JSX.Element {
  return (
    <div className="flex items-center gap-1 rounded-lg border bg-background p-1">
      <Button
        variant={mode === "normal" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("normal")}
        className="h-7 px-3 text-xs"
      >
        Normal
      </Button>
      <Button
        variant={mode === "admin" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("admin")}
        className="h-7 px-3 text-xs"
      >
        Admin
      </Button>
    </div>
  );
}

