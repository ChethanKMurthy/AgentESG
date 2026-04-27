import { useState } from "react";
import type { Citation as C } from "../../types/api";

export function CitationChip({ c }: { c: C }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="chip chip-active hover:bg-ink-750 transition-colors duration-fast"
        title={c.source}
      >
        [{c.index}] {c.source}
      </button>
      {open && (
        <div className="absolute z-30 mt-1 w-96 max-w-[36rem] panel p-3 text-xs text-fg-muted font-mono leading-relaxed">
          <div className="flex justify-between mb-2">
            <span className="text-fg-bright">[{c.index}] {c.source}</span>
            <span className="text-fg-faint">score {c.score.toFixed(3)}</span>
          </div>
          <div className="whitespace-pre-wrap">{c.snippet}</div>
        </div>
      )}
    </span>
  );
}

export function CitationList({ citations }: { citations: C[] }) {
  if (!citations.length) return <div className="text-fg-faint text-xs">No sources retrieved.</div>;
  return (
    <div className="space-y-2">
      {citations.map((c) => (
        <div key={c.chunk_id} className="border border-line rounded-sm p-2">
          <div className="flex justify-between text-2xs font-mono mb-1">
            <span className="text-fg-bright">[{c.index}] {c.source}</span>
            <span className="text-fg-faint">score {c.score.toFixed(3)}</span>
          </div>
          <div className="text-xs text-fg-muted leading-relaxed">{c.snippet}</div>
        </div>
      ))}
    </div>
  );
}
