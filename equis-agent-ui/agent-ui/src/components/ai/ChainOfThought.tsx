"use client";
import { useState } from "react";
import { ChevronRight, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface Step {
  id: string;
  label: string;
  detail: string;
  status: "done" | "active" | "pending";
}

interface ChainOfThoughtProps {
  steps: Step[];
  summary?: string;
  duration?: string;
  isStreaming?: boolean;
}

export function ChainOfThought({ steps, summary, duration, isStreaming }: ChainOfThoughtProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl overflow-hidden glass my-2 animate-in">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2.5 w-full px-4 py-3 text-left hover:bg-white/[0.03] transition-colors group"
      >
        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-purple-500/20 shrink-0">
          <Sparkles size={11} className="text-purple-400" />
        </span>
        <span className="text-sm font-medium text-white/80 flex-1">
          {isStreaming ? (
            <span className="flex items-center gap-2">
              Thinking
              <span className="flex gap-0.5">
                <span className="w-1 h-1 rounded-full bg-purple-400 dot-1" />
                <span className="w-1 h-1 rounded-full bg-purple-400 dot-2" />
                <span className="w-1 h-1 rounded-full bg-purple-400 dot-3" />
              </span>
            </span>
          ) : (
            summary || `Thought for ${duration || "4s"}`
          )}
        </span>
        <ChevronRight
          size={14}
          className={cn(
            "text-white/30 transition-transform duration-200 group-hover:text-white/50",
            open && "rotate-90"
          )}
        />
      </button>

      {open && (
        <div className="border-t border-white/[0.06] px-4 py-3 space-y-2.5">
          {steps.map((step, i) => (
            <div key={step.id} className="flex gap-3 animate-in" style={{ animationDelay: `${i * 60}ms` }}>
              <div className="flex flex-col items-center pt-0.5 shrink-0">
                <div
                  className={cn(
                    "w-2 h-2 rounded-full mt-1 shrink-0",
                    step.status === "done" && "bg-green-500",
                    step.status === "active" && "bg-blue-400 shadow-[0_0_6px_rgba(59,130,246,0.6)]",
                    step.status === "pending" && "bg-white/20"
                  )}
                />
                {i < steps.length - 1 && (
                  <div className="w-px flex-1 mt-1 bg-white/[0.07] min-h-[16px]" />
                )}
              </div>
              <div className="pb-2">
                <p className="text-xs font-medium text-white/70">{step.label}</p>
                <p className="text-xs text-white/38 mt-0.5 leading-relaxed">{step.detail}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
