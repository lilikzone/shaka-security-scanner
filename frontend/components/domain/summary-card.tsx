import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn, formatNumber } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface SummaryCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  trend?: string;
  tone?: "default" | "danger";
}

export function SummaryCard({ label, value, icon: Icon, trend, tone = "default" }: SummaryCardProps) {
  return (
    <Card className={cn("transition-all hover:border-accent/35", tone === "danger" && "border-danger/50 shadow-danger")}> 
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <CardTitle className="text-xs uppercase tracking-[0.16em] text-slate-400">{label}</CardTitle>
        <div className="rounded-lg bg-panelAlt p-2 text-slate-300">
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold tracking-tight">{typeof value === "number" ? formatNumber(value) : value}</div>
        {trend && <p className="mt-1 text-xs text-slate-400">{trend}</p>}
      </CardContent>
    </Card>
  );
}
