import { Link, NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";
import { VerdantWidget } from "../copilot/VerdantWidget";

const NAV = [
  { to: "/", label: "Home", end: true },
  { to: "/about", label: "About" },
  { to: "/#reading", label: "Reading" },
];

export function PublicShell() {
  return (
    <div className="min-h-full flex flex-col">
      <header className="sticky top-0 z-40 border-b border-line/70 bg-white/70 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-16 px-6">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="relative w-9 h-9 rounded-2xl bg-gradient-to-br from-accent via-accent-teal to-accent-blue shadow-glow flex items-center justify-center">
              <span className="text-white font-serif text-lg leading-none tracking-tight">
                e
              </span>
              <span className="absolute inset-0 rounded-2xl ring-1 ring-white/40" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="text-2xs font-mono uppercase tracking-[0.22em] text-fg-faint">
                esg.intel
              </span>
              <span className="font-serif text-lg text-fg-bright -mt-1 tracking-tight">
                Compliance Terminal
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {NAV.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  clsx(
                    "px-2.5 py-1.5 rounded-sm text-sm transition-colors duration-fast",
                    isActive
                      ? "text-fg-bright bg-ink-700"
                      : "text-fg-muted hover:text-fg"
                  )
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <Link to="/upload" className="hidden sm:inline-flex btn-ghost">
              Upload KPIs
            </Link>
            <Link to="/dashboard" className="btn-primary">
              Open Terminal →
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>

      <footer className="border-t border-line bg-white/60 mt-24">
        <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="col-span-2">
            <div className="text-xs font-mono uppercase tracking-widest text-fg-faint">
              esg.intel
            </div>
            <div className="text-fg-bright font-semibold">
              Compliance Terminal
            </div>
            <p className="text-sm text-fg-muted mt-2 max-w-sm">
              A production-grade ESG intelligence workstation built for analysts,
              risk teams, and sustainability officers operating under CSRD and
              ESRS.
            </p>
          </div>
          <div>
            <div className="field-label">Product</div>
            <ul className="space-y-1 text-sm">
              <li>
                <Link className="text-fg-muted hover:text-fg" to="/dashboard">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link className="text-fg-muted hover:text-fg" to="/upload">
                  Upload KPIs
                </Link>
              </li>
              <li>
                <Link className="text-fg-muted hover:text-fg" to="/companies">
                  Companies
                </Link>
              </li>
              <li>
                <Link className="text-fg-muted hover:text-fg" to="/copilot">
                  Copilot
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <div className="field-label">Company</div>
            <ul className="space-y-1 text-sm">
              <li>
                <Link className="text-fg-muted hover:text-fg" to="/about">
                  About
                </Link>
              </li>
              <li>
                <a
                  className="text-fg-muted hover:text-fg"
                  href="https://www.efrag.org/"
                  target="_blank"
                  rel="noreferrer"
                >
                  ESRS (EFRAG)
                </a>
              </li>
              <li>
                <a
                  className="text-fg-muted hover:text-fg"
                  href="https://www.unep.org/"
                  target="_blank"
                  rel="noreferrer"
                >
                  UN Environment
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-line">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between text-2xs text-fg-faint font-mono">
            <span>© esg.intel · demo build</span>
            <span>built for investor-grade disclosure workflows</span>
          </div>
        </div>
      </footer>
      <VerdantWidget />
    </div>
  );
}
