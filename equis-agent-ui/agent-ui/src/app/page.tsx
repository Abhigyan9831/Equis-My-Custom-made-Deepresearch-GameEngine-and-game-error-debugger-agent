"use client";
import { useState, useRef, useEffect } from "react";
import { Sidebar } from "@/components/ai/Sidebar";
import { Message } from "@/components/ai/Message";
import { ChainOfThought } from "@/components/ai/ChainOfThought";
import { Reasoning } from "@/components/ai/Reasoning";
import { Plan } from "@/components/ai/Plan";
import { Queue } from "@/components/ai/Queue";
import { Sources } from "@/components/ai/Sources";
import { Subagents } from "@/components/ai/Subagents";
import { StatusGroup } from "@/components/ai/StatusPill";
import { Composer } from "@/components/ai/Composer";
import { ToolsPanel } from "@/components/ai/ToolsPanel";
import { PanelRight, Sparkles, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Demo data ────────────────────────────────────────────────────────────────

const CHAIN_STEPS = [
  { id: "1", label: "Read the report", detail: "Loaded Q3 Benchmark Report (2.4 MB PDF)", status: "done" as const },
  { id: "2", label: "Cross-reference KPI table", detail: "Ranked deltas across all metrics", status: "done" as const },
  { id: "3", label: "Surface top 3 risks", detail: "Identified retention, CAC, and margin as largest deltas", status: "done" as const },
];

const PLAN_STEPS = [
  { id: "p1", label: "Search for Q3 benchmarks", status: "done" as const, detail: "Found 4 relevant sources" },
  { id: "p2", label: "Extract financial metrics", status: "done" as const, detail: "Parsed 18 KPIs" },
  { id: "p3", label: "Rank risks by impact", status: "active" as const, detail: "Sorting by delta magnitude…" },
  { id: "p4", label: "Write executive summary", status: "pending" as const },
];

const QUEUE_ITEMS = [
  { id: "q1", label: "Background Replacement Workflow", status: "done" as const },
  { id: "q2", label: "Style Transfer Workflow", status: "active" as const, progress: 12 },
  { id: "q3", label: "Product Visualization Workflow", status: "active" as const, progress: 36 },
  { id: "q4", label: "Colour Grading Pass", status: "pending" as const },
];

const SOURCES = [
  { id: "s1", title: "Q3 Benchmark Report", url: "#", domain: "example.com", index: 1 },
  { id: "s2", title: "Industry Outlook 2026", url: "#", domain: "mckinsey.com", index: 2 },
  { id: "s3", title: "SaaS Metrics Guide", url: "#", domain: "openview.com", index: 3 },
];

const SUBAGENTS = [
  {
    name: "Search Agent",
    description: "Searching the web for benchmark data",
    status: "done" as const,
    toolCalls: [
      { name: "web_search", status: "done" as const, input: '"Q3 SaaS benchmarks 2026"', output: "12 results found" },
      { name: "web_fetch", status: "done" as const, input: "https://example.com/report", output: "3.2 KB extracted" },
    ],
    result: "Found 3 relevant benchmark sources covering SaaS retention and CAC metrics.",
  },
  {
    name: "Analysis Agent",
    description: "Cross-referencing and ranking metrics",
    status: "active" as const,
    toolCalls: [
      { name: "run_code", status: "done" as const, input: "pandas.read_csv(data)", output: "DataFrame(18 rows)" },
      { name: "sort_by_delta", status: "active" as const, input: "axis=retention,cac,margin" },
    ],
  },
];

// ─── Turn definition ──────────────────────────────────────────────────────────

interface Turn {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  extras?: ("chain" | "reasoning" | "plan" | "queue" | "sources" | "subagents" | "status")[];
  isStreaming?: boolean;
}

const INITIAL_TURNS: Turn[] = [
  {
    id: "t1",
    role: "user",
    content: "Summarize the attached report and pull out the three biggest risks.",
    timestamp: "2:14 PM",
  },
  {
    id: "t2",
    role: "assistant",
    content: "Here are the three biggest risks from the report: retention is down 8% quarter-over-quarter, acquisition cost rose 22%, and gross margin slipped below target.",
    extras: ["chain", "sources"],
  },
  {
    id: "t3",
    role: "user",
    content: "Now build 3 parallel workflows to address each risk.",
    timestamp: "2:17 PM",
  },
  {
    id: "t4",
    role: "assistant",
    content: "I'm spinning up three parallel workflows to address each risk area. The Background Replacement is already finalizing while Style Transfer and Product Visualization are in progress.",
    extras: ["reasoning", "plan", "queue", "subagents", "status"],
    isStreaming: false,
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function Home() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPanel, setRightPanel] = useState(true);
  const [turns, setTurns] = useState<Turn[]>(INITIAL_TURNS);
  const [isGenerating, setIsGenerating] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  const handleSend = (msg: string) => {
    const userTurn: Turn = { id: `t${Date.now()}`, role: "user", content: msg, timestamp: "Now" };
    setTurns((prev) => [...prev, userTurn]);
    setIsGenerating(true);

    setTimeout(() => {
      const assistantTurn: Turn = {
        id: `t${Date.now() + 1}`,
        role: "assistant",
        content: "I'm processing your request…",
        extras: ["status", "reasoning"],
        isStreaming: true,
      };
      setTurns((prev) => [...prev, assistantTurn]);

      setTimeout(() => {
        setTurns((prev) =>
          prev.map((t) =>
            t.id === assistantTurn.id
              ? { ...t, content: "I've analyzed your request and here's my response. The data shows strong patterns in the metrics you've described.", isStreaming: false, extras: ["chain", "sources"] }
              : t
          )
        );
        setIsGenerating(false);
      }, 2200);
    }, 600);
  };

  return (
    <div className="flex h-screen overflow-hidden mesh-bg">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((v) => !v)}
        onNewChat={() => setTurns([])}
      />

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="flex items-center gap-3 h-14 px-5 border-b border-white/[0.06] shrink-0 glass-strong">
          <div className="flex items-center gap-2.5 flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
              <span className="text-xs text-white/40">Agent active</span>
            </div>
            <div className="w-px h-4 bg-white/[0.08]" />
            <span className="text-sm font-medium text-white/65 truncate">Q3 Risk Analysis</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.07] text-[11px] text-white/40">
              <Sparkles size={10} className="text-purple-400" />
              GPT-4o
            </div>
            <button
              onClick={() => setRightPanel((v) => !v)}
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-lg border transition-all",
                rightPanel
                  ? "bg-blue-500/15 border-blue-500/25 text-blue-400"
                  : "bg-white/[0.04] border-white/[0.07] text-white/35 hover:text-white/60 hover:bg-white/[0.07]"
              )}
            >
              <PanelRight size={13} />
            </button>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* Chat area */}
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <div className="flex-1 overflow-y-auto px-5 py-5 space-y-1">
              {turns.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-4 animate-in">
                  <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/[0.1]">
                    <Layers size={24} className="text-white/40" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-white/50">Start a new conversation</p>
                    <p className="text-xs text-white/25 mt-1">Type a message or use / for commands</p>
                  </div>
                  <div className="flex flex-wrap gap-2 justify-center max-w-sm">
                    {["Summarize my report", "Build 3 workflows", "Search for benchmarks", "Draft an email"].map((s) => (
                      <button
                        key={s}
                        onClick={() => handleSend(s)}
                        className="px-3 py-1.5 rounded-xl glass border border-white/[0.09] text-xs text-white/45 hover:text-white/70 hover:border-white/[0.15] hover:bg-white/[0.05] transition-all"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {turns.map((turn) => (
                <div key={turn.id}>
                  <Message
                    role={turn.role}
                    content={turn.content}
                    timestamp={turn.timestamp}
                    isStreaming={turn.isStreaming}
                    onCopy={() => navigator.clipboard?.writeText(turn.content)}
                  />

                  {turn.role === "assistant" && turn.extras && (
                    <div className="ml-10 mb-2 space-y-1">
                      {turn.extras.includes("status") && (
                        <StatusGroup
                          statuses={[
                            { type: "thinking" },
                            { type: "searching" },
                            { type: "running" },
                          ]}
                        />
                      )}
                      {turn.extras.includes("reasoning") && (
                        <Reasoning
                          content={`The report shows retention declining for two quarters. I cross-referenced the KPI table, ranked deltas, and surfaced the three largest.\n\nRetention delta: -8% QoQ\nCAC delta: +22% QoQ\nGross margin: below target for first time in 6 quarters`}
                          duration="4s"
                          isStreaming={turn.isStreaming}
                        />
                      )}
                      {turn.extras.includes("chain") && (
                        <ChainOfThought
                          steps={CHAIN_STEPS}
                          summary="Analyzed report → ranked risks → surfaced top 3"
                          duration="4s"
                        />
                      )}
                      {turn.extras.includes("plan") && (
                        <Plan steps={PLAN_STEPS} title="Execution Plan" />
                      )}
                      {turn.extras.includes("queue") && (
                        <Queue items={QUEUE_ITEMS} title="3 Workflows being built…" />
                      )}
                      {turn.extras.includes("subagents") && (
                        <Subagents agents={SUBAGENTS} />
                      )}
                      {turn.extras.includes("sources") && (
                        <Sources sources={SOURCES} />
                      )}
                    </div>
                  )}
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            {/* Composer */}
            <div className="px-5 pb-5 pt-2 shrink-0">
              <Composer
                onSend={handleSend}
                isGenerating={isGenerating}
                onStop={() => setIsGenerating(false)}
                tokenCount={1243}
                tokenLimit={8192}
              />
              <p className="text-center text-[10px] text-white/18 mt-2.5">
                AI can make mistakes. Verify important information.
              </p>
            </div>
          </div>

          {/* Right panel */}
          {rightPanel && (
            <aside className="w-72 shrink-0 border-l border-white/[0.06] overflow-y-auto px-4 py-4 space-y-4 glass-strong">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-3">Tools</p>
                <ToolsPanel />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-3">Context</p>
                <div className="rounded-xl glass p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-white/45">Context used</span>
                    <span className="text-xs font-mono text-white/55">1.2K / 8K</span>
                  </div>
                  <div className="h-1 rounded-full bg-white/[0.07] overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 w-[15%]" />
                  </div>
                  <p className="text-[10px] text-white/25">85% remaining</p>
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-3">Attached</p>
                <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl glass border border-white/[0.08]">
                  <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-blue-500/15 shrink-0 text-[10px] font-bold text-blue-400">1</div>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-white/70 truncate">Q3 Benchmark Report</p>
                    <p className="text-[10px] text-white/30">example.com · 2.4 MB</p>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-3">Suggestions</p>
                <div className="space-y-1.5">
                  {["Brainstorm ideas", "Draft a summary", "Find competitors"].map((s) => (
                    <button
                      key={s}
                      onClick={() => handleSend(s)}
                      className="flex items-center gap-2 w-full px-3 py-2 rounded-xl glass border border-white/[0.07] hover:border-white/[0.13] hover:bg-white/[0.04] text-xs text-white/45 hover:text-white/70 transition-all text-left"
                    >
                      <Sparkles size={10} className="text-purple-400 shrink-0" />
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}
