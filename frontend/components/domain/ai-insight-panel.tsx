import { aiSummary } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot } from "lucide-react";

export function AiInsightPanel() {
  return (
    <Card className="border-accent/30">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Bot className="h-4 w-4 text-accent" /> AI Security Insight
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="rounded-lg border border-accent/40 bg-accent/10 p-3 text-sm text-cyan-100">{aiSummary.headline}</p>
        <p className="text-sm leading-relaxed text-slate-300">{aiSummary.explanation}</p>
        <div>
          <p className="mb-2 text-xs uppercase tracking-widest text-slate-400">Suggested Remediation</p>
          <ul className="space-y-2 text-sm text-slate-200">
            {aiSummary.remediationSteps.map((step) => (
              <li key={step} className="rounded-md bg-panelAlt/80 px-3 py-2">{step}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
