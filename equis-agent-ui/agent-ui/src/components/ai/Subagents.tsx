"use client";
import { useState } from "react";
import { ChevronRight, Bot, CheckCircle2, AlertCircle, Loader2, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToolCall {
  name: string;
  status: "done" | "active" | "error";
  input?: string;
  output?: string;
}

interface SubagentProps {
  name: string;
  description?: string;
  status: "done" | "active" | "pending" | "error";
  toolCalls?: ToolCall[];
  result?: string;
}

export function Subagent({ name, description, status, toolCalls = [], result }: SubagentProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl glass overflow-hidden animate-in my-1.5">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2.5 w-full px-4 py-3 text-left hover:bg-white/[0.03] transition-colors group"
      >
        <div
          className={cn(
            "flex items-center justify-center w-6 h-6 rounded-lg shrink-0",
            status === "done" && "bg-green-500/15",
            status === "active" && "bg-blue-500/15",
            status === "pending" && "bg-white/[0.06]",
            status === "error" && "bg-red-500/15"
          )}
        >
          {status === "done" && <CheckCircle2 size={13} className="text-green-500" />}
          {status === "active" && <Loader2 size={13} className="text-blue-400 spin" />}
          {status === "pending" && <Bot size={13} className="text-white/30" />}
          {status === "error" && <AlertCircle size={13} className="text-red-400" />}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-white/80 truncate">{name}</p>
          {description && (
            <p className="text-[10px] text-white/35 truncate mt-0.5">{description}</p>
          )}
        </div>
        {toolCalls.length > 0 && (
          <span className="text-[10px] text-white/25 shrink-0">{toolCalls.length} calls</span>
        )}
        <ChevronRight
          size={13}
          className={cn(
            "text-white/25 transition-transform duration-200 group-hover:text-white/45 shrink-0",
            open && "rotate-90"
          )}
        />
      </button>

      {open && (
        <div className="border-t border-white/[0.06] animate-in">
          {toolCalls.length > 0 && (
            <div className="px-4 py-3 space-y-2">
              {toolCalls.map((tc, i) => (
                <div key={i} className="flex items-start gap-2.5 animate-in" style={{ animationDelay: `${i * 40}ms` }}>
                  <div className={cn(
                    "mt-0.5 flex items-center justify-center w-4 h-4 rounded shrink-0",
                    tc.status === "done" && "bg-green-500/15",
                    tc.status === "active" && "bg-blue-500/15",
                    tc.status === "error" && "bg-red-500/15"
                  )}>
                    <Wrench size={9} className={cn(
                      tc.status === "done" && "text-green-500",
                      tc.status === "active" && "text-blue-400",
                      tc.status === "error" && "text-red-400"
                    )} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] font-mono text-white/65">{tc.name}</p>
                    {tc.input && (
                      <p className="text-[10px] text-white/30 mt-0.5 font-mono truncate">{tc.input}</p>
                    )}
                    {tc.output && tc.status === "done" && (
                      <p className="text-[10px] text-green-500/60 mt-0.5 font-mono truncate">{tc.output}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          {result && (
            <div className="px-4 pb-3 border-t border-white/[0.04] pt-2.5">
              <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-1.5">Result</p>
              <p className="text-xs text-white/55 leading-relaxed">{result}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface SubagentsProps {
  agents: SubagentProps[];
  title?: string;
}

export function Subagents({ agents, title = "Subagents" }: SubagentsProps) {
  return (
    <div className="animate-in my-2">
      <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-2 px-0.5">{title}</p>
      <div className="space-y-1">
        {agents.map((agent, i) => (
          <Subagent key={i} {...agent} />
        ))}
      </div>
    </div>
  );
}
