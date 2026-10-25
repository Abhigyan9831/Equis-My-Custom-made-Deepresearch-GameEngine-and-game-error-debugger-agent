"use client";
import { useState } from "react";
import { ChevronDown, CheckCheck, Clock, Loader2, ListChecks } from "lucide-react";
import { cn } from "@/lib/utils";

interface QueueItem {
  id: string;
  label: string;
  status: "done" | "active" | "pending";
  progress?: number;
}

interface QueueProps {
  items: QueueItem[];
  title?: string;
}

export function Queue({ items, title = "Queue" }: QueueProps) {
  const [showDone, setShowDone] = useState(false);
  const todo = items.filter((i) => i.status !== "done");
  const done = items.filter((i) => i.status === "done");

  return (
    <div className="rounded-xl glass overflow-hidden animate-in my-2">
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-white/[0.06]">
        <ListChecks size={13} className="text-amber-400 shrink-0" />
        <span className="text-xs font-medium text-white/70 flex-1">{title}</span>
        <div className="flex items-center gap-1">
          <span className="px-1.5 py-0.5 rounded-md bg-amber-500/15 text-amber-400 text-[10px] font-medium tabular-nums">
            {todo.length} left
          </span>
          {done.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-md bg-green-500/10 text-green-500 text-[10px] font-medium tabular-nums">
              {done.length} done
            </span>
          )}
        </div>
      </div>

      <div className="px-3 py-2 space-y-1">
        {todo.map((item, i) => (
          <QueueRow key={item.id} item={item} index={i} />
        ))}
      </div>

      {done.length > 0 && (
        <div className="border-t border-white/[0.06]">
          <button
            onClick={() => setShowDone((v) => !v)}
            className="flex items-center gap-2 w-full px-4 py-2 text-left hover:bg-white/[0.03] transition-colors"
          >
            <CheckCheck size={11} className="text-green-500" />
            <span className="text-[10px] text-white/35 flex-1">{done.length} completed</span>
            <ChevronDown size={11} className={cn("text-white/25 transition-transform", showDone && "rotate-180")} />
          </button>
          {showDone && (
            <div className="px-3 pb-2 space-y-1">
              {done.map((item, i) => (
                <QueueRow key={item.id} item={item} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function QueueRow({ item, index }: { item: QueueItem; index: number }) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 px-1 py-1.5 rounded-lg animate-in",
        item.status === "active" && "bg-blue-500/[0.07]"
      )}
      style={{ animationDelay: `${index * 40}ms` }}
    >
      <div className="shrink-0">
        {item.status === "done" && <CheckCheck size={12} className="text-green-500" />}
        {item.status === "active" && <Loader2 size={12} className="text-blue-400 spin" />}
        {item.status === "pending" && <Clock size={12} className="text-white/25" />}
      </div>
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-xs truncate",
            item.status === "done" && "text-white/30 line-through decoration-white/20",
            item.status === "active" && "text-white/80",
            item.status === "pending" && "text-white/40"
          )}
        >
          {item.label}
        </p>
        {item.status === "active" && item.progress !== undefined && (
          <div className="mt-1 h-0.5 rounded-full bg-white/[0.08] overflow-hidden">
            <div
              className="h-full rounded-full bg-blue-400 transition-all duration-500"
              style={{ width: `${item.progress}%` }}
            />
          </div>
        )}
      </div>
      {item.status === "active" && item.progress !== undefined && (
        <span className="text-[10px] text-blue-400 tabular-nums shrink-0">{item.progress}%</span>
      )}
    </div>
  );
}
