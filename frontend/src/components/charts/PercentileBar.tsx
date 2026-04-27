import clsx from "clsx";

export function PercentileBar({
  value,
  direction = "higher",
  className,
}: {
  value: number | null;
  direction?: "higher" | "lower" | string;
  className?: string;
}) {
  if (value === null || value === undefined)
    return <div className={clsx("text-fg-faint text-2xs", className)}>n/a</div>;

  const isLeader = direction === "higher" ? value >= 75 : value <= 25;
  const isLaggard = direction === "higher" ? value <= 25 : value >= 75;
  const color = isLeader ? "bg-accent" : isLaggard ? "bg-accent-red" : "bg-accent-blue";

  return (
    <div className={clsx("w-full flex items-center gap-2", className)}>
      <div className="flex-1 h-1.5 bg-ink-700 rounded-sm relative overflow-hidden">
        <div
          className={clsx("h-full", color)}
          style={{ width: `${Math.max(2, Math.min(100, value))}%` }}
        />
        <div className="absolute inset-y-0 left-1/2 w-px bg-ink-600" />
      </div>
      <div className="mono text-2xs w-10 text-right text-fg-muted">
        {value.toFixed(0)}
      </div>
    </div>
  );
}
