/**
 * Chat Message Component
 * Displays a single chat message with optional SQL query
 */

"use client";

import { useState } from "react";

import { ChevronDown, ChevronUp } from "lucide-react";
import { motion } from "framer-motion";

import type { ChatMessage } from "@/types/chat";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessage;
}

export function ChatMessageComponent({ message }: ChatMessageProps): JSX.Element {
  const [showSql, setShowSql] = useState(false);
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("flex flex-col gap-2", isUser ? "items-end" : "items-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2 shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-muted-foreground"
        )}
      >
        <p className="whitespace-pre-wrap break-words text-sm">{message.content}</p>
      </div>

      {message.sqlQuery && (
        <div className="w-full max-w-[80%]">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSql(!showSql)}
            className="h-auto gap-1 px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
          >
            {showSql ? (
              <>
                <ChevronUp className="h-3 w-3" />
                Hide SQL
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" />
                Show SQL
              </>
            )}
          </Button>

          {showSql && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2 overflow-hidden"
            >
              <pre className="rounded-lg bg-muted p-3 text-xs">
                <code className="font-mono text-muted-foreground">{message.sqlQuery}</code>
              </pre>
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
}

