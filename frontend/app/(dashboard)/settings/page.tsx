"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const [alerts, setAlerts] = useState(true);
  const [weeklyDigest, setWeeklyDigest] = useState(false);
  const [rbacPreview, setRbacPreview] = useState(true);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">API Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Scanner API Endpoint</label>
              <Input defaultValue="https://scanner-api.shaka.local/v1" />
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Auth Token</label>
              <Input type="password" defaultValue="***************" />
            </div>
            <Button>Save API Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">AI Engine</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">AI Provider</label>
              <Select options={[{ label: "Bedrock", value: "bedrock" }, { label: "Ollama", value: "ollama" }]} />
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Model</label>
              <Select
                options={[
                  { label: "Claude 3.5 Sonnet", value: "claude-3-5-sonnet" },
                  { label: "Llama 3.1 70B", value: "llama-3-1-70b" }
                ]}
              />
            </div>
            <Button variant="secondary">Test AI Connection</Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notifications & Access</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <SettingRow
            title="Critical vulnerability alerts"
            subtitle="Send immediate alerts to SOC channel when severity is critical"
            checked={alerts}
            onChange={setAlerts}
          />
          <SettingRow
            title="Weekly executive digest"
            subtitle="Summarized risk report for management audience"
            checked={weeklyDigest}
            onChange={setWeeklyDigest}
          />
          <SettingRow
            title="Role-based UI preview"
            subtitle="Enable policy-aware controls for future multi-tenant rollout"
            checked={rbacPreview}
            onChange={setRbacPreview}
          />
        </CardContent>
      </Card>
    </div>
  );
}

function SettingRow({
  title,
  subtitle,
  checked,
  onChange
}: {
  title: string;
  subtitle: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border bg-panelAlt p-3">
      <div>
        <p className="text-sm font-medium text-slate-100">{title}</p>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>
      <Switch checked={checked} onChange={onChange} />
    </div>
  );
}
