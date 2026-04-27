import { useRagStats } from "../../hooks/api";

export function Topbar({ onOpenPalette }: { onOpenPalette: () => void }) {
  const { data } = useRagStats();
  return (
    <header className="h-10 shrink-0 border-b border-line bg-ink-850 flex items-center justify-between px-3">
      <div className="flex items-center gap-3">
        <div className="font-mono text-2xs uppercase tracking-widest text-fg-faint">
          live
        </div>
        <div className="h-1.5 w-1.5 rounded-full bg-accent" />
        <div className="text-fg-muted text-xs mono">
          rag:
          <span className={data?.ready ? "text-accent ml-1" : "text-accent-amber ml-1"}>
            {data?.ready ? "ready" : "idle"}
          </span>
          {data?.chunks !== undefined && (
            <span className="text-fg-faint ml-2">
              {data.documents} docs · {data.chunks} chunks · {data.dim}d
            </span>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenPalette}
          className="chip hover:bg-ink-750 transition-colors duration-fast"
        >
          <span>search / nav</span>
          <span className="kbd ml-2">⌘K</span>
        </button>
      </div>
    </header>
  );
}
