import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // legacy aliases (keep dashboard untouched)
        ink: {
          900: "#f2f5fb",
          850: "#ffffff",
          800: "#ffffff",
          750: "#f5f7fb",
          700: "#eef1f6",
          600: "#e5e9f0",
          500: "#d6dce6",
        },
        line: {
          DEFAULT: "#e4e8ef",
          strong: "#c8cdd8",
        },
        fg: {
          DEFAULT: "#141a27",
          muted: "#555e6e",
          faint: "#8892a3",
          bright: "#070c18",
        },
        accent: {
          DEFAULT: "#06b6d4",
          blue: "#2563eb",
          amber: "#d97706",
          red: "#ef4444",
          violet: "#7c3aed",
          emerald: "#10b981",
          teal: "#14b8a6",
          indigo: "#6366f1",
          rose: "#f43f5e",
        },
        sev: {
          info: "#2563eb",
          low: "#10b981",
          medium: "#d97706",
          high: "#ea580c",
          critical: "#dc2626",
        },
        canvas: "#f6f8fd",
        surface: "#ffffff",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: [
          "Instrument Serif",
          "ui-serif",
          "Georgia",
          "Cambria",
          "serif",
        ],
        mono: ["JetBrains Mono", "ui-monospace", "Menlo", "monospace"],
      },
      fontSize: {
        "2xs": "0.6875rem",
        "display-sm": ["2.5rem", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
        "display-md": ["3.5rem", { lineHeight: "1.02", letterSpacing: "-0.025em" }],
        "display-lg": ["5rem", { lineHeight: "0.98", letterSpacing: "-0.03em" }],
        "display-xl": ["7rem", { lineHeight: "0.95", letterSpacing: "-0.035em" }],
      },
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        panel:
          "0 1px 0 rgba(13,18,26,0.02), 0 0 0 1px rgba(13,18,26,0.03), 0 10px 30px -14px rgba(13,18,26,0.10)",
        card:
          "0 1px 0 rgba(13,18,26,0.02), 0 0 0 1px rgba(13,18,26,0.04), 0 24px 60px -28px rgba(13,18,26,0.18)",
        glow:
          "0 0 0 1px rgba(6,182,212,0.35), 0 0 22px -2px rgba(6,182,212,0.35)",
        halo:
          "0 0 60px -12px rgba(37,99,235,0.35), 0 0 80px -20px rgba(6,182,212,0.35)",
        inset: "inset 0 0 0 1px rgba(13,18,26,0.04)",
      },
      transitionDuration: {
        fast: "150ms",
        DEFAULT: "220ms",
      },
      transitionTimingFunction: {
        expo: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      backgroundImage: {
        "grid-dots":
          "radial-gradient(circle at 1px 1px, rgba(13,18,26,0.07) 1px, transparent 0)",
        "grid-dots-subtle":
          "radial-gradient(circle at 1px 1px, rgba(13,18,26,0.05) 1px, transparent 0)",
        "aurora":
          "radial-gradient(40% 50% at 20% 30%, rgba(6,182,212,0.22), transparent 60%), radial-gradient(40% 50% at 80% 20%, rgba(124,58,237,0.18), transparent 60%), radial-gradient(40% 60% at 60% 90%, rgba(16,185,129,0.20), transparent 60%)",
      },
      backgroundSize: {
        grid: "22px 22px",
      },
      keyframes: {
        "pulse-soft": {
          "0%,100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        "drift-x": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        "aurora-shift": {
          "0%,100%": { transform: "translate3d(0,0,0) scale(1)" },
          "50%": { transform: "translate3d(-3%,2%,0) scale(1.04)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        "drift-x": "drift-x 38s linear infinite",
        "aurora-shift": "aurora-shift 18s ease-in-out infinite",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        shimmer: "shimmer 1.2s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
