import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("relative overflow-hidden rounded-md bg-slate-800/70", className)}>
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-slate-700/50 to-transparent animate-shimmer" />
    </div>
  );
}
