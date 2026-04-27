import clsx from "clsx";
import { ReactNode } from "react";

const sevMap: Record<string, string> = {
  info: "text-sev-info border-sev-info/40 bg-sev-info/10",
  low: "text-sev-low border-sev-low/40 bg-sev-low/10",
  medium: "text-sev-medium border-sev-medium/40 bg-sev-medium/15",
  high: "text-sev-high border-sev-high/50 bg-sev-high/15",
  critical: "text-sev-critical border-sev-critical/60 bg-sev-critical/15",
  leader: "text-sev-low border-sev-low/40 bg-sev-low/10",
  laggard: "text-accent-red border-accent-red/40 bg-accent-red/10",
  peer: "text-fg-muted border-line bg-white",
  ok: "text-sev-low border-sev-low/40 bg-sev-low/10",
  error: "text-accent-red border-accent-red/40 bg-accent-red/10",
};

export function Badge({
  children,
  tone = "peer",
  className,
}: {
  children: ReactNode;
  tone?: string;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "chip",
        sevMap[tone] || sevMap.peer,
        "uppercase",
        className
      )}
    >
      {children}
    </span>
  );
}
