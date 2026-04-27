export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-6 text-center">
      <div className="text-fg-muted text-sm">{title}</div>
      {hint && <div className="text-fg-faint text-xs mt-1 max-w-sm">{hint}</div>}
    </div>
  );
}
