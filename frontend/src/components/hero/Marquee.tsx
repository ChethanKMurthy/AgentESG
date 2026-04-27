const ITEMS = [
  "CSRD",
  "ESRS E1 · Climate",
  "ESRS E3 · Water",
  "ESRS E5 · Circularity",
  "ESRS S1 · Workforce",
  "ESRS G1 · Business conduct",
  "GHG Protocol Scope 1·2·3",
  "SBTi 1.5°C pathway",
  "SASB",
  "TCFD",
  "GRI",
  "IFRS S1·S2",
];

export function Marquee() {
  const row = [...ITEMS, ...ITEMS];
  return (
    <div className="relative overflow-hidden py-3 border-y border-line bg-white/60 backdrop-blur-md">
      <div className="absolute inset-y-0 left-0 w-24 z-10 pointer-events-none bg-gradient-to-r from-canvas to-transparent" />
      <div className="absolute inset-y-0 right-0 w-24 z-10 pointer-events-none bg-gradient-to-l from-canvas to-transparent" />
      <div className="flex gap-8 animate-drift-x whitespace-nowrap">
        {row.map((t, i) => (
          <span
            key={i}
            className="text-2xs font-mono uppercase tracking-widest text-fg-faint"
          >
            {t} <span className="mx-3 text-line-strong">/</span>
          </span>
        ))}
      </div>
    </div>
  );
}
