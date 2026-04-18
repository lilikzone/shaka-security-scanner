"use client";

import { Dialog } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useUiStore } from "@/store/ui-store";

export function ScanCreateModal() {
  const { scanCreationOpen, setScanCreationOpen } = useUiStore();

  return (
    <Dialog title="Create New Security Scan" open={scanCreationOpen} onClose={() => setScanCreationOpen(false)}>
      <div className="grid gap-4">
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Target</label>
          <Input placeholder="domain.com | 10.0.0.1 | https://api.company.com/openapi.json" />
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Scan Type</label>
            <Select
              options={[
                { label: "Full Scan", value: "full" },
                { label: "Web Scan", value: "web" },
                { label: "API Scan", value: "api" },
                { label: "Network Scan", value: "network" }
              ]}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Execution Profile</label>
            <Select
              options={[
                { label: "Passive", value: "passive" },
                { label: "Active", value: "active" },
                { label: "Aggressive", value: "aggressive" }
              ]}
            />
          </div>
        </div>

        <div className="rounded-lg border border-accent/30 bg-accent/10 p-3 text-xs text-cyan-100">
          AI-assisted prioritization and exploitability scoring will run automatically after findings are collected.
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setScanCreationOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => setScanCreationOpen(false)}>Launch Scan</Button>
        </div>
      </div>
    </Dialog>
  );
}
