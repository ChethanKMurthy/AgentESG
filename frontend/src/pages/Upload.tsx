import { motion, AnimatePresence } from "framer-motion";
import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Reveal } from "../components/ui/Reveal";
import { Badge } from "../components/ui/Badge";
import { useUploadDisclosure } from "../hooks/api";
import type { DisclosureUploadResponse } from "../types/api";
import { fmtNum, fmtPct, fmtInt } from "../lib/formatters";

const METRIC_LABELS: Record<string, string> = {
  scope_1_emissions_tco2e: "Scope 1 (tCO2e)",
  scope_2_emissions_tco2e: "Scope 2 (tCO2e)",
  scope_3_emissions_tco2e: "Scope 3 (tCO2e)",
  energy_consumption_mwh: "Energy (MWh)",
  renewable_energy_percent: "Renewable %",
  water_usage_m3: "Water (m³)",
  waste_generated_tons: "Waste (t)",
  waste_recycled_percent: "Recycled %",
  employee_count: "Employees",
  female_employee_ratio: "Female ratio",
  board_independence_percent: "Board indep. %",
  incident_count: "Incidents",
  esg_score: "ESG score",
};

const STAGES = [
  "Parsing PDF",
  "Reading disclosure",
  "Extracting KPIs",
  "Persisting company",
  "Benchmarking vs. industry",
];

export default function Upload() {
  const nav = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [drag, setDrag] = useState(false);
  const [stageIdx, setStageIdx] = useState(0);
  const [result, setResult] = useState<DisclosureUploadResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const mutation = useUploadDisclosure();

  const onChoose = () => inputRef.current?.click();

  const onFiles = (files: FileList | null) => {
    if (!files || !files[0]) return;
    const f = files[0];
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setErr("Please upload a .pdf file.");
      return;
    }
    setErr(null);
    setResult(null);
    setFile(f);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    onFiles(e.dataTransfer.files);
  }, []);

  const runStages = () => {
    setStageIdx(0);
    const timer = setInterval(() => {
      setStageIdx((i) => (i < STAGES.length - 1 ? i + 1 : i));
    }, 1400);
    return () => clearInterval(timer);
  };

  const submit = async () => {
    if (!file) return;
    setErr(null);
    const stop = runStages();
    try {
      const data = await mutation.mutateAsync(file);
      setResult(data);
      setStageIdx(STAGES.length - 1);
      setTimeout(() => {
        nav(`/companies/${data.company_id}`);
      }, 900);
    } catch (e: any) {
      setErr(
        e?.message ||
          "Extraction failed. Check that the PDF contains selectable text (not just scanned images)."
      );
    } finally {
      stop();
    }
  };

  const pending = mutation.isPending;
  const metrics = result?.extracted_metrics || {};
  const company = result?.extracted_company || {};
  const foundMetrics = Object.keys(metrics).filter(
    (k) => !["year", "sector", "country"].includes(k)
  );

  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-aurora opacity-60 animate-aurora-shift pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 pt-20 pb-10 relative">
          <Reveal>
            <div className="text-xs font-mono uppercase tracking-widest text-accent">
              Upload
            </div>
          </Reveal>
          <Reveal delay={0.05}>
            <h1 className="mt-3 font-serif font-light text-display-md md:text-display-lg text-fg-bright leading-[1.02]">
              Drop your annual disclosure.
              <br />
              <span className="italic-serif gradient-text">
                We extract the KPIs.
              </span>
            </h1>
          </Reveal>
          <Reveal delay={0.15}>
            <p className="mt-5 text-lg text-fg-muted max-w-2xl leading-relaxed">
              Upload a sustainability or annual report as a PDF. Verdant parses
              the disclosure, extracts the ESG metrics directly, persists the
              company, and routes you to a dashboard benchmarked against your{" "}
              <span className="text-fg-bright font-medium">industry peers</span>.
            </p>
          </Reveal>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-24">
        <motion.div
          layout
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="card p-8"
        >
          {/* Dropzone */}
          <div
            onClick={onChoose}
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
            className={
              "relative flex flex-col items-center justify-center rounded-3xl border-2 border-dashed text-center cursor-pointer " +
              "transition-colors duration-fast " +
              (drag
                ? "border-accent bg-accent/5"
                : "border-line hover:border-line-strong bg-white/60")
            }
            style={{ minHeight: 280 }}
            role="button"
            aria-label="Upload disclosure PDF"
          >
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              className="hidden"
              onChange={(e) => onFiles(e.target.files)}
            />
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl mx-auto bg-gradient-to-br from-accent via-accent-teal to-accent-blue shadow-glow flex items-center justify-center">
                <DocumentIcon />
              </div>
              <div className="mt-4 font-serif text-2xl text-fg-bright">
                {file ? file.name : "Drop your PDF here"}
              </div>
              <div className="text-sm text-fg-muted mt-1">
                {file
                  ? `${(file.size / (1024 * 1024)).toFixed(2)} MB · ready to analyze`
                  : "or click to pick a file · up to 25MB · annual or sustainability report"}
              </div>
              {!file && (
                <div className="mt-6 flex items-center justify-center gap-2 text-2xs font-mono uppercase tracking-widest text-fg-faint">
                  <Badge>text-based PDF</Badge>
                  <Badge>scoped extraction</Badge>
                  <Badge tone="leader">industry-benchmarked</Badge>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <div className="text-2xs font-mono text-fg-faint">
              The system reads your disclosure. Manual metric entry is disabled
              by design — if a field is not disclosed, we mark it null.
            </div>
            <div className="flex items-center gap-2">
              {file && !pending && !result && (
                <button
                  onClick={() => {
                    setFile(null);
                    setErr(null);
                  }}
                  className="btn-ghost"
                >
                  remove
                </button>
              )}
              <button
                onClick={submit}
                disabled={!file || pending}
                className="btn-primary"
              >
                {pending ? "Extracting…" : result ? "Redirecting…" : "Analyze disclosure →"}
              </button>
            </div>
          </div>

          {err && (
            <div className="mt-4 text-sm text-accent-red font-mono">{err}</div>
          )}
        </motion.div>

        {/* Progress */}
        <AnimatePresence>
          {pending && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-5 card p-5"
            >
              <div className="text-xs font-mono uppercase tracking-widest text-accent mb-3">
                pipeline
              </div>
              <ol className="space-y-2">
                {STAGES.map((s, i) => (
                  <li
                    key={s}
                    className="flex items-center gap-3 text-sm"
                  >
                    <span
                      className={
                        "w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono " +
                        (i < stageIdx
                          ? "bg-accent-emerald text-white"
                          : i === stageIdx
                          ? "bg-gradient-to-br from-accent to-accent-blue text-white animate-pulse-soft"
                          : "bg-ink-700 text-fg-faint")
                      }
                    >
                      {i < stageIdx ? "✓" : i + 1}
                    </span>
                    <span
                      className={
                        i <= stageIdx ? "text-fg-bright" : "text-fg-faint"
                      }
                    >
                      {s}
                    </span>
                  </li>
                ))}
              </ol>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Result preview */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-5 card p-6 relative overflow-hidden"
            >
              <span className="absolute -top-16 -right-16 w-52 h-52 rounded-full blur-2xl opacity-30 bg-gradient-to-br from-accent-emerald to-accent-teal" />
              <div className="relative">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-2xs font-mono uppercase tracking-widest text-accent">
                      extraction complete
                    </div>
                    <div className="font-serif text-3xl text-fg-bright mt-1">
                      {result.company_name}
                    </div>
                    <div className="text-sm text-fg-muted mt-1">
                      {result.created ? "new record" : "updated record"} ·{" "}
                      {result.page_count} pages ·{" "}
                      {fmtInt(result.text_chars)} chars parsed · year{" "}
                      {result.year}
                    </div>
                  </div>
                  <Badge tone="leader">company #{result.company_id}</Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-5">
                  {foundMetrics.length === 0 && (
                    <div className="col-span-full text-fg-muted text-sm">
                      No numeric ESG metrics were disclosed in the PDF.
                    </div>
                  )}
                  {foundMetrics.map((k) => (
                    <div
                      key={k}
                      className="rounded-xl border border-line bg-white/80 px-3 py-2"
                    >
                      <div className="field-label">
                        {METRIC_LABELS[k] || k}
                      </div>
                      <div className="font-serif text-xl text-fg-bright">
                        {formatValue(k, metrics[k])}
                      </div>
                    </div>
                  ))}
                </div>

                {result.missing_metrics.length > 0 && (
                  <div className="mt-4">
                    <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mb-2">
                      not disclosed
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {result.missing_metrics.map((m) => (
                        <span key={m} className="chip">
                          {METRIC_LABELS[m] || m}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.extraction_notes && (
                  <div className="mt-4 text-2xs font-mono text-fg-faint">
                    note: {result.extraction_notes}
                  </div>
                )}

                <div className="mt-5 text-sm text-fg-muted">
                  Redirecting to the dashboard for{" "}
                  <span className="text-fg-bright">
                    {result.company_name}
                  </span>{" "}
                  — benchmarked against industry peers…
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </div>
  );
}

function formatValue(key: string, v: any) {
  if (v === null || v === undefined) return "—";
  if (key.endsWith("_percent") || key === "renewable_energy_percent") return fmtPct(v);
  if (key === "female_employee_ratio") return fmtNum(v, 2);
  if (key === "esg_score") return fmtNum(v, 1);
  if (key.endsWith("_count") || key === "employee_count") return fmtInt(v);
  return fmtNum(v, 2);
}

function DocumentIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="white"
      strokeWidth="1.6"
    >
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
      <path d="M9 13h6M9 17h4" />
    </svg>
  );
}
