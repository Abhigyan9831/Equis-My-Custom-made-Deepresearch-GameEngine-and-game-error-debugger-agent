"use client";
import { useRef, useState, KeyboardEvent } from "react";
import {
  Paperclip, Mic, ArrowUp, Square, Plus, Settings2, ChevronDown, Zap, Search, Code2
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ComposerProps {
  onSend?: (message: string) => void;
  isGenerating?: boolean;
  onStop?: () => void;
  placeholder?: string;
  model?: string;
  tokenCount?: number;
  tokenLimit?: number;
}

const MODELS = [
  { id: "gpt-4o", label: "GPT-4o" },
  { id: "claude-3-5-sonnet", label: "Claude 3.5" },
  { id: "gemini-pro", label: "Gemini Pro" },
];

export function Composer({
  onSend,
  isGenerating,
  onStop,
  placeholder = "Ask anything, or type / for commands…",
  model = "GPT-4o",
  tokenCount = 128,
  tokenLimit = 8192,
}: ComposerProps) {
  const [value, setValue] = useState("");
  const [showModels, setShowModels] = useState(false);
  const [selectedModel, setSelectedModel] = useState(model);
  const [showCommands, setShowCommands] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === "/" && value === "") {
      setShowCommands(true);
    } else {
      setShowCommands(false);
    }
  };

  const handleSend = () => {
    if (!value.trim() || isGenerating) return;
    onSend?.(value.trim());
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleInput = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  };

  const tokenPct = Math.round((tokenCount / tokenLimit) * 100);

  const SLASH_COMMANDS = [
    { cmd: "/summarize", desc: "Condense the current thread", icon: <Search size={13} /> },
    { cmd: "/draft-email", desc: "Turn this into an email", icon: <Zap size={13} /> },
    { cmd: "/brainstorm", desc: "Generate fresh ideas", icon: <Zap size={13} /> },
    { cmd: "/analyze", desc: "Break down the attached data", icon: <Code2 size={13} /> },
  ];

  return (
    <div className="relative">
      {/* Slash commands */}
      {showCommands && (
        <div className="absolute bottom-full left-0 right-0 mb-2 rounded-xl glass-strong border border-white/[0.1] overflow-hidden animate-in z-50 shadow-2xl">
          {SLASH_COMMANDS.map((c) => (
            <button
              key={c.cmd}
              onClick={() => { setValue(c.cmd + " "); setShowCommands(false); textareaRef.current?.focus(); }}
              className="flex items-center gap-3 w-full px-4 py-3 hover:bg-white/[0.05] text-left transition-colors first:rounded-t-xl last:rounded-b-xl"
            >
              <span className="text-white/40 shrink-0">{c.icon}</span>
              <div>
                <p className="text-sm font-medium text-white/80">{c.cmd}</p>
                <p className="text-xs text-white/35">{c.desc}</p>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Model picker */}
      {showModels && (
        <div className="absolute bottom-full left-0 mb-2 rounded-xl glass-strong border border-white/[0.1] overflow-hidden animate-in z-50 shadow-2xl min-w-[160px]">
          {MODELS.map((m) => (
            <button
              key={m.id}
              onClick={() => { setSelectedModel(m.label); setShowModels(false); }}
              className={cn(
                "flex items-center gap-2 w-full px-4 py-2.5 hover:bg-white/[0.05] text-left transition-colors",
                selectedModel === m.label && "bg-blue-500/10 text-blue-400"
              )}
            >
              <span className={cn("text-xs font-medium", selectedModel === m.label ? "text-blue-400" : "text-white/65")}>
                {m.label}
              </span>
            </button>
          ))}
        </div>
      )}

      <div className={cn(
        "rounded-2xl glass-strong border transition-all",
        isGenerating ? "border-blue-500/25 glow-blue" : "border-white/[0.1] hover:border-white/[0.16] focus-within:border-white/[0.2]"
      )}>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => { setValue(e.target.value); handleInput(); }}
          onKeyDown={handleKeyDown}
          placeholder={isGenerating ? "Generating…" : placeholder}
          disabled={isGenerating}
          rows={1}
          className="w-full bg-transparent px-4 pt-3.5 pb-1 text-sm text-white/85 placeholder:text-white/25 outline-none resize-none leading-relaxed disabled:opacity-50"
        />

        <div className="flex items-center gap-2 px-3 pb-3 pt-1">
          {/* Left actions */}
          <button className="flex items-center justify-center w-7 h-7 rounded-lg hover:bg-white/[0.07] text-white/30 hover:text-white/60 transition-all">
            <Plus size={14} />
          </button>
          <button className="flex items-center justify-center w-7 h-7 rounded-lg hover:bg-white/[0.07] text-white/30 hover:text-white/60 transition-all">
            <Settings2 size={14} />
          </button>
          <button
            onClick={() => setShowModels((v) => !v)}
            className="flex items-center gap-1.5 h-7 px-2.5 rounded-lg hover:bg-white/[0.07] text-white/40 hover:text-white/70 transition-all text-xs font-medium"
          >
            <Zap size={11} className="text-blue-400" />
            {selectedModel}
            <ChevronDown size={10} />
          </button>

          {/* Right */}
          <div className="flex-1" />

          <div className="flex items-center gap-1 mr-1">
            <div className={cn(
              "text-[10px] tabular-nums font-medium",
              tokenPct > 80 ? "text-amber-400" : "text-white/25"
            )}>
              {tokenCount} / {tokenLimit > 1000 ? `${Math.round(tokenLimit / 1000)}K` : tokenLimit}
            </div>
            <div className="w-10 h-0.5 rounded-full bg-white/[0.08] overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", tokenPct > 80 ? "bg-amber-400" : "bg-white/20")}
                style={{ width: `${tokenPct}%` }}
              />
            </div>
          </div>

          <button className="flex items-center justify-center w-7 h-7 rounded-lg hover:bg-white/[0.07] text-white/30 hover:text-white/60 transition-all">
            <Mic size={14} />
          </button>
          <button className="flex items-center justify-center w-7 h-7 rounded-lg hover:bg-white/[0.07] text-white/30 hover:text-white/60 transition-all">
            <Paperclip size={14} />
          </button>

          {isGenerating ? (
            <button
              onClick={onStop}
              className="flex items-center justify-center w-8 h-8 rounded-xl bg-white/[0.1] hover:bg-white/[0.15] text-white/70 hover:text-white transition-all"
            >
              <Square size={12} fill="currentColor" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!value.trim()}
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-xl transition-all",
                value.trim()
                  ? "bg-white text-black hover:bg-white/90"
                  : "bg-white/[0.07] text-white/25 cursor-not-allowed"
              )}
            >
              <ArrowUp size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
