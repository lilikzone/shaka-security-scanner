import { Activity, AlertOctagon, Radar, ShieldAlert } from "lucide-react";
import { dashboardSummary, scans } from "@/lib/mock-data";
import { SummaryCard } from "@/components/domain/summary-card";
import { VulnerabilityTrendChart } from "@/components/charts/vulnerability-trend-chart";
import { SeverityDistributionChart } from "@/components/charts/severity-distribution-chart";
import { ScanCard } from "@/components/domain/scan-card";
import { AiInsightPanel } from "@/components/domain/ai-insight-panel";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-accent/30 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-emerald-500/10 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">SOC Overview</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Shaka Security Command Center</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-300">
          AI-assisted vulnerability operations for security engineers, DevOps, and SOC teams. Monitor active scans,
          prioritize risk, and execute remediation with context-rich findings.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Total Scans" value={dashboardSummary.totalScans} icon={Radar} trend="+14.6% this month" />
        <SummaryCard label="Active Scans" value={dashboardSummary.activeScans} icon={Activity} trend="3 in aggressive mode" />
        <SummaryCard
          label="Critical Vulnerabilities"
          value={dashboardSummary.criticalVulnerabilities}
          icon={AlertOctagon}
          trend="Immediate triage required"
          tone="danger"
        />
        <SummaryCard
          label="Risk Score"
          value={dashboardSummary.riskScore.toFixed(1)}
          icon={ShieldAlert}
          trend={`+${dashboardSummary.riskDelta.toFixed(1)} since yesterday`}
          tone="danger"
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <VulnerabilityTrendChart />
        </div>
        <SeverityDistributionChart />
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400">Recent Scan Activity</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {scans.map((scan) => (
              <ScanCard key={scan.id} scan={scan} />
            ))}
          </div>
        </div>
        <AiInsightPanel />
      </section>
    </div>
  );
}
