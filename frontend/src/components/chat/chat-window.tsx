/**
 * Chat Window Component
 * Main chat interface with messages, input, and mode toggle
 */

"use client";

import { useEffect, useRef, useState } from "react";

import { AnimatePresence, motion } from "framer-motion";
import { Send, X } from "lucide-react";

import type { ChatMessage, ChatMode } from "@/types/chat";

import { Button } from "@/components/ui/button";
import { createChatSession, sendMessage } from "@/lib/chat-api";
import {
  generateUsername,
  getUsernameForMode,
  setUsernameForMode,
  validateUsername,
} from "@/lib/user-storage";

import { ChatMessageComponent } from "./chat-message";
import { ModeToggle } from "./mode-toggle";
import { TypingIndicator } from "./typing-indicator";
import { UserNameBadge } from "./user-name-badge";

interface ChatWindowProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatWindow({ isOpen, onClose }: ChatWindowProps): JSX.Element {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mode, setMode] = useState<ChatMode>("normal");
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState<string>("");
  const [userId, setUserId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Create session on mount or mode change
  useEffect(() => {
    if (isOpen && !sessionId) {
      // 1. Get username from localStorage for current mode
      let currentUsername = getUsernameForMode(mode);

      // 2. If no username - generate new one
      if (!currentUsername) {
        currentUsername = generateUsername();
        setUsernameForMode(mode, currentUsername);
      }

      setUsername(currentUsername);

      // 3. Create session with username
      createChatSession(mode, currentUsername)
        .then((session) => {
          setSessionId(session.session_id);
          setUserId(session.user_id);
        })
        .catch((err) => {
          console.error("Failed to create session:", err);
          setError("Failed to create chat session");
        });
    }
  }, [isOpen, sessionId, mode]);

  // Focus input when window opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSend = async (): Promise<void> => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);

    // Add user message to UI
    const newUserMessage: ChatMessage = {
      role: "user",
      content: userMessage,
    };
    setMessages((prev) => [...prev, newUserMessage]);

    setIsLoading(true);

    try {
      // Send message to API
      const response = await sendMessage(sessionId, userMessage, mode);

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.content,
        sqlQuery: response.sql_query,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(err instanceof Error ? err.message : "Failed to send message");

      // Add error message
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error processing your message. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = async (newMode: ChatMode): Promise<void> => {
    if (newMode === mode) return;

    setMode(newMode);
    setMessages([]);
    setError(null);

    // Get or generate username for new mode
    let newUsername = getUsernameForMode(newMode);
    if (!newUsername) {
      newUsername = generateUsername();
      setUsernameForMode(newMode, newUsername);
    }

    setUsername(newUsername);

    // Create new session with new mode and username
    try {
      const session = await createChatSession(newMode, newUsername);
      setSessionId(session.session_id);
      setUserId(session.user_id);
    } catch (err) {
      console.error("Failed to create session:", err);
      setError("Failed to switch mode");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleUsernameChange = async (newUsername: string): Promise<void> => {
    // Validate format
    if (!validateUsername(newUsername)) {
      throw new Error("Invalid username format");
    }

    setUsernameForMode(mode, newUsername);
    setUsername(newUsername);
    setMessages([]);
    setError(null);

    try {
      // Recreate session with new username
      const session = await createChatSession(mode, newUsername);
      setSessionId(session.session_id);
      setUserId(session.user_id);
    } catch (err) {
      console.error("Failed to change username:", err);
      setError("Failed to change username");
      throw err;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="fixed bottom-20 right-6 z-40 flex h-[600px] w-full flex-col overflow-hidden rounded-2xl border bg-background shadow-2xl sm:w-[400px]"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-3">
            <div className="flex items-center gap-3">
              <h2 className="text-sm font-semibold">AI Assistant</h2>
              {username && (
                <UserNameBadge username={username} onUsernameChange={handleUsernameChange} />
              )}
              <ModeToggle mode={mode} onModeChange={handleModeChange} />
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.length === 0 && (
              <div className="flex h-full items-center justify-center text-center">
                <p className="text-sm text-muted-foreground">
                  {mode === "admin"
                    ? "Ask questions about bot statistics and conversations"
                    : "Start a conversation with the AI assistant"}
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <ChatMessageComponent key={index} message={message} />
            ))}

            {isLoading && <TypingIndicator />}

            {error && (
              <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t bg-muted/50 p-4">
            <div className="flex gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                disabled={isLoading}
                className="min-h-[40px] max-h-[120px] flex-1 resize-none rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                rows={1}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
                className="h-10 w-10 shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

