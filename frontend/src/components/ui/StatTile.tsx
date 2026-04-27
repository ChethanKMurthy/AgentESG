import clsx from "clsx";
import { ReactNode } from "react";

export function StatTile({
  label,
  value,
  unit,
  delta,
  hint,
  tone = "default",
  className,
}: {
  label: string;
  value: ReactNode;
  unit?: string;
  delta?: string;
  hint?: string;
  tone?: "default" | "good" | "warn" | "bad";
  className?: string;
}) {
  const toneColor = {
    default: "text-fg-bright",
    good: "text-accent",
    warn: "text-accent-amber",
    bad: "text-accent-red",
  }[tone];
  return (
    <div className={clsx("panel px-3 py-2.5", className)}>
      <div className="panel-title">{label}</div>
      <div className="flex items-baseline gap-2 mt-1.5">
        <div className={clsx("num-xl", toneColor)}>{value}</div>
        {unit && <div className="text-fg-faint text-xs mono">{unit}</div>}
      </div>
      {(delta || hint) && (
        <div className="mt-1 text-2xs text-fg-muted mono flex gap-2">
          {delta && <span>{delta}</span>}
          {hint && <span className="text-fg-faint">{hint}</span>}
        </div>
      )}
    </div>
  );
}
