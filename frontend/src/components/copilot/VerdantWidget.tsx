import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { VerdantAvatar } from "./VerdantAvatar";
import { useRagStats, useCopilotBrief } from "../../hooks/api";
import { useCompanyContext } from "../../hooks/useCompanyContext";
import { streamCopilot } from "../../lib/stream";
import { CitationList } from "../ui/Citation";
import { SkeletonRows } from "../ui/Skeleton";
import { Badge } from "../ui/Badge";
import type { Citation, CopilotBriefResponse } from "../../types/api";

type Turn =
  | {
      kind: "user";
      text: string;
    }
  | {
      kind: "assistant";
      text: string;
      citations?: Citation[];
      model?: string | null;
      used_llm?: boolean;
      streaming?: boolean;
      mode: "chat" | "brief";
      brief?: CopilotBriefResponse;
      error?: string;
    };

const QUICK_PROMPTS = [
  "Does CSRD apply to a 250-employee EU manufacturer?",
  "Explain ESRS E1 climate disclosures in plain terms.",
  "What counts as Scope 3, and which categories are usually material?",
  "What must a CSRD transition plan include?",
];

const QUICK_PROMPTS_COMPANY = [
  "Brief me on this company's CSRD posture.",
  "Identify the top three ESG risks for this company.",
  "Where is disclosure weakest versus ESRS E1?",
  "Suggest the first 90-day roadmap priorities.",
];

export function VerdantWidget() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"chat" | "brief">("chat");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [expandedSources, setExpandedSources] = useState<Record<number, boolean>>({});
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const rag = useRagStats();
  const { companyId, company } = useCompanyContext();
  const briefMutation = useCopilotBrief();
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 160);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const scrollToBottom = () =>
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: 1e9, behavior: "smooth" });
    }, 30);

  const sendChat = async (q?: string) => {
    const text = (q ?? input).trim();
    if (!text || streaming) return;
    setInput("");
    setTurns((t) => [
      ...t,
      { kind: "user", text },
      { kind: "assistant", text: "", streaming: true, mode: "chat" },
    ]);
    scrollToBottom();
    setStreaming(true);
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    let cites: Citation[] = [];
    let meta: any = {};
    try {
      await streamCopilot(
        { query: text, company_id: companyId },
        {
          onMeta: (m) => {
            meta = m;
          },
          onCitations: (c) => {
            cites = c as Citation[];
            setTurns((t) => {
              const idx = t.length - 1;
              const copy = [...t];
              if (copy[idx]?.kind === "assistant") {
                copy[idx] = { ...copy[idx], citations: cites } as Turn;
              }
              return copy;
            });
          },
          onToken: (delta) => {
            setTurns((t) => {
              const idx = t.length - 1;
              const copy = [...t];
              const last = copy[idx];
              if (last?.kind === "assistant") {
                copy[idx] = { ...last, text: (last.text || "") + delta } as Turn;
              }
              return copy;
            });
          },
        },
        ctrl.signal
      );
      setTurns((t) => {
        const idx = t.length - 1;
        const copy = [...t];
        const last = copy[idx];
        if (last?.kind === "assistant") {
          copy[idx] = {
            ...last,
            streaming: false,
            citations: cites,
            model: meta.model,
            used_llm: meta.used_llm,
          } as Turn;
        }
        return copy;
      });
    } catch (e: any) {
      setTurns((t) => {
        const idx = t.length - 1;
        const copy = [...t];
        const last = copy[idx];
        if (last?.kind === "assistant") {
          copy[idx] = {
            ...last,
            streaming: false,
            error: e?.message || "stream failed",
            text:
              (last.text || "") +
              (last.text ? "" : "Verdant: comms down."),
          } as Turn;
        }
        return copy;
      });
    } finally {
      setStreaming(false);
      abortRef.current = null;
      scrollToBottom();
    }
  };

  const sendBrief = async (q?: string) => {
    const text = (q ?? input).trim();
    if (!text) return;
    setInput("");
    setTurns((t) => [
      ...t,
      { kind: "user", text },
      { kind: "assistant", text: "", streaming: true, mode: "brief" },
    ]);
    scrollToBottom();
    try {
      const res = (await briefMutation.mutateAsync({
        query: text,
        company_id: companyId,
      })) as CopilotBriefResponse;
      setTurns((t) => {
        const idx = t.length - 1;
        const copy = [...t];
        const last = copy[idx];
        if (last?.kind === "assistant") {
          copy[idx] = {
            ...last,
            streaming: false,
            brief: res,
            citations: res.citations,
            model: res.model,
            used_llm: res.used_llm,
            text: res.headline,
          } as Turn;
        }
        return copy;
      });
    } catch (e: any) {
      setTurns((t) => {
        const idx = t.length - 1;
        const copy = [...t];
        const last = copy[idx];
        if (last?.kind === "assistant") {
          copy[idx] = {
            ...last,
            streaming: false,
            error: e?.message || "brief failed",
            text: "Verdant: briefing failed.",
          } as Turn;
        }
        return copy;
      });
    } finally {
      scrollToBottom();
    }
  };

  const onSend = () => (mode === "chat" ? sendChat() : sendBrief());

  const stop = () => abortRef.current?.abort();

  const companyBadge = companyId && company?.company_name;

  return (
    <>
      {/* FAB */}
      <motion.button
        onClick={() => setOpen((o) => !o)}
        aria-label="Open Agent Verdant"
        className="fixed z-[60] bottom-5 right-5 group"
        whileHover={{ y: -2 }}
        whileTap={{ scale: 0.96 }}
        transition={{ type: "spring", stiffness: 400, damping: 25 }}
      >
        <span
          aria-hidden
          className={clsx(
            "absolute inset-0 rounded-full",
            !open && "animate-pulse-soft"
          )}
          style={{
            boxShadow:
              "0 0 0 1px rgba(6,182,212,0.35), 0 0 36px -4px rgba(6,182,212,0.55)",
          }}
        />
        <span className="relative flex items-center gap-2 pl-1 pr-3 py-1 rounded-full bg-white/95 backdrop-blur border border-line shadow-panel">
          <VerdantAvatar size={40} />
          <span className="flex flex-col items-start leading-tight pr-1">
            <span className="text-2xs font-mono uppercase tracking-widest text-fg-faint">
              codename
            </span>
            <span className="text-sm font-semibold text-fg-bright -mt-0.5">
              Verdant
            </span>
          </span>
        </span>
      </motion.button>

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="verdant-panel"
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.97 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className={clsx(
              "fixed z-[70] bottom-24 right-5 w-[420px] max-w-[calc(100vw-2rem)]",
              "h-[620px] max-h-[calc(100vh-7rem)]"
            )}
          >
            <div className="card h-full flex flex-col overflow-hidden">
              {/* Header */}
              <header className="flex items-center justify-between px-3 py-2.5 border-b border-line bg-gradient-to-b from-white to-ink-750 relative">
                <div className="flex items-center gap-2.5 min-w-0">
                  <VerdantAvatar size={36} ring />
                  <div className="leading-tight min-w-0">
                    <div className="text-2xs font-mono uppercase tracking-widest text-fg-faint">
                      codename
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-fg-bright">
                        Agent Verdant
                      </span>
                      <span className="flex items-center gap-1 text-2xs font-mono text-sev-low">
                        <span className="w-1.5 h-1.5 rounded-full bg-sev-low animate-pulse-soft" />
                        on station
                      </span>
                    </div>
                    <div className="text-2xs text-fg-faint font-mono mt-0.5 truncate">
                      {rag.data?.ready
                        ? `corpus: ${rag.data.documents} docs · ${rag.data.chunks} chunks`
                        : "corpus: idle"}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button className="chip" onClick={() => setTurns([])} title="Clear">
                    clear
                  </button>
                  <button
                    className="chip"
                    onClick={() => setOpen(false)}
                    aria-label="Close"
                    title="Close"
                  >
                    ✕
                  </button>
                </div>
              </header>

              {/* Mode switch + context badge */}
              <div className="flex items-center justify-between px-3 py-2 border-b border-line bg-white/80">
                <div className="inline-flex rounded-full border border-line bg-ink-750 p-0.5 text-xs font-mono">
                  <button
                    onClick={() => setMode("chat")}
                    className={clsx(
                      "px-2.5 py-1 rounded-full transition-colors duration-fast",
                      mode === "chat"
                        ? "bg-white shadow-panel text-fg-bright"
                        : "text-fg-muted"
                    )}
                  >
                    chat
                  </button>
                  <button
                    onClick={() => setMode("brief")}
                    className={clsx(
                      "px-2.5 py-1 rounded-full transition-colors duration-fast",
                      mode === "brief"
                        ? "bg-white shadow-panel text-fg-bright"
                        : "text-fg-muted"
                    )}
                  >
                    briefing
                  </button>
                </div>
                {companyBadge ? (
                  <span className="chip chip-active">
                    briefing on:{" "}
                    <span className="text-fg ml-1 truncate max-w-[160px]">
                      {company!.company_name}
                    </span>
                  </span>
                ) : (
                  <span className="chip">context: none</span>
                )}
              </div>

              {/* Messages */}
              <div
                ref={scrollRef}
                className="flex-1 overflow-auto px-3 py-3 space-y-3"
              >
                {turns.length === 0 && (
                  <div className="space-y-3">
                    <div className="flex items-start gap-2">
                      <VerdantAvatar size={28} />
                      <div className="text-sm text-fg leading-relaxed">
                        Verdant, at your service. Ask anything about CSRD, ESRS,
                        or the company in focus. Every answer is grounded in the
                        indexed corpus — I do not speculate.
                      </div>
                    </div>
                    <div className="pl-9 space-y-1">
                      {(companyBadge ? QUICK_PROMPTS_COMPANY : QUICK_PROMPTS).map(
                        (q) => (
                          <button
                            key={q}
                            onClick={() =>
                              mode === "chat" ? sendChat(q) : sendBrief(q)
                            }
                            className="w-full text-left text-xs text-fg-muted hover:text-fg
                                       border border-line bg-white rounded-full px-3 py-1.5
                                       hover:bg-ink-750 transition-colors duration-fast"
                          >
                            {q}
                          </button>
                        )
                      )}
                    </div>
                  </div>
                )}

                {turns.map((t, i) => {
                  if (t.kind === "user") {
                    return (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.18 }}
                        className="flex justify-end"
                      >
                        <div
                          className="max-w-[86%] px-3 py-2 rounded-2xl rounded-br-sm text-sm
                                      bg-gradient-to-br from-accent via-accent-teal to-accent-blue
                                      text-white shadow-glow"
                        >
                          {t.text}
                        </div>
                      </motion.div>
                    );
                  }
                  const isExpanded = !!expandedSources[i];
                  const cites = t.citations || [];
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.22 }}
                      className="flex items-start gap-2"
                    >
                      <VerdantAvatar size={28} />
                      <div className="flex-1 min-w-0">
                        <div className="text-2xs font-mono text-fg-faint mb-1">
                          Verdant
                          {t.mode === "brief" && (
                            <span className="ml-1 text-accent-violet">· briefing</span>
                          )}
                          {t.model && (
                            <span className="text-fg-muted ml-1">· {t.model}</span>
                          )}
                          {t.used_llm === false && (
                            <span className="text-accent-amber ml-1">
                              · llm disabled
                            </span>
                          )}
                        </div>

                        {t.mode === "chat" && (
                          <div className="text-sm text-fg-bright whitespace-pre-wrap leading-relaxed">
                            {t.text || (t.streaming ? "…" : "")}
                            {t.streaming && (
                              <span className="inline-block w-1.5 h-4 ml-0.5 align-middle bg-accent animate-pulse-soft" />
                            )}
                          </div>
                        )}

                        {t.mode === "brief" && t.brief && (
                          <BriefingCard brief={t.brief} />
                        )}
                        {t.mode === "brief" && !t.brief && t.streaming && (
                          <div className="border border-line rounded-xl p-3">
                            <SkeletonRows rows={4} />
                          </div>
                        )}

                        {cites.length > 0 && !t.streaming && (
                          <div className="mt-2">
                            <button
                              onClick={() =>
                                setExpandedSources((s) => ({
                                  ...s,
                                  [i]: !s[i],
                                }))
                              }
                              className="chip hover:bg-ink-750"
                            >
                              {isExpanded
                                ? "hide sources"
                                : `${cites.length} source${cites.length > 1 ? "s" : ""}`}
                              <span className="ml-1">
                                {isExpanded ? "▾" : "▸"}
                              </span>
                            </button>
                            {isExpanded && (
                              <div className="mt-2">
                                <CitationList citations={cites} />
                              </div>
                            )}
                          </div>
                        )}

                        {t.error && !t.streaming && (
                          <div className="text-2xs text-accent-red mt-1 font-mono">
                            {t.error}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Input */}
              <div className="border-t border-line p-2 bg-white">
                <div className="flex items-end gap-2">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        onSend();
                      }
                    }}
                    rows={2}
                    placeholder={
                      mode === "chat" ? "brief the agent…" : "request a briefing card…"
                    }
                    className="flex-1 bg-white border border-line rounded-xl px-3 py-2
                               text-sm outline-none focus:border-accent focus:shadow-glow
                               resize-none transition-all duration-fast"
                  />
                  {streaming ? (
                    <button onClick={stop} className="btn-ghost px-3 py-2">
                      stop
                    </button>
                  ) : (
                    <button
                      onClick={onSend}
                      disabled={!input.trim() || briefMutation.isPending}
                      className="btn-primary px-3 py-2"
                      aria-label="Send"
                      title="Send (Enter)"
                    >
                      send
                    </button>
                  )}
                </div>
                <div className="flex items-center justify-between mt-1.5 px-0.5">
                  <span className="text-2xs font-mono text-fg-faint">
                    enter to send · shift+enter = newline
                  </span>
                  <span className="text-2xs font-mono text-fg-faint">
                    esc to close
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function verdictTone(v: string): "leader" | "laggard" | "peer" {
  const s = v.toLowerCase();
  if (s.startsWith("applies")) return "leader";
  if (s.startsWith("not")) return "peer";
  return "peer";
}

function confidenceTone(c: string): string {
  const s = c.toLowerCase();
  if (s === "high") return "leader";
  if (s === "low") return "laggard";
  return "medium";
}

function BriefingCard({ brief }: { brief: CopilotBriefResponse }) {
  return (
    <div className="card-soft overflow-hidden">
      <div className="px-3 py-2 border-b border-line flex items-center justify-between bg-gradient-to-br from-white to-ink-750">
        <div className="flex items-center gap-2 min-w-0">
          <Badge tone={verdictTone(brief.verdict)}>{brief.verdict.replace(/_/g, " ")}</Badge>
          <span className="font-semibold text-fg-bright truncate">
            {brief.headline}
          </span>
        </div>
        <Badge tone={confidenceTone(brief.confidence)}>
          {brief.confidence} conf.
        </Badge>
      </div>
      <div className="p-3 text-sm text-fg leading-relaxed">
        {brief.summary}
      </div>
      {brief.findings.length > 0 && (
        <div className="px-3 pb-3">
          <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mb-2">
            Findings
          </div>
          <ul className="space-y-1.5">
            {brief.findings.map((f, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-xs text-fg-muted"
              >
                <Badge tone={f.severity}>{f.severity}</Badge>
                <span className="flex-1">{f.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {brief.confidence_reason && (
        <div className="px-3 pb-3 text-2xs font-mono text-fg-faint">
          why: {brief.confidence_reason}
        </div>
      )}
    </div>
  );
}
