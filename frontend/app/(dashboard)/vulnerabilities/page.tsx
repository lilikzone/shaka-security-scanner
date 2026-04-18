"use client";

import { vulnerabilities } from "@/lib/mock-data";
import { SeverityBadge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { useUiStore } from "@/store/ui-store";

export default function VulnerabilitiesPage() {
  const { selectedVulnerabilityId, selectVulnerability } = useUiStore();
  const selected = vulnerabilities.find((vuln) => vuln.id === selectedVulnerabilityId) ?? vulnerabilities[0];

  return (
    <div className="grid gap-6 xl:grid-cols-3">
      <Card className="xl:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Vulnerability Results</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <THead>
              <TR>
                <TH>Vulnerability</TH>
                <TH>Severity</TH>
                <TH>CVE/CWE</TH>
                <TH>Affected Target</TH>
              </TR>
            </THead>
            <TBody>
              {vulnerabilities.map((vuln) => (
                <TR
                  key={vuln.id}
                  className={selected.id === vuln.id ? "bg-accent/10" : ""}
                  onClick={() => selectVulnerability(vuln.id)}
                >
                  <TD className="font-medium">{vuln.name}</TD>
                  <TD>
                    <SeverityBadge severity={vuln.severity} />
                  </TD>
                  <TD>{vuln.cve ?? "-"}</TD>
                  <TD>{vuln.target}</TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Finding Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Description</p>
            <p className="mt-1 text-slate-100">{selected.description}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Exploit Scenario</p>
            <p className="mt-1 text-slate-100">{selected.exploitScenario}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Recommendation</p>
            <p className="mt-1 text-slate-100">{selected.recommendation}</p>
          </div>
          <div className="rounded-lg border border-accent/30 bg-accent/10 p-3">
            <p className="text-xs uppercase tracking-wide text-cyan-200">AI Analysis</p>
            <p className="mt-1 text-cyan-50">{selected.aiAnalysis}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
