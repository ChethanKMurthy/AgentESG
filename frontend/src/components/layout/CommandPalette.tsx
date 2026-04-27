import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../lib/api";
import type { CompanyListResponse } from "../../types/api";

type Cmd = { id: string; label: string; hint?: string; run: () => void };

export function CommandPalette({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<CompanyListResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setQ("");
      setHits(null);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    if (!q.trim()) {
      setHits(null);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const { data } = await api.get<CompanyListResponse>("/companies", {
          params: { search: q, limit: 8 },
        });
        setHits(data);
      } catch {
        setHits(null);
      }
    }, 120);
    return () => clearTimeout(t);
  }, [q, open]);

  const staticCmds: Cmd[] = useMemo(
    () => [
      { id: "dash", label: "Go: Dashboard", hint: "/", run: () => navigate("/") },
      {
        id: "cmp",
        label: "Go: Companies",
        hint: "/companies",
        run: () => navigate("/companies"),
      },
      {
        id: "cpl",
        label: "Go: Copilot",
        hint: "/copilot",
        run: () => navigate("/copilot"),
      },
    ],
    [navigate]
  );

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-[1px] flex items-start justify-center pt-28"
      onClick={onClose}
    >
      <div
        className="panel w-[640px] max-w-[92vw] max-h-[70vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center px-3 h-10 border-b border-line">
          <span className="font-mono text-2xs uppercase text-fg-faint mr-3">
            ⌘K
          </span>
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search companies, run commands…"
            className="bg-transparent flex-1 outline-none text-sm text-fg-bright placeholder:text-fg-faint"
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
            }}
          />
          <button className="chip" onClick={onClose}>
            esc
          </button>
        </div>
        <div className="overflow-auto max-h-[60vh]">
          {!q.trim() && (
            <div className="p-2 space-y-0.5">
              {staticCmds.map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    c.run();
                    onClose();
                  }}
                  className="w-full flex items-center justify-between px-2 py-1.5 rounded-sm hover:bg-ink-750"
                >
                  <span className="text-fg">{c.label}</span>
                  <span className="text-2xs text-fg-faint mono">{c.hint}</span>
                </button>
              ))}
            </div>
          )}
          {q.trim() && hits && (
            <div className="p-2 space-y-0.5">
              {hits.items.length === 0 && (
                <div className="text-fg-faint text-sm p-2">No matches.</div>
              )}
              {hits.items.map((c) => (
                <button
                  key={c.company_id}
                  onClick={() => {
                    navigate(`/companies/${c.company_id}`);
                    onClose();
                  }}
                  className="w-full flex items-center justify-between px-2 py-1.5 rounded-sm hover:bg-ink-750"
                >
                  <span className="text-fg">{c.company_name}</span>
                  <span className="text-2xs text-fg-faint mono">
                    {c.country} · {c.sector}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
