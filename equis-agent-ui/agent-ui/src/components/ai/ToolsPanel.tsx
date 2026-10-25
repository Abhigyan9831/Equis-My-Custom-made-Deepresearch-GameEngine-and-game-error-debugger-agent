"use client";
import { useState } from "react";
import { Search, Code2, Image, BookOpen, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface Tool {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
  color: string;
}

const DEFAULT_TOOLS: Tool[] = [
  { id: "web-search", label: "Web search", description: "Search the internet in real-time", icon: <Search size={14} />, enabled: true, color: "blue" },
  { id: "image-gen", label: "Image generation", description: "Generate images from text", icon: <Image size={14} />, enabled: false, color: "purple" },
  { id: "code", label: "Code interpreter", description: "Run and execute code", icon: <Code2 size={14} />, enabled: true, color: "cyan" },
  { id: "research", label: "Deep research", description: "Multi-step research tasks", icon: <BookOpen size={14} />, enabled: false, color: "amber" },
  { id: "actions", label: "Browser actions", description: "Interact with web pages", icon: <Zap size={14} />, enabled: false, color: "green" },
];

const colorMap: Record<string, { icon: string; toggle: string; bg: string }> = {
  blue:   { icon: "text-blue-400",   toggle: "bg-blue-500",   bg: "bg-blue-500/10" },
  purple: { icon: "text-purple-400", toggle: "bg-purple-500", bg: "bg-purple-500/10" },
  cyan:   { icon: "text-cyan-400",   toggle: "bg-cyan-500",   bg: "bg-cyan-500/10" },
  amber:  { icon: "text-amber-400",  toggle: "bg-amber-500",  bg: "bg-amber-500/10" },
  green:  { icon: "text-green-400",  toggle: "bg-green-500",  bg: "bg-green-500/10" },
};

export function ToolsPanel() {
  const [tools, setTools] = useState<Tool[]>(DEFAULT_TOOLS);

  const toggle = (id: string) => {
    setTools((prev) => prev.map((t) => (t.id === id ? { ...t, enabled: !t.enabled } : t)));
  };

  return (
    <div className="rounded-xl glass overflow-hidden animate-in">
      <div className="px-4 py-3 border-b border-white/[0.06]">
        <p className="text-xs font-semibold text-white/70">Tools</p>
        <p className="text-[10px] text-white/30 mt-0.5">Toggle web search, code, image, and deep research</p>
      </div>
      <div className="p-2 space-y-0.5">
        {tools.map((tool) => {
          const colors = colorMap[tool.color];
          return (
            <div
              key={tool.id}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.03] transition-colors"
            >
              <div className={cn("flex items-center justify-center w-7 h-7 rounded-lg shrink-0", colors.bg, colors.icon)}>
                {tool.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white/75">{tool.label}</p>
                <p className="text-[10px] text-white/30 truncate">{tool.description}</p>
              </div>
              <button
                onClick={() => toggle(tool.id)}
                className={cn(
                  "relative w-9 h-5 rounded-full transition-all duration-200 shrink-0",
                  tool.enabled ? colors.toggle : "bg-white/[0.1]"
                )}
              >
                <span
                  className={cn(
                    "absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-200",
                    tool.enabled ? "left-[18px]" : "left-0.5"
                  )}
                />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
