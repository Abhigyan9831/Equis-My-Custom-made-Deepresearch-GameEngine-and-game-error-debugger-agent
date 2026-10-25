"use client";
import { useState } from "react";
import { Plus, MessageSquare, Search, Settings, ChevronRight, Sparkles, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface Thread {
  id: string;
  title: string;
  preview: string;
  time: string;
  active?: boolean;
}

const THREADS: Thread[] = [
  { id: "1", title: "Q3 Risk Analysis", preview: "Summarize the attached report…", time: "2:14 PM", active: true },
  { id: "2", title: "Background Replacement", preview: "3 workflows being built…", time: "Yesterday" },
  { id: "3", title: "Market Research", preview: "Find competitors in the SaaS space", time: "Mon" },
  { id: "4", title: "Code Review", preview: "Review my TypeScript component", time: "Sun" },
  { id: "5", title: "Email Draft", preview: "Draft a follow-up to the investor", time: "Fri" },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
  onNewChat?: () => void;
}

export function Sidebar({ collapsed, onToggle, onNewChat }: SidebarProps) {
  const [search, setSearch] = useState("");
  const filtered = THREADS.filter(
    (t) =>
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.preview.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside
      className={cn(
        "flex flex-col h-full glass-strong border-r border-white/[0.07] transition-all duration-300 relative",
        collapsed ? "w-14" : "w-60"
      )}
    >
      {/* Logo / header */}
      <div className="flex items-center gap-2.5 h-14 px-3.5 border-b border-white/[0.06] shrink-0">
        <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shrink-0">
          <Sparkles size={14} className="text-white" />
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-white/85 tracking-tight">Agent UI</span>
        )}
        <button
          onClick={onToggle}
          className="ml-auto p-1 rounded-md hover:bg-white/[0.06] text-white/25 hover:text-white/50 transition-all"
        >
          <ChevronRight size={13} className={cn("transition-transform", !collapsed && "rotate-180")} />
        </button>
      </div>

      {!collapsed && (
        <>
          {/* New chat */}
          <div className="p-2.5 border-b border-white/[0.05] shrink-0">
            <button
              onClick={onNewChat}
              className="flex items-center gap-2 w-full h-8 px-3 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/[0.08] hover:border-white/[0.14] text-white/60 hover:text-white/85 text-xs font-medium transition-all"
            >
              <Plus size={13} />
              New chat
            </button>
          </div>

          {/* Search */}
          <div className="px-2.5 pt-2.5 pb-1 shrink-0">
            <div className="relative">
              <Search size={11} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-white/25" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search chats…"
                className="w-full h-7 pl-7 pr-3 bg-white/[0.04] border border-white/[0.07] rounded-lg text-xs text-white/70 placeholder:text-white/25 outline-none focus:border-white/[0.14] focus:bg-white/[0.06] transition-all"
              />
            </div>
          </div>

          {/* Label */}
          <div className="flex items-center gap-1.5 px-3.5 py-1.5 shrink-0">
            <Clock size={10} className="text-white/20" />
            <span className="text-[10px] uppercase tracking-wider text-white/20 font-medium">Recent</span>
          </div>

          {/* Threads */}
          <div className="flex-1 overflow-y-auto px-2 space-y-0.5 pb-2">
            {filtered.map((thread) => (
              <button
                key={thread.id}
                className={cn(
                  "w-full text-left px-2.5 py-2 rounded-xl transition-all",
                  thread.active
                    ? "bg-white/[0.08] border border-white/[0.1]"
                    : "hover:bg-white/[0.04] border border-transparent"
                )}
              >
                <div className="flex items-baseline gap-2">
                  <p className={cn(
                    "text-xs font-medium truncate flex-1",
                    thread.active ? "text-white/90" : "text-white/55"
                  )}>
                    {thread.title}
                  </p>
                  <span className="text-[10px] text-white/25 shrink-0">{thread.time}</span>
                </div>
                <p className="text-[11px] text-white/28 truncate mt-0.5">{thread.preview}</p>
              </button>
            ))}
          </div>
        </>
      )}

      {collapsed && (
        <div className="flex-1 flex flex-col items-center gap-1.5 pt-2 pb-2">
          <button onClick={onNewChat} className="p-2 rounded-xl hover:bg-white/[0.07] text-white/30 hover:text-white/60 transition-all">
            <Plus size={16} />
          </button>
          {THREADS.slice(0, 5).map((t) => (
            <button key={t.id} className={cn("p-2 rounded-xl transition-all", t.active ? "bg-white/[0.1] text-white/80" : "hover:bg-white/[0.06] text-white/25 hover:text-white/50")}>
              <MessageSquare size={15} />
            </button>
          ))}
        </div>
      )}

      {/* Bottom nav */}
      <div className="border-t border-white/[0.06] p-2 shrink-0">
        <button className={cn(
          "flex items-center gap-2.5 w-full px-2.5 py-2 rounded-xl hover:bg-white/[0.06] text-white/35 hover:text-white/65 transition-all",
          collapsed && "justify-center"
        )}>
          <Settings size={14} />
          {!collapsed && <span className="text-xs font-medium">Settings</span>}
        </button>
      </div>
    </aside>
  );
}
