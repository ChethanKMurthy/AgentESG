import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
  useAnalysisFull,
  useCompany,
  useCompare,
  useRoadmap,
} from "../hooks/api";
import { Panel } from "../components/ui/Panel";
import { StatTile } from "../components/ui/StatTile";
import { SkeletonRows } from "../components/ui/Skeleton";
import { Badge } from "../components/ui/Badge";
import { PercentileBar } from "../components/charts/PercentileBar";
import { RadarScore } from "../components/charts/RadarScore";
import { CitationList } from "../components/ui/Citation";
import { Explainer } from "../components/ui/Explainer";
import { fmtInt, fmtPct, fmtNum, shorten } from "../lib/formatters";
import type { BenchmarkStat } from "../types/api";

export default function CompanyDetail() {
  const { id } = useParams();
  const companyId = id ? Number(id) : undefined;

  const { data: company } = useCompany(companyId);
  const { data: full, isLoading: fullLoading } = useAnalysisFull(companyId);
  const [peerScope, setPeerScope] = useState<
    "industry" | "sector" | "country" | "sector_country" | "industry_country"
  >("industry");
  const { data: compare } = useCompare(companyId, peerScope);
  const { data: roadmap } = useRoadmap(companyId, 12);

  const radar = useMemo(() => {
    if (!compare) return [];
    const pick = [
      "renewable_energy_percent",
      "waste_recycled_percent",
      "board_independence_percent",
      "female_employee_ratio",
      "esg_score",
    ];
    return pick.map((m) => {
      const b = compare.benchmarks[m];
      const rank = b?.percentile_rank ?? 0;
      return { metric: shortMetric(m), value: rank };
    });
  }, [compare]);

  return (
    <div className="p-3 grid gap-3 grid-cols-12 auto-rows-min">
      {/* Header */}
      <Panel className="col-span-12" title="company">
        {!company ? (
          <SkeletonRows rows={2} />
        ) : (
          <div className="grid grid-cols-12 gap-3 items-center">
            <div className="col-span-12 md:col-span-5">
              <div className="text-fg-faint text-2xs mono">
                #{company.company_id}
              </div>
              <div className="text-fg-bright text-lg font-semibold">
                {company.company_name}
              </div>
              <div className="text-fg-muted text-xs mono mt-1">
                {company.country} · {company.sector} · {company.industry}
              </div>
            </div>
            <Kv label="revenue" value={fmtMoney(company.revenue_usd)} />
            <Kv label="assets" value={fmtMoney(company.total_assets_usd)} />
            <Kv label="employees" value={fmtInt(company.employees)} />
            <Kv
              label="csrd"
              value={
                company.csrd_applicable ? (
                  <Badge tone="leader">applicable</Badge>
                ) : (
                  <Badge>n/a</Badge>
                )
              }
            />
          </div>
        )}
      </Panel>

      {/* KPI tiles from full analysis */}
      <div className="col-span-12 grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile
          label="esg score"
          value={fmtNum(full?.metrics?.esg_score, 1)}
          tone={
            !full?.metrics?.esg_score
              ? "default"
              : full.metrics.esg_score >= 60
              ? "good"
              : full.metrics.esg_score >= 45
              ? "warn"
              : "bad"
          }
        />
        <StatTile
          label="renewable energy"
          value={fmtPct(full?.metrics?.renewable_energy_percent)}
          tone={
            !full?.metrics?.renewable_energy_percent
              ? "default"
              : full.metrics.renewable_energy_percent >= 40
              ? "good"
              : full.metrics.renewable_energy_percent >= 20
              ? "warn"
              : "bad"
          }
        />
        <StatTile
          label="board independence"
          value={fmtPct(full?.metrics?.board_independence_percent)}
          tone={
            !full?.metrics?.board_independence_percent
              ? "default"
              : full.metrics.board_independence_percent >= 50
              ? "good"
              : "bad"
          }
        />
        <StatTile
          label="incidents"
          value={fmtInt(full?.metrics?.incident_count)}
          tone={
            full?.metrics?.incident_count === undefined
              ? "default"
              : (full.metrics.incident_count ?? 0) > 5
              ? "bad"
              : "good"
          }
        />
      </div>

      {/* Rule findings */}
      <Panel className="col-span-12 lg:col-span-6 min-h-[260px]" title="rule findings">
        {fullLoading || !full ? (
          <SkeletonRows rows={6} />
        ) : (
          <div className="overflow-auto max-h-[420px]">
            <table className="table-compact">
              <thead>
                <tr>
                  <th>Rule</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Triggered</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {full.rule_results.map((r) => (
                  <tr key={r.rule_id}>
                    <td className="mono text-2xs text-fg-muted">{r.rule_id}</td>
                    <td className="text-fg-muted">{r.category}</td>
                    <td>
                      <Badge tone={r.severity}>{r.severity}</Badge>
                    </td>
                    <td>
                      {r.triggered ? (
                        <Badge tone="critical">yes</Badge>
                      ) : (
                        <Badge>no</Badge>
                      )}
                    </td>
                    <td className="text-xs text-fg-muted">{r.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Benchmark percentiles */}
      <Panel
        className="col-span-12 lg:col-span-6 min-h-[260px]"
        title={`benchmark · ${
          compare ? `vs ${peerScope.replace("_", "+")} · n=${compare.peer_count}` : "…"
        }`}
        actions={
          <div className="inline-flex rounded-full border border-line bg-ink-750 p-0.5 text-2xs font-mono">
            {(["industry", "sector", "country"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setPeerScope(s)}
                className={
                  "px-2 py-0.5 rounded-full transition-colors duration-fast " +
                  (peerScope === s
                    ? "bg-white shadow-panel text-fg-bright"
                    : "text-fg-muted hover:text-fg")
                }
              >
                {s}
              </button>
            ))}
          </div>
        }
      >
        {!compare ? (
          <SkeletonRows rows={8} />
        ) : compare.peer_count === 0 ? (
          <div className="text-sm text-fg-muted">
            No peers found for scope <code>{peerScope}</code> — try a wider peer set.
          </div>
        ) : (
          <div className="space-y-2">
            {Object.values(compare.benchmarks).map((b) => (
              <BenchRow key={b.metric} b={b} />
            ))}
          </div>
        )}
      </Panel>

      {/* Radar */}
      <Panel className="col-span-12 lg:col-span-6" title="positioning (percentile)">
        {radar.length === 0 ? <SkeletonRows rows={5} /> : <RadarScore data={radar} />}
      </Panel>

      {/* Roadmap */}
      <Panel className="col-span-12 lg:col-span-6" title="roadmap · next 12m">
        {!roadmap ? (
          <SkeletonRows rows={6} />
        ) : roadmap.items.length === 0 ? (
          <div className="text-fg-muted text-sm">
            No material gaps identified — keep monitoring.
          </div>
        ) : (
          <div className="space-y-2">
            {roadmap.items.map((item) => (
              <div
                key={item.id}
                className="border border-line rounded-xl p-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-2xs text-fg-faint">
                      #{item.priority}
                    </span>
                    <span className="text-fg-bright text-sm">{item.title}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Badge tone={item.severity}>{item.severity}</Badge>
                    <Badge>{item.horizon}</Badge>
                    <Badge
                      tone={
                        item.confidence === "high"
                          ? "leader"
                          : item.confidence === "low"
                          ? "laggard"
                          : "medium"
                      }
                    >
                      {item.confidence} conf.
                    </Badge>
                  </div>
                </div>
                <div className="text-xs text-fg-muted mt-1">
                  {item.evidence}
                </div>
                <ul className="mt-2 list-disc pl-5 text-xs text-fg-muted space-y-0.5">
                  {item.actions.slice(0, 3).map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
                {item.kpis.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {item.kpis.slice(0, 4).map((k, i) => (
                      <span key={i} className="chip">
                        {k}
                      </span>
                    ))}
                  </div>
                )}
                <Explainer explanation={item.explanation} />
              </div>
            ))}
          </div>
        )}
      </Panel>

      {/* Report + citations */}
      <Panel className="col-span-12 lg:col-span-8" title="ai compliance brief">
        {fullLoading || !full ? (
          <SkeletonRows rows={10} />
        ) : (
          <pre className="text-xs text-fg leading-relaxed whitespace-pre-wrap font-sans">
            {full.report || "No report generated."}
          </pre>
        )}
      </Panel>

      <Panel className="col-span-12 lg:col-span-4" title="retrieved context">
        {fullLoading || !full ? (
          <SkeletonRows rows={5} />
        ) : (
          <CitationList citations={full.citations} />
        )}
      </Panel>

      {/* Agent trace */}
      <Panel className="col-span-12" title="agent trace">
        {!full ? (
          <SkeletonRows rows={3} />
        ) : (
          <div className="flex flex-wrap gap-2">
            {full.trace.map((t, i) => (
              <div key={i} className="border border-line rounded-sm p-2 min-w-[180px]">
                <div className="flex items-center justify-between">
                  <div className="font-mono text-xs text-fg-bright">{t.agent}</div>
                  <Badge tone={t.status === "ok" ? "ok" : "error"}>
                    {t.status}
                  </Badge>
                </div>
                <div className="text-2xs text-fg-faint mono mt-1">
                  {t.duration_ms.toFixed(1)} ms
                </div>
                {t.error && (
                  <div className="text-2xs text-accent-red mt-1">{t.error}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  );
}

function Kv({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="col-span-6 md:col-span-1">
      <div className="panel-title">{label}</div>
      <div className="mono text-sm text-fg-bright mt-1">{value}</div>
    </div>
  );
}

function BenchRow({ b }: { b: BenchmarkStat }) {
  return (
    <div className="grid grid-cols-12 gap-2 items-center text-xs">
      <div className="col-span-4 truncate text-fg-muted">{shortMetric(b.metric)}</div>
      <div className="col-span-2 mono text-fg-bright">{fmtNum(b.value, 2)}</div>
      <div className="col-span-4">
        <PercentileBar value={b.percentile_rank} direction={b.direction} />
      </div>
      <div className="col-span-2 text-right">
        <Badge tone={b.status}>{b.status}</Badge>
      </div>
    </div>
  );
}

function fmtMoney(v?: number | null): string {
  if (v === null || v === undefined) return "—";
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(1)}K`;
  return `$${v.toFixed(0)}`;
}

function shortMetric(m: string): string {
  return m
    .replace("_tco2e", "")
    .replace("_percent", "%")
    .replace("_mwh", " MWh")
    .replace("_m3", " m³")
    .replace(/_/g, " ");
}
