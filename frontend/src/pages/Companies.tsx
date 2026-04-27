import { useState } from "react";
import { Link } from "react-router-dom";
import { useCompanies } from "../hooks/api";
import { Panel } from "../components/ui/Panel";
import { Skeleton, SkeletonRows } from "../components/ui/Skeleton";
import { Badge } from "../components/ui/Badge";
import { fmtInt, shorten } from "../lib/formatters";

export default function Companies() {
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [sector, setSector] = useState("");
  const [csrdOnly, setCsrdOnly] = useState<boolean | undefined>(undefined);
  const [page, setPage] = useState(0);
  const limit = 50;

  const { data, isLoading } = useCompanies({
    limit,
    offset: page * limit,
    search,
    country,
    sector,
    csrd_applicable: csrdOnly,
  });

  return (
    <div className="p-3 grid gap-3">
      <Panel title="filters">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
          <TextInput placeholder="search name" value={search} onChange={setSearch} />
          <TextInput placeholder="country" value={country} onChange={setCountry} />
          <TextInput placeholder="sector" value={sector} onChange={setSector} />
          <button
            className={
              "chip " +
              (csrdOnly === true ? "chip-active bg-ink-750" : "")
            }
            onClick={() =>
              setCsrdOnly((v) => (v === true ? undefined : true))
            }
          >
            csrd: applicable
          </button>
          <button
            className={"chip " + (csrdOnly === false ? "chip-active bg-ink-750" : "")}
            onClick={() =>
              setCsrdOnly((v) => (v === false ? undefined : false))
            }
          >
            csrd: non-applicable
          </button>
        </div>
      </Panel>

      <Panel
        title={`companies ${data ? `· ${fmtInt(data.total)}` : ""}`}
        actions={
          <div className="flex items-center gap-1">
            <button
              className="chip"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              prev
            </button>
            <span className="text-2xs text-fg-faint mono">
              page {page + 1}
            </span>
            <button
              className="chip"
              onClick={() => setPage((p) => p + 1)}
              disabled={!data || (page + 1) * limit >= data.total}
            >
              next
            </button>
          </div>
        }
      >
        {isLoading ? (
          <SkeletonRows rows={12} />
        ) : (
          <div className="overflow-auto max-h-[72vh]">
            <table className="table-compact">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Country</th>
                  <th>Sector</th>
                  <th>Industry</th>
                  <th className="text-right">Revenue</th>
                  <th className="text-right">Employees</th>
                  <th>Size</th>
                  <th>CSRD</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((c) => (
                  <tr key={c.company_id}>
                    <td className="mono text-fg-faint">{c.company_id}</td>
                    <td>
                      <Link
                        to={`/companies/${c.company_id}`}
                        className="text-fg-bright hover:underline"
                      >
                        {shorten(c.company_name, 48)}
                      </Link>
                    </td>
                    <td className="text-fg-muted">{c.country}</td>
                    <td className="text-fg-muted">{c.sector}</td>
                    <td className="text-fg-muted">{shorten(c.industry, 24)}</td>
                    <td className="text-right mono">
                      {c.revenue_usd ? (c.revenue_usd / 1e6).toFixed(0) + "M" : "—"}
                    </td>
                    <td className="text-right mono">
                      {c.employees ? fmtInt(c.employees) : "—"}
                    </td>
                    <td className="text-fg-muted">{c.company_size_band}</td>
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
    </div>
  );
}

function TextInput({
  placeholder,
  value,
  onChange,
}: {
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="bg-ink-750 border border-line rounded-sm text-sm px-2 py-1.5
                 text-fg placeholder:text-fg-faint outline-none
                 focus:border-line-strong"
    />
  );
}
