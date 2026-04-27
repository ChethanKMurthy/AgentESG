import { useEffect, useRef } from "react";

export function Aurora() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      el.style.setProperty("--x", `${x}%`);
      el.style.setProperty("--y", `${y}%`);
    };
    el.addEventListener("mousemove", onMove);
    return () => el.removeEventListener("mousemove", onMove);
  }, []);
  return (
    <div
      ref={ref}
      className="absolute inset-0 overflow-hidden spotlight"
      aria-hidden
    >
      <div className="aurora-layer" />
      <div className="absolute inset-0 bg-grid-dots-subtle bg-grid opacity-50" />
      <div
        className="absolute inset-x-0 -bottom-1 h-24"
        style={{
          background:
            "linear-gradient(to bottom, rgba(246,248,253,0) 0%, #f6f8fd 100%)",
        }}
      />
    </div>
  );
}
