export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type ScanState = "queued" | "running" | "completed" | "failed";
export type ScanMode = "full" | "web" | "api" | "network";
export type AudienceMode = "pentester" | "executive";

export interface Vulnerability {
  id: string;
  name: string;
  severity: Severity;
  cve?: string;
  target: string;
  category: "web" | "network" | "misconfiguration" | "api";
  description: string;
  exploitScenario: string;
  recommendation: string;
  aiAnalysis: string;
  discoveredAt: string;
}

export interface Scan {
  id: string;
  target: string;
  type: ScanMode;
  status: ScanState;
  progress: number;
  startedAt: string;
  completedAt?: string;
  findingsCount: number;
  riskScore: number;
}

export interface InsightMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: string;
}
