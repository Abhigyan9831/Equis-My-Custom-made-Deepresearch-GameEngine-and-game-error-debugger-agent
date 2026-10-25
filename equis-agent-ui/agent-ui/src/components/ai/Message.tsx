"use client";
import { Copy, RotateCcw, ThumbsUp, ThumbsDown, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";

interface MessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
  onCopy?: () => void;
  onRegenerate?: () => void;
  onEdit?: () => void;
}

export function Message({ role, content, timestamp, isStreaming, onCopy, onRegenerate, onEdit }: MessageProps) {
  if (role === "user") {
    return (
      <div className="flex justify-end mb-4 animate-in group">
        <div className="max-w-[75%]">
          <div className="rounded-2xl rounded-br-md px-4 py-3 bg-white/[0.08] border border-white/[0.1]">
            <p className="text-sm text-white/88 leading-relaxed whitespace-pre-wrap">{content}</p>
          </div>
          <div className="flex items-center justify-end gap-2 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            {timestamp && <span className="text-[10px] text-white/25">{timestamp}</span>}
            <button onClick={onCopy} className="p-1 rounded hover:bg-white/[0.06] text-white/25 hover:text-white/50 transition-all">
              <Copy size={10} />
            </button>
            <button onClick={onEdit} className="p-1 rounded hover:bg-white/[0.06] text-white/25 hover:text-white/50 transition-all">
              <Pencil size={10} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 mb-5 animate-in group">
      <div className="flex items-center justify-center w-7 h-7 rounded-xl bg-gradient-to-br from-blue-500/30 to-purple-500/30 border border-white/[0.1] shrink-0 mt-0.5">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M8 2L14 8L8 14L2 8Z" fill="url(#grad)" />
          <defs>
            <linearGradient id="grad" x1="2" y1="2" x2="14" y2="14" gradientUnits="userSpaceOnUse">
              <stop stopColor="#60A5FA" />
              <stop offset="1" stopColor="#A78BFA" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-sm text-white/82 leading-relaxed whitespace-pre-wrap",
            isStreaming && "after:content-['|'] after:animate-pulse after:text-blue-400 after:ml-0.5"
          )}
        >
          {content}
        </p>
        <div className="flex items-center gap-1 mt-2.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={onCopy} className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/25 hover:text-white/55 transition-all" title="Copy">
            <Copy size={11} />
          </button>
          <button onClick={onRegenerate} className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/25 hover:text-white/55 transition-all" title="Regenerate">
            <RotateCcw size={11} />
          </button>
          <div className="w-px h-3 bg-white/[0.08] mx-0.5" />
          <button className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/25 hover:text-green-400 transition-all" title="Good response">
            <ThumbsUp size={11} />
          </button>
          <button className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/25 hover:text-red-400 transition-all" title="Bad response">
            <ThumbsDown size={11} />
          </button>
        </div>
      </div>
    </div>
  );
}
