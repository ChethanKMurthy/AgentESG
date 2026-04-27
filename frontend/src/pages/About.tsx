import { Link } from "react-router-dom";
import { Aurora } from "../components/hero/Aurora";
import { Reveal, Stagger, StaggerItem } from "../components/ui/Reveal";
import { Badge } from "../components/ui/Badge";

const FRAMEWORKS = [
  {
    tag: "CSRD",
    full: "Corporate Sustainability Reporting Directive",
    body: "EU directive adopted in 2022. Replaces the NFRD and expands the universe and depth of mandatory disclosure.",
  },
  {
    tag: "ESRS",
    full: "European Sustainability Reporting Standards",
    body: "Sector-agnostic and topical standards by EFRAG underpinning CSRD. Covers E1–E5, S1–S4, G1.",
  },
  {
    tag: "SASB",
    full: "Sustainability Accounting Standards Board",
    body: "Industry-specific disclosure standards stewarded by the IFRS Foundation (ISSB). Investor-focused materiality.",
  },
  {
    tag: "TCFD",
    full: "Task Force on Climate-related Financial Disclosures",
    body: "Four-pillar framework (governance, strategy, risk, metrics/targets) shaping climate risk disclosure globally.",
  },
  {
    tag: "GRI",
    full: "Global Reporting Initiative",
    body: "Multi-stakeholder impact disclosure standards, often used alongside CSRD/ESRS for broader audiences.",
  },
  {
    tag: "GHG",
    full: "Greenhouse Gas Protocol",
    body: "De facto standard for Scopes 1, 2, and 3 corporate inventory accounting. Basis for most ESRS E1 numbers.",
  },
];

const ARCHITECTURE = [
  {
    layer: "Backend",
    body: "FastAPI (async), SQLAlchemy 2.0 over PostgreSQL. Pydantic Settings for env-driven config, structlog JSON logs, Alembic migrations.",
    accent: "from-accent-blue to-accent-indigo",
  },
  {
    layer: "Rule engine",
    body: "Declarative rules (category, severity, citations) evaluated deterministically. Data-driven — no hardcoded if-trees.",
    accent: "from-accent-violet to-accent-rose",
  },
  {
    layer: "RAG",
    body: "Sentence-transformer embeddings → FAISS inner-product index + BM25 sparse. Reciprocal-rank fusion, MMR diversification.",
    accent: "from-accent-emerald to-accent-teal",
  },
  {
    layer: "Multi-agent",
    body: "Five agents (data, retrieval, analysis, report, audit) with a shared context. Each step emits latency + status trace.",
    accent: "from-accent to-accent-blue",
  },
  {
    layer: "Analytics",
    body: "Direction-aware percentiles, per-metric peer distributions, pillar scoring, composite E/S/G derivation.",
    accent: "from-accent-teal to-accent-blue",
  },
  {
    layer: "Frontend",
    body: "React 18 + TypeScript + Vite, Tailwind tokens, Recharts, React Query, Framer Motion, nginx-proxied API.",
    accent: "from-accent-amber to-accent-rose",
  },
  {
    layer: "Infrastructure",
    body: "Docker Compose (backend + postgres + frontend-nginx), multi-stage images, healthchecks, persistent volumes.",
    accent: "from-accent-indigo to-accent-violet",
  },
];

export default function About() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <Aurora />
        <div className="max-w-5xl mx-auto px-6 pt-24 pb-20 relative">
          <Reveal>
            <div className="text-xs font-mono uppercase tracking-widest text-accent">
              About
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <h1 className="mt-3 font-serif font-light text-display-md md:text-display-lg text-fg-bright leading-[1.0]">
              A workstation for
              <br />
              <span className="italic-serif gradient-text">
                verifiable sustainability disclosure.
              </span>
            </h1>
          </Reveal>
          <Reveal delay={0.2}>
            <p className="mt-6 text-lg md:text-xl text-fg-muted leading-relaxed max-w-3xl">
              esg.intel combines the analytical rigor of a trading terminal with
              the auditability of a regulatory filing. Deterministic rule
              evaluation. Hybrid retrieval over a regulatory corpus. LLM
              reasoning that never speaks without citations.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ESG primer */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <Reveal>
          <SectionHead kicker="Primer" title="What ESG is, in plain terms." />
        </Reveal>
        <Stagger className="space-y-5 text-fg text-lg leading-relaxed">
          <StaggerItem>
            <p>
              <strong>ESG</strong> stands for Environmental, Social, and
              Governance. It is a framework for evaluating a company along three
              dimensions that sit outside the traditional income statement but
              materially shape long-term risk and returns.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              <span className="italic-serif gradient-text-warm">
                Environmental
              </span>{" "}
              captures a company&apos;s footprint on natural systems —
              greenhouse-gas emissions across Scopes 1, 2, and 3, energy and
              renewable mix, water withdrawals, biodiversity impacts, waste
              generation and circularity, and pollution events.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              <span className="italic-serif gradient-text">Social</span> captures
              how a company treats the people it touches — its own workforce
              (pay equity, diversity, health and safety), workers in the value
              chain, affected communities, and end-consumers.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              <span className="italic-serif gradient-text">Governance</span>{" "}
              captures the quality of corporate oversight — board independence,
              diversity, tenure, committee structure; business conduct policies
              on anti-corruption, whistleblowing, lobbying; and the reliability
              of internal controls.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              Under <strong>CSRD</strong>, large EU companies (and many non-EU
              companies with an EU footprint) must disclose this information in
              a machine-readable, assured format. The <strong>ESRS</strong>{" "}
              standards specify the mandatory data points; auditors must verify
              the filings. Non-compliance is a real enforcement risk, and strong
              disclosure is increasingly a condition for capital.
            </p>
          </StaggerItem>
        </Stagger>
      </section>

      {/* Frameworks */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <Reveal>
          <SectionHead
            kicker="Frameworks we speak"
            title={
              <>
                The standards the platform{" "}
                <span className="italic-serif gradient-text">aligns to.</span>
              </>
            }
          />
        </Reveal>
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FRAMEWORKS.map((f) => (
            <StaggerItem key={f.tag}>
              <div className="card p-6 h-full tilt-hover">
                <div className="flex items-center gap-2 mb-3">
                  <Badge tone="info">{f.tag}</Badge>
                  <span className="text-xs font-mono text-fg-faint">
                    {f.full}
                  </span>
                </div>
                <p className="text-sm text-fg-muted leading-relaxed">
                  {f.body}
                </p>
              </div>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* Methodology */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <Reveal>
          <SectionHead
            kicker="Methodology"
            title={
              <>
                How we generate a result{" "}
                <span className="italic-serif gradient-text-warm">— layer by layer.</span>
              </>
            }
            sub="Every surface of the UI can be traced to one of the layers below."
          />
        </Reveal>
        <Stagger className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ARCHITECTURE.map((a) => (
            <StaggerItem key={a.layer}>
              <div className="card p-6 h-full relative overflow-hidden">
                <span
                  className={`absolute -top-12 -right-12 w-40 h-40 rounded-full blur-2xl opacity-40 bg-gradient-to-br ${a.accent}`}
                />
                <div className="relative">
                  <Badge tone="leader">{a.layer}</Badge>
                  <p className="text-sm text-fg-muted leading-relaxed mt-3">
                    {a.body}
                  </p>
                </div>
              </div>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* Trust */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <Reveal>
          <SectionHead
            kicker="Trust"
            title={
              <>
                Why the AI output here{" "}
                <span className="italic-serif gradient-text">is auditable.</span>
              </>
            }
          />
        </Reveal>
        <Stagger className="space-y-4 text-fg-muted text-base leading-relaxed">
          <StaggerItem>
            <p>
              Every LLM response is produced by the <code>ReportAgent</code> or
              the <code>Copilot</code> endpoint against a prompt that includes
              (i) deterministic rule-engine findings, (ii) structured company
              and metric JSON, and (iii) retrieved regulatory passages. The
              system prompt forbids numeric fabrication and requires inline [n]
              citations.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              Retrieved passages are ranked by both semantic similarity (FAISS)
              and lexical relevance (BM25), fused with reciprocal-rank fusion,
              and diversified with maximal-marginal relevance. The user sees
              every cited chunk, its source, and its fusion score.
            </p>
          </StaggerItem>
          <StaggerItem>
            <p>
              Backend middleware logs each request with a{" "}
              <code>request_id</code>, method, path, latency, and retrieval
              citations. Agent steps write their own audit rows. A full run of{" "}
              <code>/api/analysis/full</code> leaves a five-row audit trail plus
              a summary row.
            </p>
          </StaggerItem>
        </Stagger>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <Reveal>
          <div className="card p-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 relative overflow-hidden">
            <div className="absolute inset-0 bg-aurora opacity-40 pointer-events-none" />
            <div className="relative">
              <h3 className="font-serif text-display-sm text-fg-bright">
                See it run on{" "}
                <span className="italic-serif gradient-text">your data.</span>
              </h3>
              <p className="text-fg-muted mt-1 text-lg">
                Upload one fiscal year and we&apos;ll route you straight to the
                dashboard.
              </p>
            </div>
            <div className="relative flex gap-2">
              <Link to="/upload" className="btn-primary px-5 py-2.5 text-base">
                Upload KPIs →
              </Link>
              <Link to="/dashboard" className="btn-ghost px-5 py-2.5 text-base">
                Open terminal
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}

function SectionHead({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: React.ReactNode;
  sub?: string;
}) {
  return (
    <header className="mb-10 max-w-4xl">
      <div className="text-xs font-mono uppercase tracking-widest text-accent">
        {kicker}
      </div>
      <h2 className="mt-3 font-serif font-light text-display-sm md:text-display-md text-fg-bright leading-[1.02]">
        {title}
      </h2>
      {sub && (
        <p className="text-fg-muted mt-4 text-lg leading-relaxed">{sub}</p>
      )}
    </header>
  );
}
