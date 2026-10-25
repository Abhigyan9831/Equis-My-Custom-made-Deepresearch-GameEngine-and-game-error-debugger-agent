"use client";
import { Search, Code2, Zap, Globe, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type StatusType = "thinking" | "searching" | "running" | "generating" | "browsing";

interface StatusPillProps {
  type: StatusType;
  label?: string;
  active?: boolean;
}

const statusConfig: Record<StatusType, { icon: React.ReactNode; defaultLabel: string; color: string }> = {
  thinking: {
    icon: <Loader2 size={11} className="spin" />,
    defaultLabel: "Thinking…",
    color: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  },
  searching: {
    icon: <Search size={11} />,
    defaultLabel: "Searching the web…",
    color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  },
  running: {
    icon: <Code2 size={11} />,
    defaultLabel: "Using script…",
    color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  },
  generating: {
    icon: <Zap size={11} />,
    defaultLabel: "Generating…",
    color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  },
  browsing: {
    icon: <Globe size={11} />,
    defaultLabel: "Browsing…",
    color: "text-green-400 bg-green-500/10 border-green-500/20",
  },
};

export function StatusPill({ type, label, active = true }: StatusPillProps) {
  const config = statusConfig[type];
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border animate-in",
        config.color,
        !active && "opacity-40"
      )}
    >
      {config.icon}
      {label || config.defaultLabel}
    </div>
  );
}

export function StatusGroup({ statuses }: { statuses: { type: StatusType; label?: string }[] }) {
  return (
    <div className="flex flex-col gap-1.5 my-2 animate-in">
      {statuses.map((s, i) => (
        <StatusPill key={i} type={s.type} label={s.label} />
      ))}
    </div>
  );
}
