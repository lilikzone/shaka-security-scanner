"use client";

import { useEffect, useMemo, useState } from "react";
import { liveLogs } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function LogViewer() {
  const [lineCount, setLineCount] = useState(4);

  useEffect(() => {
    const timer = setInterval(() => {
      setLineCount((prev) => (prev >= liveLogs.length ? prev : prev + 1));
    }, 1100);

    return () => clearInterval(timer);
  }, []);

  const logs = useMemo(() => liveLogs.slice(0, lineCount), [lineCount]);

  return (
    <Card className="grid-bg">
      <CardHeader>
        <CardTitle className="text-base">Live Scanner Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="terminal-font max-h-72 overflow-y-auto rounded-lg border border-border bg-slate-950/80 p-3 text-xs leading-relaxed text-emerald-300">
          {logs.map((line) => (
            <p key={line}>{line}</p>
          ))}
          {lineCount < liveLogs.length && <p className="animate-pulse text-cyan-300">_ streaming ...</p>}
        </div>
      </CardContent>
    </Card>
  );
}
