import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { Badge } from "./Badge";
import type { RoadmapExplanation } from "../../types/api";

export function Explainer({ explanation }: { explanation: RoadmapExplanation }) {
  const [open, setOpen] = useState(false);
  if (!explanation) return null;
  const { drivers, priority_factors, horizon_rationale, methodology, narrative } =
    explanation;

  return (
    <div className="mt-3">
      <button
        onClick={() => setOpen((o) => !o)}
        className="chip hover:bg-ink-750 transition-colors duration-fast"
        aria-expanded={open}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-br from-accent to-accent-violet" />
        {open ? "hide explanation" : "why this?"}
        <span className="ml-1">{open ? "▾" : "▸"}</span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="mt-2 rounded-xl border border-line bg-gradient-to-b from-white to-ink-750 p-3 space-y-3">
              {narrative && (
                <div>
                  <div className="text-2xs font-mono uppercase tracking-widest text-accent-violet mb-1">
                    Verdant narrative
                  </div>
                  <div className="text-sm text-fg leading-relaxed">
                    {narrative}
                  </div>
                </div>
              )}

              <div>
                <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mb-1">
                  Drivers
                </div>
                <div className="space-y-1.5">
                  {drivers.map((d, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 text-xs p-2 rounded-lg border border-line/80 bg-white"
                    >
                      <Badge tone={d.kind === "rule" ? "info" : "leader"}>
                        {d.kind}
                      </Badge>
                      <Badge tone={d.severity}>{d.severity}</Badge>
                      <div className="min-w-0 flex-1">
                        <div className="font-mono text-2xs text-fg-faint">
                          {d.identifier}
                          {d.metric && (
                            <span className="text-fg-muted ml-1">
                              · {d.metric}
                            </span>
                          )}
                          {d.current !== null && d.current !== undefined && (
                            <span className="text-fg-muted ml-1">
                              · current {format(d.current)}
                            </span>
                          )}
                          {d.target !== null && d.target !== undefined && (
                            <span className="text-fg-muted ml-1">
                              → target {format(d.target)}
                            </span>
                          )}
                        </div>
                        <div className="text-fg text-xs leading-relaxed mt-0.5">
                          {d.description}
                        </div>
                        {d.citations.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {d.citations.map((c) => (
                              <span key={c} className="chip">
                                {c}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                {Object.entries(priority_factors).map(([k, v]) => (
                  <div
                    key={k}
                    className="rounded-lg border border-line/80 bg-white px-2 py-1.5"
                  >
                    <div className="text-2xs font-mono uppercase tracking-wider text-fg-faint">
                      {k.replace(/_/g, " ")}
                    </div>
                    <div className="font-mono text-sm text-fg-bright">
                      {String(v)}
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid md:grid-cols-2 gap-2">
                <div className="rounded-lg border border-line/80 bg-white p-2">
                  <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mb-1">
                    horizon rationale
                  </div>
                  <div className="text-xs text-fg leading-relaxed">
                    {horizon_rationale}
                  </div>
                </div>
                <div className="rounded-lg border border-line/80 bg-white p-2">
                  <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mb-1">
                    methodology
                  </div>
                  <div className="text-xs text-fg leading-relaxed">
                    {methodology}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function format(n: number): string {
  if (Math.abs(n) >= 1000) return n.toLocaleString();
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(2);
}
