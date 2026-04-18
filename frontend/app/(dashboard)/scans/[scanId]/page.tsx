import { notFound } from "next/navigation";
import { scans, scanTimeline, vulnerabilities } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { LogViewer } from "@/components/domain/log-viewer";

export default async function ScanDetailPage({ params }: { params: Promise<{ scanId: string }> }) {
  const { scanId } = await params;
  const scan = scans.find((item) => item.id === scanId);

  if (!scan) {
    notFound();
  }

  const grouped = {
    web: vulnerabilities.filter((v) => v.category === "web"),
    network: vulnerabilities.filter((v) => v.category === "network"),
    misconfiguration: vulnerabilities.filter((v) => v.category === "misconfiguration" || v.category === "api")
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-border bg-panel p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Scan Detail</p>
        <h1 className="mt-2 text-2xl font-semibold">{scan.target}</h1>
        <p className="mt-2 text-sm text-slate-300">
          {scan.id} • {scan.type} • status {scan.status} • risk {scan.riskScore.toFixed(1)}
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {scanTimeline.map((item) => (
              <div key={`${item.at}-${item.event}`} className="rounded-lg border border-border bg-panelAlt p-3">
                <p className="terminal-font text-xs text-cyan-300">{item.at}</p>
                <p className="text-sm text-slate-100">{item.event}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="xl:col-span-2">
          <LogViewer />
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <IssueGroup title="Web" items={grouped.web} />
        <IssueGroup title="Network" items={grouped.network} />
        <IssueGroup title="Misconfiguration" items={grouped.misconfiguration} />
      </div>
    </div>
  );
}

function IssueGroup({
  title,
  items
}: {
  title: string;
  items: Array<{ id: string; name: string; severity: "critical" | "high" | "medium" | "low" | "info" }>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-400">No issues found.</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="rounded-lg border border-border bg-panelAlt p-3">
              <p className="mb-2 text-sm text-slate-100">{item.name}</p>
              <SeverityBadge severity={item.severity} />
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
