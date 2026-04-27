import clsx from "clsx";
import { Link, NavLink } from "react-router-dom";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", key: "DSH" },
  { to: "/upload", label: "Upload KPI", key: "UPL" },
  { to: "/companies", label: "Companies", key: "CMP" },
];

export function Sidebar() {
  return (
    <aside className="hidden md:flex w-56 shrink-0 border-r border-line flex-col bg-ink-850">
      <Link
        to="/"
        className="px-3 py-3 border-b border-line block hover:bg-ink-750 transition-colors duration-fast"
      >
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-sm bg-gradient-to-br from-accent to-accent-blue flex items-center justify-center">
            <span className="text-white font-mono text-[10px]">E</span>
          </div>
          <div>
            <div className="font-mono text-2xs uppercase tracking-widest text-fg-faint">
              esg.intel
            </div>
            <div className="text-fg-bright text-sm font-semibold tracking-tight -mt-0.5">
              Terminal
            </div>
          </div>
        </div>
      </Link>
      <nav className="p-2 space-y-0.5 flex-1">
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              clsx("sidebar-link", isActive && "sidebar-link-active")
            }
          >
            <span className="font-mono text-2xs text-fg-faint w-8">{l.key}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-line text-2xs text-fg-faint font-mono space-y-1">
        <Link to="/" className="block hover:text-fg">
          ← back to home
        </Link>
        <div className="text-fg-muted">
          Verdant is always on station (bottom-right).
        </div>
      </div>
    </aside>
  );
}
