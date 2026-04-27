import clsx from "clsx";

export function Skeleton({
  className,
  h = "h-4",
  w = "w-full",
}: {
  className?: string;
  h?: string;
  w?: string;
}) {
  return <div className={clsx("skeleton rounded-sm", h, w, className)} />;
}

export function SkeletonRows({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} w={i % 2 ? "w-4/5" : "w-full"} />
      ))}
    </div>
  );
}
