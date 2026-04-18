import { AiInsightPanel } from "@/components/domain/ai-insight-panel";
import { ChatPanel } from "@/components/domain/chat-panel";

export default function InsightsPage() {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <AiInsightPanel />
      <ChatPanel />
    </div>
  );
}
