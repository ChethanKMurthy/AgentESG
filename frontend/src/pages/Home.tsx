import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Aurora } from "../components/hero/Aurora";
import { Marquee } from "../components/hero/Marquee";
import { Reveal, Stagger, StaggerItem } from "../components/ui/Reveal";
import { AnimatedNumber } from "../components/ui/AnimatedNumber";
import { Badge } from "../components/ui/Badge";

const PILLARS = [
  {
    tag: "E",
    accent: "from-accent-emerald to-accent-teal",
    title: "Environmental",
    body: "Climate transition, emissions, energy, water, biodiversity, circular economy — codified under ESRS E1 through E5.",
  },
  {
    tag: "S",
    accent: "from-accent-blue to-accent-indigo",
    title: "Social",
    body: "Own workforce, value-chain workers, affected communities, consumers — ESRS S1 through S4, with DEI and fair-labor emphasis.",
  },
  {
    tag: "G",
    accent: "from-accent-violet to-accent-rose",
    title: "Governance",
    body: "Business conduct, board composition, whistleblowing, anti-corruption, lobbying — ESRS G1.",
  },
];

const CAPABILITIES = [
  {
    title: "Deterministic rule engine",
    tone: "accent",
    body: "CSRD applicability + ESRS disclosure triggers modeled as versioned, data-driven rules. Every trigger is auditable.",
    hint: "rule_engine/",
  },
  {
    title: "Hybrid RAG retrieval",
    tone: "violet",
    body: "FAISS dense + BM25 sparse fusion with MMR reranking over your regulatory corpus. Every LLM claim carries a citation.",
    hint: "rag/",
  },
  {
    title: "Multi-agent orchestration",
    tone: "emerald",
    body: "Data → retrieval → analysis → report → audit. Each step emits a structured trace with latency and status.",
    hint: "agents/",
  },
  {
    title: "Peer benchmarking",
    tone: "blue",
    body: "Direction-aware percentiles against sector, country, or global peers. Composite scoring across E/S/G pillars.",
    hint: "analytics/",
  },
  {
    title: "Automated roadmap",
    tone: "amber",
    body: "Prioritized, horizon-bucketed actions and KPIs generated from rule gaps and benchmark laggards.",
    hint: "roadmap/",
  },
  {
    title: "Full audit trail",
    tone: "rose",
    body: "Every request, agent step, rule firing, and retrieval call is logged with request-id correlation.",
    hint: "middleware/",
  },
];

const STEPS = [
  {
    n: "01",
    kicker: "Upload",
    title: "Drop one fiscal year of KPIs.",
    body: "Company profile + ESG metrics, via the form or a JSON paste. No schema acrobatics required.",
  },
  {
    n: "02",
    kicker: "Analyze",
    title: "Agents go to work.",
    body: "Deterministic rules fire, the retrieval layer pulls regulatory context, Claude drafts a grounded compliance brief.",
  },
  {
    n: "03",
    kicker: "Act",
    title: "Benchmark, gap, roadmap — one screen.",
    body: "Percentile ranks, triggered rules, and a prioritized action plan, with every AI claim cited.",
  },
];

const ARTICLES = [
  {
    source: "Nature",
    topic: "Climate Science",
    title: "Research & analysis on climate change",
    body: "Peer-reviewed updates on attribution, tipping points, and mitigation pathways — a core primary source for ESRS E1 evidence.",
    href: "https://www.nature.com/subjects/climate-change",
    accent: "from-accent-emerald to-accent-teal",
  },
  {
    source: "IPCC",
    topic: "Assessment Reports",
    title: "The authoritative synthesis on climate",
    body: "Working group reports and synthesis summaries — the scientific basis most policy instruments, including CSRD, cite by default.",
    href: "https://www.ipcc.ch/",
    accent: "from-accent-blue to-accent-indigo",
  },
  {
    source: "EFRAG",
    topic: "ESRS",
    title: "European Sustainability Reporting Standards",
    body: "The standards body shaping the disclosure requirements for CSRD-reporting companies — exposure drafts, Q&A, and taxonomy.",
    href: "https://www.efrag.org/",
    accent: "from-accent-violet to-accent-rose",
  },
  {
    source: "UNEP",
    topic: "Environment",
    title: "Global environmental coverage",
    body: "Nature briefs, biodiversity updates, and the flagship Emissions Gap Report from the UN Environment Programme.",
    href: "https://www.unep.org/",
    accent: "from-accent-teal to-accent-blue",
  },
  {
    source: "SBTi",
    topic: "Targets",
    title: "Science-based targets initiative",
    body: "Methodologies and company-level commitments for aligning emission targets with the 1.5 °C pathway.",
    href: "https://sciencebasedtargets.org/",
    accent: "from-accent-emerald to-accent-blue",
  },
  {
    source: "Reuters",
    topic: "Sustainability",
    title: "The business of sustainability, daily",
    body: "Market coverage on ESG regulation, climate risk, carbon markets, and corporate disclosure news.",
    href: "https://www.reuters.com/sustainability/",
    accent: "from-accent-amber to-accent-rose",
  },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <Aurora />
        <div className="max-w-7xl mx-auto px-6 pt-24 pb-28 relative">
          <Reveal>
            <div className="flex flex-wrap items-center gap-2 mb-6">
              <Badge tone="leader">CSRD-ready</Badge>
              <Badge tone="info">ESRS E1 · G1 · S1 · E3 · E5</Badge>
              <Badge>Hybrid RAG · Multi-agent · Audited</Badge>
            </div>
          </Reveal>

          <HeroHeadline />

          <Reveal delay={0.35}>
            <p className="mt-6 text-lg md:text-xl text-fg-muted max-w-2xl leading-relaxed">
              An intelligence workstation that turns a company&apos;s KPIs into a
              cited CSRD applicability verdict, an ESRS-aligned rule evaluation,
              peer benchmarks, and a prioritized roadmap — in one screen.
            </p>
          </Reveal>

          <Reveal delay={0.45}>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link to="/upload" className="btn-primary text-base px-5 py-2.5">
                Upload your KPIs
                <ArrowRight />
              </Link>
              <Link to="/dashboard" className="btn-ghost text-base px-5 py-2.5">
                Open the terminal
              </Link>
              <Link to="/about" className="btn-ghost text-base px-5 py-2.5">
                How it works
              </Link>
            </div>
          </Reveal>

          {/* Stat strip */}
          <Stagger className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-3 max-w-5xl">
            <StaggerItem>
              <StatBit value={<AnimatedNumber to={10} />} unit="rules" label="CSRD + ESRS" />
            </StaggerItem>
            <StaggerItem>
              <StatBit value={<AnimatedNumber to={12} />} unit="metrics" label="peer-benchmarked" />
            </StaggerItem>
            <StaggerItem>
              <StatBit value={<AnimatedNumber to={5} />} unit="agents" label="orchestrated" />
            </StaggerItem>
            <StaggerItem>
              <StatBit value={<AnimatedNumber to={100} suffix="%" />} unit="cited" label="AI output" />
            </StaggerItem>
          </Stagger>
        </div>
      </section>

      <Marquee />

      {/* Philosophy / What ESG is */}
      <section className="max-w-7xl mx-auto px-6 pt-24 pb-10">
        <div className="grid grid-cols-12 gap-8 items-start">
          <div className="col-span-12 md:col-span-5">
            <Reveal>
              <div className="text-xs font-mono uppercase tracking-widest text-accent">
                Primer
              </div>
              <h2 className="mt-3 font-serif font-light text-display-md text-fg-bright leading-[1.02]">
                Three letters,
                <br />
                <span className="italic gradient-text-warm">balance-sheet weight.</span>
              </h2>
            </Reveal>
          </div>
          <div className="col-span-12 md:col-span-7 md:pt-6">
            <Reveal delay={0.1}>
              <p className="text-lg text-fg leading-relaxed">
                ESG is not marketing. It is the non-financial axis along which
                regulators, insurers, and institutional allocators now price
                long-term risk — and the axis along which the EU&apos;s CSRD now
                obligates disclosure, assured by auditors, machine-readable, at
                scale.
              </p>
            </Reveal>
          </div>
        </div>

        <Stagger className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
          {PILLARS.map((p) => (
            <StaggerItem key={p.tag}>
              <motion.div
                whileHover={{ y: -4 }}
                transition={{ type: "spring", stiffness: 300, damping: 22 }}
                className="card p-6 h-full tilt-hover"
              >
                <div className="flex items-start justify-between">
                  <span
                    className={`w-11 h-11 rounded-2xl bg-gradient-to-br ${p.accent} text-white flex items-center justify-center font-serif text-xl shadow-glow`}
                  >
                    {p.tag}
                  </span>
                  <span className="text-2xs font-mono uppercase tracking-widest text-fg-faint">
                    pillar
                  </span>
                </div>
                <div className="mt-4 font-serif text-2xl text-fg-bright">
                  {p.title}
                </div>
                <p className="text-sm text-fg-muted leading-relaxed mt-2">
                  {p.body}
                </p>
              </motion.div>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* Capabilities */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <Reveal>
          <SectionHead
            kicker="Platform"
            title={
              <>
                Built like a{" "}
                <span className="italic-serif gradient-text">quant terminal,</span>
                <br />
                wired to an auditor&apos;s filing cabinet.
              </>
            }
            sub="Six integrated layers. Every output traces back to a rule, a peer distribution, or a cited source."
          />
        </Reveal>
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {CAPABILITIES.map((c) => (
            <StaggerItem key={c.title}>
              <motion.div
                whileHover={{ y: -3 }}
                transition={{ type: "spring", stiffness: 300, damping: 22 }}
                className="card p-6 h-full relative overflow-hidden"
              >
                <span
                  className={`absolute -top-12 -right-12 w-40 h-40 rounded-full blur-2xl opacity-40`}
                  style={{
                    background: toneToGradient(c.tone),
                  }}
                />
                <div className="relative">
                  <div className="flex items-center justify-between">
                    <span
                      className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-glow"
                      style={{ background: toneToGradient(c.tone) }}
                    >
                      <Sparkle />
                    </span>
                    <span className="chip">{c.hint}</span>
                  </div>
                  <div className="mt-4 font-serif text-xl text-fg-bright">
                    {c.title}
                  </div>
                  <p className="text-sm text-fg-muted leading-relaxed mt-2">
                    {c.body}
                  </p>
                </div>
              </motion.div>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* Flow */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <Reveal>
          <SectionHead
            kicker="Flow"
            title={
              <>
                From raw KPIs{" "}
                <span className="italic-serif gradient-text">to a brief</span>,
                in one click.
              </>
            }
          />
        </Reveal>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
          <div className="absolute top-12 left-[5%] right-[5%] h-px bg-gradient-to-r from-transparent via-line-strong to-transparent hidden md:block" />
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={0.1 * i}>
              <div className="card p-6 h-full relative overflow-hidden tilt-hover">
                <span className="absolute -right-4 -top-2 font-serif text-[120px] leading-none text-ink-700 select-none">
                  {s.n}
                </span>
                <div className="relative">
                  <div className="text-xs font-mono uppercase tracking-widest text-accent">
                    Step · {s.kicker}
                  </div>
                  <div className="mt-2 font-serif text-2xl text-fg-bright">
                    {s.title}
                  </div>
                  <p className="text-sm text-fg-muted mt-3 leading-relaxed">
                    {s.body}
                  </p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <div className="diag-divider my-10" />

      {/* Reading */}
      <section id="reading" className="max-w-7xl mx-auto px-6 py-16">
        <Reveal>
          <SectionHead
            kicker="Resources"
            title={
              <>
                Curated ESG & nature{" "}
                <span className="italic-serif gradient-text-warm">reading.</span>
              </>
            }
            sub="Primary sources. External links open to the publisher; esg.intel does not proxy or store their content."
          />
        </Reveal>

        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ARTICLES.map((a, i) => (
            <StaggerItem key={a.href}>
              <motion.a
                href={a.href}
                target="_blank"
                rel="noreferrer"
                whileHover={{ y: -4 }}
                transition={{ type: "spring", stiffness: 280, damping: 20 }}
                className="card p-6 h-full block group relative overflow-hidden"
              >
                <span
                  className={`absolute -top-16 -right-16 w-52 h-52 rounded-full blur-2xl opacity-30 bg-gradient-to-br ${a.accent}`}
                />
                <div className="relative">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-mono uppercase tracking-widest text-fg-faint">
                      {a.source}
                    </div>
                    <Badge>{a.topic}</Badge>
                  </div>
                  <div className="mt-4 font-serif text-xl text-fg-bright group-hover:text-accent-blue transition-colors duration-fast">
                    {a.title}
                  </div>
                  <p className="text-sm text-fg-muted mt-2 leading-relaxed">
                    {a.body}
                  </p>
                  <div className="mt-5 text-xs font-mono text-accent-blue underline-grow inline-block">
                    visit source ↗
                  </div>
                </div>
              </motion.a>
            </StaggerItem>
          ))}
        </Stagger>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 pt-10 pb-24">
        <Reveal>
          <div className="card p-12 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-aurora opacity-60 pointer-events-none" />
            <div className="relative">
              <h3 className="font-serif text-display-sm md:text-display-md text-fg-bright">
                Ready to see it on{" "}
                <span className="italic-serif gradient-text">your data?</span>
              </h3>
              <p className="text-fg-muted mt-3 max-w-xl mx-auto text-lg">
                Drop one year of KPIs and receive back a briefing, a peer
                percentile, rule triggers, and a roadmap — in one click.
              </p>
              <div className="mt-8 flex justify-center gap-3 flex-wrap">
                <Link to="/upload" className="btn-primary text-base px-5 py-2.5">
                  Upload KPIs
                  <ArrowRight />
                </Link>
                <Link to="/about" className="btn-ghost text-base px-5 py-2.5">
                  How we do it
                </Link>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}

function HeroHeadline() {
  const words = ["ESG", "intelligence,"];
  const italic = "built for disclosure.";
  return (
    <div>
      <motion.h1
        initial="hidden"
        animate="show"
        variants={{
          hidden: {},
          show: { transition: { staggerChildren: 0.06, delayChildren: 0.1 } },
        }}
        className="font-serif font-light text-display-md md:text-display-lg lg:text-display-xl text-fg-bright leading-[0.98] max-w-5xl"
      >
        {words.map((w, i) => (
          <motion.span
            key={i}
            variants={{
              hidden: { y: 30, opacity: 0 },
              show: {
                y: 0,
                opacity: 1,
                transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] },
              },
            }}
            className="inline-block mr-3"
          >
            {w}
          </motion.span>
        ))}
        <br />
        <motion.span
          variants={{
            hidden: { y: 30, opacity: 0 },
            show: {
              y: 0,
              opacity: 1,
              transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.25 },
            },
          }}
          className="italic-serif gradient-text"
        >
          {italic}
        </motion.span>
      </motion.h1>
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
        <p className="text-fg-muted mt-4 text-lg leading-relaxed max-w-3xl">
          {sub}
        </p>
      )}
    </header>
  );
}

function StatBit({
  value,
  unit,
  label,
}: {
  value: React.ReactNode;
  unit?: string;
  label: string;
}) {
  return (
    <div className="card px-5 py-4 tilt-hover">
      <div className="flex items-baseline gap-1.5">
        <span className="font-serif text-4xl md:text-5xl text-fg-bright tracking-tight">
          {value}
        </span>
        {unit && (
          <span className="text-2xs font-mono uppercase tracking-widest text-fg-faint">
            {unit}
          </span>
        )}
      </div>
      <div className="text-2xs font-mono uppercase tracking-widest text-fg-muted mt-1">
        {label}
      </div>
    </div>
  );
}

function ArrowRight() {
  return (
    <motion.span
      className="inline-block"
      initial={{ x: 0 }}
      whileHover={{ x: 3 }}
    >
      →
    </motion.span>
  );
}

function Sparkle() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l2.09 5.26L20 9l-5.91 1.74L12 16l-2.09-5.26L4 9l5.91-1.74L12 2z" opacity="0.95" />
    </svg>
  );
}

function toneToGradient(tone: string): string {
  switch (tone) {
    case "violet":
      return "linear-gradient(135deg, #7c3aed, #6366f1)";
    case "emerald":
      return "linear-gradient(135deg, #10b981, #14b8a6)";
    case "blue":
      return "linear-gradient(135deg, #2563eb, #06b6d4)";
    case "amber":
      return "linear-gradient(135deg, #d97706, #f43f5e)";
    case "rose":
      return "linear-gradient(135deg, #f43f5e, #7c3aed)";
    default:
      return "linear-gradient(135deg, #06b6d4, #2563eb)";
  }
}
