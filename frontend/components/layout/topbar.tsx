"use client";

import { Bell, Search, TerminalSquare, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useUiStore } from "@/store/ui-store";
import { cn } from "@/lib/utils";

export function Topbar() {
  const { audienceMode, toggleAudienceMode } = useUiStore();
  const isPentester = audienceMode === "pentester";

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/85 px-4 py-3 backdrop-blur md:px-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="relative w-full max-w-xl">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <Input placeholder="Search target, CVE, scanner module..." className="pl-9" />
        </div>

        <div className="flex items-center gap-2">
          <button
            className={cn(
              "inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold uppercase tracking-wide transition",
              isPentester
                ? "border-accent/40 bg-accent/15 text-cyan-200"
                : "border-border bg-panelAlt text-slate-300"
            )}
            onClick={toggleAudienceMode}
          >
            <TerminalSquare className="h-4 w-4" /> Pentester Mode
          </button>
          <button
            className={cn(
              "inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold uppercase tracking-wide transition",
              !isPentester
                ? "border-accent/40 bg-accent/15 text-cyan-200"
                : "border-border bg-panelAlt text-slate-300"
            )}
            onClick={toggleAudienceMode}
          >
            <User className="h-4 w-4" /> Executive Mode
          </button>

          <button className="rounded-lg border border-border bg-panelAlt p-2 text-slate-300 hover:text-white">
            <Bell className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
