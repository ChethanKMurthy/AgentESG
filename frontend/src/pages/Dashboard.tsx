import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useCompanies, useRagStats } from "../hooks/api";
import { Panel } from "../components/ui/Panel";
import { StatTile } from "../components/ui/StatTile";
import { Skeleton, SkeletonRows } from "../components/ui/Skeleton";
import { fmtInt, fmtPct, shorten } from "../lib/formatters";
import { Badge } from "../components/ui/Badge";

export default function Dashboard() {
  const { data: sample, isLoading } = useCompanies({ limit: 500 });
  const { data: rag } = useRagStats();

  const kpis = useMemo(() => {
    if (!sample) return null;
    const items = sample.items;
    const csrd = items.filter((c) => c.csrd_applicable).length;
    const sectors = new Set(items.map((c) => c.sector || "").filter(Boolean));
    const countries = new Set(items.map((c) => c.country || "").filter(Boolean));
    const avgRev =
      items.reduce((s, c) => s + (c.revenue_usd || 0), 0) /
      Math.max(1, items.length);
    return {
      total: sample.total,
      inSample: items.length,
      csrdPct: items.length ? (csrd / items.length) * 100 : 0,
      sectors: sectors.size,
      countries: countries.size,
      avgRev,
    };
  }, [sample]);

  const topBySector = useMemo(() => {
    if (!sample) return [];
    const map = new Map<string, number>();
    sample.items.forEach((c) => {
      const k = c.sector || "—";
      map.set(k, (map.get(k) || 0) + 1);
    });
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
  }, [sample]);

  return (
    <div className="p-3 grid gap-3 grid-cols-12 auto-rows-min">
      <div className="col-span-12 grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile
          label="companies (sample)"
          value={isLoading ? "…" : fmtInt(kpis?.inSample)}
          hint={`of ${fmtInt(kpis?.total)} total`}
        />
        <StatTile
          label="csrd applicable"
          value={isLoading ? "…" : fmtPct(kpis?.csrdPct)}
          tone="good"
          hint="of sampled entities"
        />
        <StatTile
          label="sectors / countries"
          value={isLoading ? "…" : `${kpis?.sectors ?? "—"} / ${kpis?.countries ?? "—"}`}
        />
        <StatTile
          label="rag index"
          value={rag?.ready ? "ready" : "idle"}
          tone={rag?.ready ? "good" : "warn"}
          hint={
            rag?.chunks !== undefined
              ? `${rag.documents} docs · ${rag.chunks} chunks`
              : "—"
          }
        />
      </div>

      <Panel className="col-span-12 lg:col-span-8 min-h-[260px]" title="recent companies">
        {isLoading ? (
          <div className="p-3">
            <SkeletonRows rows={8} />
          </div>
        ) : (
          <div className="overflow-auto max-h-[420px]">
            <table className="table-compact">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Country</th>
                  <th>Sector</th>
                  <th className="text-right">Revenue</th>
                  <th className="text-right">Employees</th>
                  <th>CSRD</th>
                </tr>
              </thead>
              <tbody>
                {sample?.items.slice(0, 20).map((c) => (
                  <tr key={c.company_id}>
                    <td className="mono text-fg-faint">{c.company_id}</td>
                    <td>
                      <Link
                        to={`/companies/${c.company_id}`}
                        className="text-fg-bright hover:underline"
                      >
                        {shorten(c.company_name, 44)}
                      </Link>
                    </td>
                    <td className="text-fg-muted">{c.country}</td>
                    <td className="text-fg-muted">{c.sector}</td>
                    <td className="text-right mono">
                      {c.revenue_usd ? (c.revenue_usd / 1e6).toFixed(0) + "M" : "—"}
                    </td>
                    <td className="text-right mono">
                      {c.employees ? fmtInt(c.employees) : "—"}
                    </td>
                    <td>
                      {c.csrd_applicable ? (
                        <Badge tone="leader">yes</Badge>
                      ) : (
                        <Badge>no</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <Panel className="col-span-12 lg:col-span-4 min-h-[260px]" title="sector mix">
        {isLoading ? (
          <SkeletonRows rows={8} />
        ) : (
          <div className="space-y-2">
            {topBySector.map(([sector, n]) => (
              <SectorBar
                key={sector}
                sector={sector}
                count={n}
                total={kpis?.inSample || 1}
              />
            ))}
          </div>
        )}
      </Panel>
    </div>
  );
}

function SectorBar({
  sector,
  count,
  total,
}: {
  sector: string;
  count: number;
  total: number;
}) {
  const pct = (count / total) * 100;
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-fg-muted">{sector}</span>
        <span className="mono text-fg-faint">
          {count} · {pct.toFixed(0)}%
        </span>
      </div>
      <div className="h-1.5 bg-ink-700 rounded-sm">
        <div className="h-full bg-accent-blue" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
