import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
    "./store/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        panel: "hsl(var(--panel))",
        panelAlt: "hsl(var(--panel-alt))",
        border: "hsl(var(--border))",
        accent: "hsl(var(--accent))",
        accentForeground: "hsl(var(--accent-foreground))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
        info: "hsl(var(--info))"
      },
      boxShadow: {
        glow: "0 0 0 1px hsl(var(--accent) / 0.4), 0 0 24px hsl(var(--accent) / 0.2)",
        danger: "0 0 0 1px hsl(var(--danger) / 0.4), 0 0 20px hsl(var(--danger) / 0.2)"
      },
      keyframes: {
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 0 0 hsl(var(--accent) / 0.4)" },
          "50%": { boxShadow: "0 0 0 8px hsl(var(--accent) / 0)" }
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" }
        }
      },
      animation: {
        pulseGlow: "pulseGlow 2s infinite",
        shimmer: "shimmer 1.6s infinite"
      }
    }
  },
  plugins: []
};

export default config;
