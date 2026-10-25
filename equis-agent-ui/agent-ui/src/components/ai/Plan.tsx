"use client";
import { CheckCircle2, Circle, Loader2, ListTodo } from "lucide-react";
import { cn } from "@/lib/utils";

interface PlanStep {
  id: string;
  label: string;
  status: "done" | "active" | "pending";
  detail?: string;
}

interface PlanProps {
  steps: PlanStep[];
  title?: string;
}

export function Plan({ steps, title = "Plan" }: PlanProps) {
  const done = steps.filter((s) => s.status === "done").length;
  const pct = Math.round((done / steps.length) * 100);

  return (
    <div className="rounded-xl glass overflow-hidden animate-in my-2">
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-white/[0.06]">
        <ListTodo size={13} className="text-cyan-400 shrink-0" />
        <span className="text-xs font-medium text-white/70 flex-1">{title}</span>
        <span className="text-xs text-white/35 tabular-nums">{done}/{steps.length}</span>
        <div className="w-16 h-1 rounded-full bg-white/[0.08] overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 progress-fill"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="px-4 py-3 space-y-2">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-start gap-3 animate-in" style={{ animationDelay: `${i * 50}ms` }}>
            <div className="mt-0.5 shrink-0">
              {step.status === "done" && <CheckCircle2 size={14} className="text-green-500" />}
              {step.status === "active" && <Loader2 size={14} className="text-blue-400 spin" />}
              {step.status === "pending" && <Circle size={14} className="text-white/20" />}
            </div>
            <div className="flex-1 min-w-0">
              <p
                className={cn(
                  "text-xs font-medium",
                  step.status === "done" && "text-white/45 line-through decoration-white/25",
                  step.status === "active" && "text-white/85",
                  step.status === "pending" && "text-white/35"
                )}
              >
                {step.label}
              </p>
              {step.detail && step.status !== "pending" && (
                <p className="text-xs text-white/30 mt-0.5">{step.detail}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
