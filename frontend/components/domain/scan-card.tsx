import Link from "next/link";
import { Scan } from "@/types/security";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const stateTone = {
  running: "text-cyan-300 border-cyan-400/50 bg-cyan-500/10",
  completed: "text-emerald-300 border-emerald-400/50 bg-emerald-500/10",
  failed: "text-red-300 border-red-400/50 bg-red-500/10",
  queued: "text-slate-300 border-slate-500/50 bg-slate-500/10"
};

export function ScanCard({ scan }: { scan: Scan }) {
  return (
    <Card className="hover:border-accent/30">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">{scan.target}</CardTitle>
            <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">
              {scan.id} • {scan.type} scan
            </p>
          </div>
          <span className={cn("rounded-md border px-2 py-1 text-[11px] font-semibold uppercase", stateTone[scan.status])}>
            {scan.status}
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <div className="mb-1 flex justify-between text-xs text-slate-400">
            <span>Progress</span>
            <span>{scan.progress}%</span>
          </div>
          <Progress value={scan.progress} />
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-300">Findings: {scan.findingsCount}</span>
          <span className="font-semibold text-amber-300">Risk {scan.riskScore.toFixed(1)}</span>
        </div>

        <Link href={`/scans/${scan.id}`} className="text-xs font-semibold uppercase tracking-wide text-accent hover:underline">
          Open Scan Detail
        </Link>
      </CardContent>
    </Card>
  );
}
