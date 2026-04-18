import { cn } from "@/lib/utils";

const severityMap = {
  critical: "bg-danger/20 text-red-200 border-danger/60",
  high: "bg-orange-500/20 text-orange-200 border-orange-400/60",
  medium: "bg-warning/20 text-yellow-200 border-yellow-400/60",
  low: "bg-success/20 text-green-200 border-green-400/60",
  info: "bg-info/20 text-blue-200 border-blue-400/60"
};

export function SeverityBadge({ severity, className }: { severity: keyof typeof severityMap; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide",
        severityMap[severity],
        className
      )}
    >
      {severity}
    </span>
  );
}
