import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      // ── Color Palette ────────────────────────────────────────────
      colors: {
        // Primary brand — electric indigo (accent)
        primary: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        // Accent — emerald (secondary highlights)
        accent: {
          50:  "#ecfdf5",
          100: "#d1fae5",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
        },
        // Surface — pure white base for B&W theme
        surface: {
          50:  "#ffffff",
          100: "#fafafa",
          200: "#f4f4f5",
          300: "#e4e4e7",
          400: "#d4d4d8",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b",
        },
        // Border system
        border: {
          DEFAULT: "#e4e4e7",
          strong:  "#d4d4d8",
        },
      },

      // ── Typography ────────────────────────────────────────────────
      fontFamily: {
        sans:    ["Inter", "system-ui", "sans-serif"],
        display: ["Outfit", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "Fira Code", "monospace"],
      },

      // ── Animations ────────────────────────────────────────────────
      animation: {
        "fade-in":    "fadeIn 0.4s ease-out forwards",
        "slide-up":   "slideUp 0.4s ease-out forwards",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow":  "spin 3s linear infinite",
        "gradient-x": "gradientX 8s ease infinite",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to:   { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(16px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        gradientX: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%":      { backgroundPosition: "100% 50%" },
        },
      },

      // ── Box shadows ───────────────────────────────────────────────
      boxShadow: {
        // Crisp, minimal shadows for white/light surfaces
        card:      "0 1px 3px 0 rgba(0,0,0,0.08), 0 1px 2px -1px rgba(0,0,0,0.06)",
        "card-md": "0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.06)",
        "card-lg": "0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.06)",
        glow:      "0 0 20px rgba(99, 102, 241, 0.3)",
        "glow-sm": "0 0 10px rgba(99, 102, 241, 0.2)",
        // Legacy (for any remaining dark references)
        glass:     "0 1px 3px 0 rgba(0,0,0,0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
