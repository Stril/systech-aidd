/**
 * User Name Badge Component
 * Displays username with inline editing capability
 */

"use client";

import { useState } from "react";

import { Check, Pencil, X } from "lucide-react";

import { validateUsername } from "@/lib/user-storage";

import { Button } from "../ui/button";

interface UserNameBadgeProps {
  username: string;
  onUsernameChange: (newUsername: string) => Promise<void>;
}

export function UserNameBadge({ username, onUsernameChange }: UserNameBadgeProps): JSX.Element {
  const [isEditing, setIsEditing] = useState(false);
  const [editedUsername, setEditedUsername] = useState(username);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEdit = (): void => {
    setIsEditing(true);
    setEditedUsername(username);
    setError(null);
  };

  const handleCancel = (): void => {
    setIsEditing(false);
    setEditedUsername(username);
    setError(null);
  };

  const handleSave = async (): Promise<void> => {
    // Validate format
    if (!validateUsername(editedUsername)) {
      setError("Invalid format. Use 'User_NNNNN' (5 digits)");
      return;
    }

    // No change
    if (editedUsername === username) {
      setIsEditing(false);
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await onUsernameChange(editedUsername);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change username");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  if (!isEditing) {
    return (
      <div className="flex items-center gap-1.5 rounded-md bg-muted px-2 py-1 text-xs">
        <span className="font-mono text-muted-foreground">{username}</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleEdit}
          className="h-4 w-4 hover:bg-transparent"
          title="Edit username"
        >
          <Pencil className="h-3 w-3" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1">
        <input
          type="text"
          value={editedUsername}
          onChange={(e) => setEditedUsername(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          className="h-7 w-24 rounded border bg-background px-2 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          autoFocus
          maxLength={10}
        />
        <Button
          variant="ghost"
          size="icon"
          onClick={handleSave}
          disabled={isLoading}
          className="h-6 w-6"
          title="Save"
        >
          <Check className="h-3 w-3 text-green-600" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleCancel}
          disabled={isLoading}
          className="h-6 w-6"
          title="Cancel"
        >
          <X className="h-3 w-3 text-red-600" />
        </Button>
      </div>
      {error && <span className="text-[10px] text-destructive">{error}</span>}
    </div>
  );
}

