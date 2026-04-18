"use client";

import { FormEvent, useState } from "react";
import { chatSeed } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const quickReplies = {
  "How to fix this vulnerability?":
    "Start with parameterized SQL, then add input validation and WAF signatures for immediate defense-in-depth.",
  "Is this critical?":
    "Yes, this is critical due to high exploitability and direct exposure to sensitive customer data.",
  "What should be fixed first?":
    "Fix SQL Injection first, then transport security weaknesses, then XSS hardening."
};

export function ChatPanel() {
  const [messages, setMessages] = useState(chatSeed);
  const [prompt, setPrompt] = useState("");

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!prompt.trim()) return;

    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const userMessage = { id: crypto.randomUUID(), role: "user" as const, content: prompt, timestamp: now };
    const answer = quickReplies[prompt as keyof typeof quickReplies] ??
      "I can break this finding into exploitability, impact, and remediation steps. Ask for an executive summary if needed.";

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: crypto.randomUUID(), role: "assistant" as const, content: answer, timestamp: now }
    ]);

    setPrompt("");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">AI Security Chat</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
          {messages.map((message) => (
            <div
              key={message.id}
              className={message.role === "assistant" ? "rounded-lg bg-panelAlt p-3" : "ml-auto max-w-[85%] rounded-lg bg-accent/20 p-3"}
            >
              <div className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">{message.role}</div>
              <p className="text-sm text-slate-100">{message.content}</p>
            </div>
          ))}
        </div>

        <form onSubmit={onSubmit} className="flex gap-2">
          <Input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Ask: How to fix this vulnerability?" />
          <Button type="submit">Send</Button>
        </form>
      </CardContent>
    </Card>
  );
}
