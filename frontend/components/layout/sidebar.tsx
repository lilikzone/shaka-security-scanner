"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/store/ui-store";
import {
  AlertTriangle,
  Bot,
  Gauge,
  Logs,
  Radar,
  Settings,
  Shield,
  Sidebar,
  Target
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/scans", label: "Scan Management", icon: Radar },
  { href: "/vulnerabilities", label: "Vulnerabilities", icon: AlertTriangle },
  { href: "/insights", label: "AI Insights", icon: Bot },
  { href: "/scans/scan-8841", label: "Scan Detail", icon: Logs },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppSidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        "hidden border-r border-border bg-panel/95 backdrop-blur-md md:block",
        "transition-all duration-300",
        sidebarCollapsed ? "w-20" : "w-72"
      )}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-border px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg border border-accent/40 bg-accent/10 p-2 text-accent">
              <Shield className="h-5 w-5" />
            </div>
            {!sidebarCollapsed && (
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Shaka Security</p>
                <p className="text-sm font-semibold">Scanner Console</p>
              </div>
            )}
          </div>
          <button
            className="rounded-md p-1.5 text-slate-400 hover:bg-panelAlt hover:text-slate-100"
            onClick={toggleSidebar}
            aria-label="Collapse sidebar"
          >
            <Sidebar className="h-4 w-4" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all",
                  active
                    ? "bg-accent/15 text-accent shadow-[inset_0_0_0_1px_rgba(34,211,238,.35)]"
                    : "text-slate-300 hover:bg-panelAlt hover:text-slate-100"
                )}
              >
                <Icon className="h-4 w-4" />
                {!sidebarCollapsed && item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border p-4">
          <div className="rounded-lg border border-danger/40 bg-danger/10 p-3 text-xs text-red-200">
            <p className="mb-1 flex items-center gap-2 font-semibold uppercase tracking-wide">
              <Target className="h-3.5 w-3.5" /> High-Risk Target
            </p>
            {!sidebarCollapsed && <p>api.shaka-finance.io shows exploit-ready findings.</p>}
          </div>
        </div>
      </div>
    </aside>
  );
}
