export type CopilotStreamHandlers = {
  onMeta?: (meta: any) => void;
  onCitations?: (cites: any[]) => void;
  onToken?: (delta: string) => void;
  onError?: (err: { message: string }) => void;
  onDone?: () => void;
};

export type CopilotStreamParams = {
  query: string;
  company_id?: number | null;
  top_k?: number;
  rerank?: boolean;
};

const BASE = import.meta.env.VITE_API_BASE || "/api";

export async function streamCopilot(
  params: CopilotStreamParams,
  handlers: CopilotStreamHandlers,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${BASE}/copilot/stream`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    throw new Error(`stream failed: ${res.status} ${text}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n\n")) !== -1) {
      const chunk = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      parseSSE(chunk, handlers);
    }
  }
  if (buf.trim()) parseSSE(buf, handlers);
  handlers.onDone?.();
}

function parseSSE(chunk: string, h: CopilotStreamHandlers) {
  let event = "message";
  let data = "";
  for (const line of chunk.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return;
  try {
    const parsed = JSON.parse(data);
    if (event === "meta") h.onMeta?.(parsed);
    else if (event === "citations") h.onCitations?.(parsed);
    else if (event === "token") h.onToken?.(parsed.delta || "");
    else if (event === "error") h.onError?.(parsed);
    else if (event === "done") h.onDone?.();
  } catch {
    /* ignore malformed chunks */
  }
}
