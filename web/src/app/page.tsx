"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Loader2, Brain, CheckCircle, AlertCircle, Cpu } from "lucide-react";

type Agent = { id: string; name: string; description?: string };
type InboxItem = {
  id: string;
  prompt: string;
  agent_id: string;
  status: "idle" | "running" | "done" | "error";
  result?: string;
  error?: string;
  progress?: number;
  currentStep?: string;
  startTime?: number;
  thinkingStream?: Array<{text: string; tools: string[]}>;
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
): Promise<{ report?: string; assistant_message?: string; thinking_steps?: Array<{text: string; tools: string[]}> }> {
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
    const item: InboxItem = { 
      id, 
      prompt, 
      agent_id: activeAgent, 
      status: "running",
      progress: 0,
      currentStep: "Initializing research...",
      startTime: Date.now(),
      thinkingStream: [
        { text: "🔍 Initializing research...", tools: ["Query Analyzer", "Research Initializer"] }
      ]
    };
    setInbox((prev) => [item, ...prev]);
    setPrompt("");

    // Simulate realistic thinking stream and progress
    const thinkingSteps = [
      { text: "🔍 Analyzing the research question...", tools: ["Query Analyzer", "NLP Processor"] },
      { text: "🌐 Initiating web search for relevant information...", tools: ["Tavily Search", "Web Crawler"] },
      { text: "📄 Found multiple sources, scanning content...", tools: ["Content Parser", "PDF Reader"] },
      { text: "🔍 Searching for official documentation...", tools: ["Academic Search", "Document Finder"] },
      { text: "📊 Analyzing data from authoritative sources...", tools: ["Data Analyzer", "Source Validator"] },
      { text: "🧠 Cross-referencing information for accuracy...", tools: ["Fact Checker", "Cross Referencer"] },
      { text: "📝 Extracting key facts and insights...", tools: ["Text Extractor", "Insight Generator"] },
      { text: "🔗 Identifying additional relevant sources...", tools: ["Link Crawler", "Citation Finder"] },
      { text: "📋 Organizing information into coherent structure...", tools: ["Content Organizer", "Structure Builder"] },
      { text: "✍️ Synthesizing findings into comprehensive report...", tools: ["Report Generator", "Content Synthesizer"] },
      { text: "📑 Formatting with proper markdown structure...", tools: ["Markdown Formatter", "Document Styler"] },
      { text: "🔗 Adding citations and source references...", tools: ["Citation Manager", "Reference Builder"] },
      { text: "✅ Finalizing research report...", tools: ["Quality Checker", "Final Validator"] }
    ];

    let stepIndex = 1; // Start from 1 since we already added initial step
    const progressInterval = setInterval(() => {
      setInbox((prev) => prev.map((x) => {
        if (x.id === id && x.status === "running") {
          const elapsed = Date.now() - (x.startTime || Date.now());
          const newProgress = Math.min(90, (elapsed / 45000) * 100); // Progress to 90% over 45 seconds
          
          // Add new thinking step periodically and update current step
          const newThinking = [...(x.thinkingStream || [])];
          if (stepIndex < thinkingSteps.length && elapsed > stepIndex * 3500) {
            newThinking.push(thinkingSteps[stepIndex]);
            stepIndex++;
          }
          
          // Get current step info for live updates
          let currentStepText = "Conducting research...";
          let currentStepTools = ["Research Engine"];
          
          if (newProgress > 10) {
            currentStepText = "Analyzing search results...";
            currentStepTools = ["Data Analyzer", "Content Parser"];
          }
          if (newProgress > 30) {
            currentStepText = "Gathering additional sources...";
            currentStepTools = ["Source Crawler", "Link Validator"];
          }
          if (newProgress > 50) {
            currentStepText = "Cross-referencing information...";
            currentStepTools = ["Fact Checker", "Cross Referencer"];
          }
          if (newProgress > 70) {
            currentStepText = "Synthesizing information...";
            currentStepTools = ["Content Synthesizer", "Report Builder"];
          }
          if (newProgress > 85) {
            currentStepText = "Formatting research report...";
            currentStepTools = ["Markdown Formatter", "Citation Manager"];
          }
          
          // Update the last step in thinking stream to reflect current status
          if (newThinking.length > 0) {
            newThinking[newThinking.length - 1] = {
              text: currentStepText,
              tools: currentStepTools
            };
          }
          
          return { ...x, progress: newProgress, currentStep: currentStepText, thinkingStream: newThinking };
        }
        return x;
      }));
    }, 1000);

    try {
      const res = await runAgent(item.prompt, item.agent_id);
      clearInterval(progressInterval);
      
      setInbox((prev) => prev.map((x) => {
        if (x.id === id) {
          // Combine simulated progress with actual thinking steps from backend
          // Filter out any commentary-related steps from the backend
          const filteredBackendSteps = (res.thinking_steps || []).filter(step => {
            const stepText = typeof step === 'string' ? step : step.text;
            const commentaryKeywords = ['commentary', 'channel', 'message', 'end'];
            return !commentaryKeywords.some(keyword => 
              stepText.toLowerCase().includes(keyword.toLowerCase())
            );
          });
          
          const finalThinkingStream = [
            ...(x.thinkingStream || []),
            ...filteredBackendSteps,
            { text: "✅ Research completed successfully!", tools: ["Report Finalizer"] },
            { text: "📊 Generated comprehensive report with citations", tools: ["Citation Generator", "Report Publisher"] }
          ];
          
          return { 
            ...x, 
            status: "done", 
            result: res.report || res.assistant_message,
            progress: 100,
            currentStep: "Research complete!",
            thinkingStream: finalThinkingStream
          };
        }
        return x;
      }));
    } catch (e: any) {
      clearInterval(progressInterval);
      setInbox((prev) => prev.map((x) => (x.id === id ? { 
        ...x, 
        status: "error", 
        error: e?.message || "Failed",
        currentStep: "Error occurred",
        thinkingStream: [...(x.thinkingStream || []), { text: "❌ An error occurred during research", tools: ["Error Handler"] }]
      } : x)));
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
          <h2 className="mb-3 text-lg font-medium">Research Results</h2>
          <div className="grid gap-6">
            {inbox.map((m) => (
              <Card key={m.id} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-muted-foreground capitalize">{m.agent_id} Agent</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      {m.status === "running" && (
                        <>
                          <Loader2 className="h-3 w-3 animate-spin text-amber-600" />
                          <span className="text-amber-600 font-medium">Researching...</span>
                        </>
                      )}
                      {m.status === "done" && (
                        <>
                          <CheckCircle className="h-3 w-3 text-green-600" />
                          <span className="text-green-600 font-medium">Complete</span>
                        </>
                      )}
                      {m.status === "error" && (
                        <>
                          <AlertCircle className="h-3 w-3 text-red-600" />
                          <span className="text-red-600 font-medium">Error</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    "{m.prompt}"
                  </div>
                </CardHeader>
                
                <CardContent className="pt-0">
                  {/* Research Process and Tools - Always show at top */}
                  <div className="space-y-4 mb-6">
                    {m.status === "running" && (m.thinkingStream || []).length > 0 && (
                      <Collapsible 
                        title={`Current Research Step`}
                        defaultOpen={true}
                        className="border-2 border-blue-200 dark:border-blue-800"
                        titleClassName="text-blue-700 dark:text-blue-400"
                      >
                        <div className="p-4">
                          {(() => {
                            const currentStep = (m.thinkingStream || [])[(m.thinkingStream || []).length - 1];
                            if (!currentStep) return null;
                            
                            // Filter out commentary-related steps
                            const stepText = typeof currentStep === 'string' ? currentStep : currentStep.text;
                            const commentaryKeywords = ['commentary', 'channel', 'message', 'end'];
                            if (commentaryKeywords.some(keyword => stepText.toLowerCase().includes(keyword.toLowerCase()))) {
                              return null; // Don't show commentary steps
                            }
                            
                            return (
                              <div className="flex items-start gap-3">
                                <span className="font-mono text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded min-w-[2rem] text-center">
                                  {String((m.thinkingStream || []).length).padStart(2, '0')}
                                </span>
                                <div className="flex-1">
                                  <div className="text-sm text-gray-700 dark:text-gray-300 mb-3 font-medium">
                                    {typeof currentStep === 'string' ? currentStep : currentStep.text}
                                  </div>
                                                                      {typeof currentStep === 'object' && currentStep.tools && (
                                      <div className="flex flex-wrap gap-2">
                                        {currentStep.tools.map((tool, toolIndex) => (
                                          <Button 
                                            key={toolIndex}
                                            variant="outline" 
                                            size="sm" 
                                            className="h-7 rounded-full px-3 py-1 text-xs"
                                          >
                                            <Cpu className="h-3 w-3 mr-1" />
                                            {tool}
                                          </Button>
                                        ))}
                                      </div>
                                    )}
                                </div>
                              </div>
                            );
                          })()}
                        </div>
                      </Collapsible>
                    )}

                    {(m.status === "done" || m.status === "error") && (m.thinkingStream || []).length > 0 && (
                      <Collapsible 
                        title={`Research process completed (${(m.thinkingStream || []).length} steps)`}
                        defaultOpen={false}
                        className={`border-2 ${m.status === "done" ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}
                        titleClassName={m.status === "done" ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}
                      >
                        <ScrollArea className="max-h-96 pt-2">
                          <div className="space-y-3">
                            {(m.thinkingStream || [])
                              .filter(step => {
                                // Filter out commentary-related steps
                                const stepText = typeof step === 'string' ? step : step.text;
                                const commentaryKeywords = ['commentary', 'channel', 'message', 'end'];
                                return !commentaryKeywords.some(keyword => 
                                  stepText.toLowerCase().includes(keyword.toLowerCase())
                                );
                              })
                              .map((step, index) => (
                              <div 
                                key={index} 
                                className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
                              >
                                <div className="flex items-start gap-3">
                                  <span className="font-mono text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded min-w-[2rem] text-center">
                                    {String(index + 1).padStart(2, '0')}
                                  </span>
                                  <div className="flex-1">
                                    <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                                      {typeof step === 'string' ? step : step.text}
                                    </div>
                                    {typeof step === 'object' && step.tools && (
                                      <div className="flex flex-wrap gap-2">
                                        {step.tools.map((tool, toolIndex) => (
                                          <Button 
                                            key={toolIndex}
                                            variant="outline" 
                                            size="sm" 
                                            className="h-7 rounded-full px-3 py-1 text-xs"
                                          >
                                            <Cpu className="h-3 w-3 mr-1" />
                                            {tool}
                                          </Button>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </Collapsible>
                    )}
                  </div>

                  {m.status === "running" && (
                    <div className="space-y-4">
                      {/* Progress section - always visible */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Brain className="h-4 w-4 animate-pulse" />
                            <span className="font-medium">{m.currentStep}</span>
                          </div>
                          <span className="text-xs text-muted-foreground font-mono">
                            {Math.round(m.progress || 0)}%
                          </span>
                        </div>
                        <Progress value={m.progress || 0} className="h-2" />
                      </div>
                    </div>
                  )}
                  
                  {m.result && (
                    <div className="space-y-4">
                      {/* Main result display */}
                      <ScrollArea className="max-h-[600px] rounded-lg border bg-white dark:bg-gray-900 p-6">
                        <MarkdownRenderer content={m.result} />
                      </ScrollArea>

                    </div>
                  )}
                  
                  {m.error && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-medium text-red-700 dark:text-red-400">
                        <AlertCircle className="h-4 w-4" />
                        Error
                      </div>
                      <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-700 dark:text-red-400">
                        {m.error}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
            {inbox.length === 0 && (
              <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                  <Brain className="h-12 w-12 text-muted-foreground/50 mb-4" />
                  <h3 className="text-lg font-medium text-muted-foreground mb-2">No research requests yet</h3>
                  <p className="text-sm text-muted-foreground">
                    Ask the research agent a question to get started with comprehensive AI-powered research.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
