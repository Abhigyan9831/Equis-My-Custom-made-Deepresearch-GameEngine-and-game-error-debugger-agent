"use client";
import { useState } from "react";
import { ChevronDown, ChevronUp, BrainCircuit } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReasoningProps {
  content: string;
  isStreaming?: boolean;
  duration?: string;
}

export function Reasoning({ content, isStreaming, duration }: ReasoningProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl glass overflow-hidden animate-in my-1.5">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-2.5 w-full px-4 py-2.5 text-left hover:bg-white/[0.03] transition-colors group"
      >
        <BrainCircuit size={13} className="text-violet-400 shrink-0" />
        <span className="text-xs font-medium text-white/60 flex-1">
          {isStreaming ? (
            <span className="flex items-center gap-1.5">
              Reasoning
              <span className="flex gap-0.5">
                <span className="w-1 h-1 rounded-full bg-violet-400 dot-1" />
                <span className="w-1 h-1 rounded-full bg-violet-400 dot-2" />
                <span className="w-1 h-1 rounded-full bg-violet-400 dot-3" />
              </span>
            </span>
          ) : (
            `Thought for ${duration || "4s"}`
          )}
        </span>
        {expanded ? (
          <ChevronUp size={12} className="text-white/25 group-hover:text-white/40" />
        ) : (
          <ChevronDown size={12} className="text-white/25 group-hover:text-white/40" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-white/[0.06] px-4 py-3 animate-in">
          <p className="text-xs leading-relaxed text-white/45 font-mono whitespace-pre-wrap">
            {content}
            {isStreaming && <span className="cursor ml-0.5" />}
          </p>
        </div>
      )}
    </div>
  );
}
