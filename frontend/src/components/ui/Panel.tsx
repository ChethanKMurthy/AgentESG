import clsx from "clsx";
import { ReactNode } from "react";

export function Panel({
  title,
  actions,
  className,
  children,
  dense = false,
}: {
  title?: ReactNode;
  actions?: ReactNode;
  className?: string;
  children: ReactNode;
  dense?: boolean;
}) {
  return (
    <section className={clsx("panel flex flex-col min-h-0", className)}>
      {(title || actions) && (
        <header className="panel-header">
          <div className="panel-title">{title}</div>
          <div className="flex items-center gap-2">{actions}</div>
        </header>
      )}
      <div className={clsx("min-h-0", dense ? "p-0" : "p-3")}>{children}</div>
    </section>
  );
}
