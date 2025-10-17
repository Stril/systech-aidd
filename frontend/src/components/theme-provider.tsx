"use client";

/**
 * Theme Provider component using next-themes
 * Provides dark/light theme switching with localStorage persistence
 */

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ReactNode } from "react";

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps): JSX.Element {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange={false}
    >
      {children}
    </NextThemesProvider>
  );
}

