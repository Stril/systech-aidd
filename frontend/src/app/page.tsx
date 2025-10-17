"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { checkApiHealth } from "@/lib/api";

export default function Home() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const checkApi = async () => {
      try {
        await checkApiHealth();
        setApiStatus("ok");
      } catch (err) {
        setApiStatus("error");
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    };

    checkApi();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <Card className="w-full">
          <CardHeader>
            <CardTitle>AIDD Frontend - Dashboard и Web-чат</CardTitle>
            <CardDescription>Спринт FE-SP-2: Инициализация Frontend проекта</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Статус API Backend:</h3>
              <div className="flex items-center gap-2">
                <div
                  className={`h-3 w-3 rounded-full ${
                    apiStatus === "checking"
                      ? "bg-yellow-500"
                      : apiStatus === "ok"
                        ? "bg-green-500"
                        : "bg-red-500"
                  }`}
                />
                <span>
                  {apiStatus === "checking"
                    ? "Проверка соединения..."
                    : apiStatus === "ok"
                      ? "Подключено"
                      : "Ошибка подключения"}
                </span>
              </div>
              {apiStatus === "error" && <p className="text-sm text-red-600">Ошибка: {error}</p>}
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Технологический стек:</h3>
              <ul className="list-inside list-disc space-y-1 text-sm">
                <li>Framework: Next.js 14 (App Router)</li>
                <li>Language: TypeScript (strict mode)</li>
                <li>UI Library: shadcn/ui</li>
                <li>Styling: Tailwind CSS</li>
                <li>Package Manager: pnpm</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Следующие шаги:</h3>
              <ul className="list-inside list-disc space-y-1 text-sm">
                <li>FE-SP-3: Реализация Dashboard</li>
                <li>FE-SP-4: Реализация ИИ-чата</li>
                <li>FE-SP-5: Переход на Real API</li>
              </ul>
            </div>

            <div className="flex gap-2 pt-4">
              <Button asChild>
                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                  API Документация
                </a>
              </Button>
              <Button variant="outline" asChild>
                <a
                  href="https://github.com/yourusername/systech-aidd-1"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
