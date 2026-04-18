"use client";

import { scans } from "@/lib/mock-data";
import { Button } from "@/components/ui/button";
import { ScanCard } from "@/components/domain/scan-card";
import { ScanCreateModal } from "@/components/domain/scan-create-modal";
import { useUiStore } from "@/store/ui-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ScansPage() {
  const { setScanCreationOpen } = useUiStore();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Scan Management</h1>
          <p className="text-sm text-slate-300">Launch and monitor multi-target scans across domain, IP, and API surfaces.</p>
        </div>
        <Button onClick={() => setScanCreationOpen(true)}>Create New Scan</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Execution Queue</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {scans.map((scan) => (
            <ScanCard key={scan.id} scan={scan} />
          ))}
        </CardContent>
      </Card>

      <ScanCreateModal />
    </div>
  );
}
