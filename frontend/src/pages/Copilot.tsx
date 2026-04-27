import { useRef, useState } from "react";
import { Panel } from "../components/ui/Panel";
import { CitationList } from "../components/ui/Citation";
import { Badge } from "../components/ui/Badge";
import { Skeleton, SkeletonRows } from "../components/ui/Skeleton";
import { useCopilotQuery, useRagStats } from "../hooks/api";
import type { CopilotQueryResponse } from "../types/api";

type Turn = {
  role: "user" | "assistant";
  text: string;
  response?: CopilotQueryResponse;
};

export default function Copilot() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const mutation = useCopilotQuery();
  const rag = useRagStats();
  const scrollRef = useRef<HTMLDivElement>(null);

  const onSend = async () => {
    const q = input.trim();
    if (!q) return;
    setInput("");
    setTurns((t) => [...t, { role: "user", text: q }]);
    try {
      const res = await mutation.mutateAsync({ query: q });
      setTurns((t) => [...t, { role: "assistant", text: res.answer, response: res }]);
    } catch (err: any) {
      setTurns((t) => [
        ...t,
        { role: "assistant", text: `Error: ${err?.message || "request failed"}` },
      ]);
    }
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: 1e9, behavior: "smooth" });
    }, 30);
  };

  const lastAssistant = [...turns].reverse().find((t) => t.role === "assistant");

  return (
    <div className="p-3 grid gap-3 grid-cols-12 h-[calc(100vh-2.5rem-1.5rem)]">
      <Panel
        className="col-span-12 lg:col-span-8 flex flex-col"
        title="esg copilot"
        actions={
          <div className="flex items-center gap-2">
            <span className="text-2xs text-fg-faint mono">
              {rag.data?.ready
                ? `${rag.data.documents} docs · ${rag.data.chunks} chunks`
                : "rag idle"}
            </span>
            {mutation.isPending && (
              <Badge tone="medium">thinking…</Badge>
            )}
          </div>
        }
      >
        <div ref={scrollRef} className="flex-1 overflow-auto space-y-3 pr-1">
          {turns.length === 0 && !mutation.isPending && (
            <div className="text-fg-muted text-sm">
              Ask about CSRD applicability, ESRS disclosures, scope 3 calculation, or a
              specific company's ESG posture. Answers are grounded in the indexed
              regulatory corpus.
            </div>
          )}
          {turns.map((t, i) => (
            <div
              key={i}
              className={
                "rounded-sm border p-2.5 " +
                (t.role === "user"
                  ? "border-line bg-ink-750"
                  : "border-line-strong bg-ink-800")
              }
            >
              <div className="text-2xs font-mono uppercase tracking-wide text-fg-faint mb-1">
                {t.role === "user" ? "you" : "copilot"}
                {t.response?.model && (
                  <span className="ml-2 text-fg-muted">· {t.response.model}</span>
                )}
                {t.response && !t.response.used_llm && (
                  <span className="ml-2 text-accent-amber">· llm disabled</span>
                )}
              </div>
              <div className="text-sm text-fg-bright whitespace-pre-wrap leading-relaxed">
                {t.text}
              </div>
            </div>
          ))}
          {mutation.isPending && (
            <div className="border border-line rounded-sm p-2.5">
              <div className="text-2xs font-mono text-fg-faint mb-1">copilot</div>
              <SkeletonRows rows={4} />
            </div>
          )}
        </div>
        <div className="mt-2 flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
              }
            }}
            rows={2}
            placeholder="Ask the copilot… (Enter to send, Shift+Enter for newline)"
            className="flex-1 bg-ink-750 border border-line rounded-sm px-2 py-1.5 text-sm
                       text-fg outline-none focus:border-line-strong resize-none"
          />
          <button
            onClick={onSend}
            disabled={!input.trim() || mutation.isPending}
            className="chip chip-active bg-accent/10 border-accent/40 text-accent
                       disabled:opacity-50"
          >
            send
          </button>
        </div>
      </Panel>

      <Panel
        className="col-span-12 lg:col-span-4 overflow-auto"
        title="source context"
      >
        {lastAssistant?.response ? (
          <CitationList citations={lastAssistant.response.citations} />
        ) : (
          <div className="text-fg-faint text-xs">
            Sources for the latest answer will appear here.
          </div>
        )}
      </Panel>
    </div>
  );
}
