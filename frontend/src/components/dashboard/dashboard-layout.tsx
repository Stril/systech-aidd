/**
 * Dashboard Layout Component
 * Provides header with GitHub link, title, theme toggle, and chat
 */

"use client";

import { useState } from "react";

import { Github } from "lucide-react";
import Link from "next/link";

import { ChatWindow } from "@/components/chat/chat-window";
import { FloatingChatButton } from "@/components/chat/floating-chat-button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4 md:px-8">
          <div className="flex items-center gap-2 sm:gap-4">
            <Link
              href="https://github.com/aidialogs/systech-aidd/tree/main"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="ghost" size="icon" aria-label="View on GitHub">
                <Github className="h-5 w-5" />
              </Button>
            </Link>
            <h1 className="text-sm font-semibold sm:text-base md:text-xl">Bot Statistics Dashboard</h1>
          </div>
          <ThemeToggle />
        </div>
      </header>
      <main className="container px-4 py-6 md:px-8">{children}</main>

      {/* Floating Chat */}
      <FloatingChatButton
        onClick={() => setIsChatOpen(!isChatOpen)}
        isOpen={isChatOpen}
      />
      <ChatWindow isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
}

