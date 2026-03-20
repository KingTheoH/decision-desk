import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      colors: {
        surface: {
          DEFAULT: "#111113",
          1: "#1a1a1f",
          2: "#222228",
          3: "#2a2a32",
        },
        border: {
          DEFAULT: "#2e2e38",
          subtle: "#232330",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
