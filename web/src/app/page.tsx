"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Agent = { id: string; name: string; description?: string };
type InboxItem = {
  id: string;
  prompt: string;
  agent_id: string;
  status: "idle" | "running" | "done" | "error";
  result?: string;
  error?: string;
};

async function fetchAgents(): Promise<Agent[]> {
  const base = process.env.NEXT_PUBLIC_SERVER_URL || "http://localhost:8000";
  const res = await fetch(base + "/api/agents");
  if (!res.ok) throw new Error("Failed to load agents");
  const data = await res.json();
  return data.agents ?? [];
}

async function runAgent(
  prompt: string,
  agent_id: string
): Promise<{ report?: string; assistant_message?: string }> {
  const base = process.env.NEXT_PUBLIC_SERVER_URL || "http://localhost:8000";
  const res = await fetch(base + "/api/agent/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, agent_id }),
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || "Agent run failed");
  }
  return res.json();
}

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgent, setActiveAgent] = useState<string>("research");
  const [prompt, setPrompt] = useState("");
  const [inbox, setInbox] = useState<InboxItem[]>([]);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(() => setAgents([{ id: "research", name: "Research Agent" }]));
  }, []);

  const canSubmit = useMemo(() => prompt.trim().length > 0 && !!activeAgent, [prompt, activeAgent]);

  const onSubmit = async () => {
    if (!canSubmit) return;
    const id = `${Date.now()}`;
    const item: InboxItem = { id, prompt, agent_id: activeAgent, status: "running" };
    setInbox((prev) => [item, ...prev]);
    setPrompt("");

    try {
      const res = await runAgent(item.prompt, item.agent_id);
      setInbox((prev) => prev.map((x) => (x.id === id ? { ...x, status: "done", result: res.report || res.assistant_message } : x)));
    } catch (e: any) {
      setInbox((prev) => prev.map((x) => (x.id === id ? { ...x, status: "error", error: e?.message || "Failed" } : x)));
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-5xl p-6">
        <header className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">DeepAgents Inbox</h1>
          <div className="flex items-center gap-3">
            <select
              value={activeAgent}
              onChange={(e) => setActiveAgent(e.target.value)}
              className="rounded-md border px-3 py-2"
            >
              {agents.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
        </header>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Prompt</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              ref={inputRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask the research agent..."
              className="mb-3 w-full resize-y rounded-md border p-3 focus:outline-none"
              rows={4}
            />
            <div className="flex justify-end">
              <button
                onClick={onSubmit}
                disabled={!canSubmit}
                className="rounded-md bg-black px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
              >
                Send
              </button>
            </div>
          </CardContent>
        </Card>

        <section>
          <h2 className="mb-3 text-lg font-medium">Inbox</h2>
          <div className="grid gap-3">
            {inbox.map((m) => (
              <div key={m.id} className="rounded-lg border p-4">
                <div className="mb-2 flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">{m.agent_id}</div>
                  <div className="text-xs">
                    {m.status === "running" && <span className="text-amber-600">Running…</span>}
                    {m.status === "done" && <span className="text-green-600">Done</span>}
                    {m.status === "error" && <span className="text-red-600">Error</span>}
                  </div>
                </div>
                <div className="mb-2 whitespace-pre-wrap text-sm">{m.prompt}</div>
                {m.result && (
                  <div className="mt-2 rounded-md bg-muted p-3 text-sm whitespace-pre-wrap">{m.result}</div>
                )}
                {m.error && (
                  <div className="mt-2 rounded-md bg-red-50 p-3 text-sm text-red-700 whitespace-pre-wrap">{m.error}</div>
                )}
              </div>
            ))}
            {inbox.length === 0 && (
              <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
                No prompts yet. Submit one above.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
