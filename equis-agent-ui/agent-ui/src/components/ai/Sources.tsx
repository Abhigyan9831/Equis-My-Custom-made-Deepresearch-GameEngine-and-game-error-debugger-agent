"use client";
import { ExternalLink, Globe } from "lucide-react";

interface Source {
  id: string;
  title: string;
  url: string;
  domain: string;
  favicon?: string;
  index: number;
}

interface SourcesProps {
  sources: Source[];
}

export function Sources({ sources }: SourcesProps) {
  if (!sources.length) return null;

  return (
    <div className="animate-in my-2">
      <p className="text-[10px] uppercase tracking-wider text-white/25 font-medium mb-2 px-0.5">Sources</p>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, i) => (
          <a
            key={src.id}
            href={src.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg glass border border-white/[0.08] hover:border-white/[0.15] hover:bg-white/[0.05] transition-all group max-w-[200px]"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            <span className="flex items-center justify-center w-4 h-4 rounded-full bg-white/10 shrink-0 text-[9px] font-mono text-white/50">
              {src.index}
            </span>
            <Globe size={10} className="text-white/25 shrink-0" />
            <span className="text-xs text-white/55 truncate group-hover:text-white/75 transition-colors">
              {src.title}
            </span>
            <ExternalLink size={9} className="text-white/20 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
        ))}
      </div>
    </div>
  );
}
