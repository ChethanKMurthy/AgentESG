import clsx from "clsx";

export function VerdantAvatar({
  size = 40,
  className,
  ring = false,
}: {
  size?: number;
  className?: string;
  ring?: boolean;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center rounded-full overflow-hidden shrink-0 relative",
        ring && "ring-2 ring-accent/50 ring-offset-2 ring-offset-white",
        className
      )}
      style={{ width: size, height: size }}
      aria-label="Agent Verdant"
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="v-bg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0b1220" />
            <stop offset="100%" stopColor="#1e293b" />
          </linearGradient>
          <linearGradient id="v-suit" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#020617" />
          </linearGradient>
          <linearGradient id="v-accent" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
          <radialGradient id="v-glow" cx="50%" cy="20%" r="60%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Background circle */}
        <circle cx="32" cy="32" r="32" fill="url(#v-bg)" />
        <circle cx="32" cy="32" r="32" fill="url(#v-glow)" />

        {/* Subtle grid overlay */}
        <g stroke="#ffffff" strokeOpacity="0.04">
          <line x1="0" y1="20" x2="64" y2="20" />
          <line x1="0" y1="44" x2="64" y2="44" />
          <line x1="20" y1="0" x2="20" y2="64" />
          <line x1="44" y1="0" x2="44" y2="64" />
        </g>

        {/* Suit shoulders */}
        <path
          d="M6 62 C 10 48, 22 44, 32 44 C 42 44, 54 48, 58 62 L 58 64 L 6 64 Z"
          fill="url(#v-suit)"
        />
        {/* Lapels */}
        <path
          d="M26 45 L 32 54 L 38 45 L 35 60 L 32 56 L 29 60 Z"
          fill="#e5e7eb"
          fillOpacity="0.92"
        />
        {/* Shirt triangle */}
        <path d="M30 46 L 32 53 L 34 46 Z" fill="#f8fafc" />
        {/* Bow tie */}
        <path
          d="M28 48 L 32 51 L 36 48 L 36 52 L 32 50 L 28 52 Z"
          fill="url(#v-accent)"
        />
        <circle cx="32" cy="50" r="0.9" fill="#0b1220" />

        {/* Head */}
        <circle cx="32" cy="30" r="11" fill="#e5c4a3" />
        {/* Jaw shadow */}
        <path
          d="M23 34 Q 32 40 41 34 Q 38 42 32 42 Q 26 42 23 34 Z"
          fill="#000"
          fillOpacity="0.08"
        />
        {/* Hair */}
        <path
          d="M22 26 Q 24 16 32 16 Q 40 16 42 26 Q 40 22 36 22 Q 32 20 28 22 Q 24 22 22 26 Z"
          fill="#1f2937"
        />
        {/* Brows */}
        <rect x="26" y="27" width="4" height="1" rx="0.5" fill="#111827" />
        <rect x="34" y="27" width="4" height="1" rx="0.5" fill="#111827" />
        {/* Eyes */}
        <circle cx="28" cy="30" r="0.9" fill="#0f172a" />
        <circle cx="36" cy="30" r="0.9" fill="#0f172a" />
        {/* Mouth */}
        <path
          d="M28.5 35 Q 32 36.2 35.5 35"
          stroke="#7f1d1d"
          strokeWidth="0.9"
          strokeLinecap="round"
          fill="none"
        />
        {/* Earpiece */}
        <circle cx="42.2" cy="30" r="1" fill="#0b1220" />
        <path
          d="M42.5 31 Q 44 34 43 38"
          stroke="#0b1220"
          strokeWidth="0.8"
          fill="none"
        />
      </svg>
    </span>
  );
}
