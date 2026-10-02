/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Primary gold palette
        gold: {
          50: "#FBF8F0",
          100: "#F5EDDD",
          200: "#EBD9B8",
          300: "#DFC28A",
          400: "#D4AF37",
          500: "#C9A961",
          600: "#B8860B",
          700: "#966C0E",
          800: "#7A5711",
          900: "#5F4214",
          950: "#3A2808",
        },
        // Warm neutral palette
        cream: {
          50: "#FEFCF8",
          100: "#FBF8F3",
          200: "#F5EDDD",
          300: "#E8DCC5",
          400: "#D4C4A8",
          500: "#B8A689",
          600: "#8B7355",
          700: "#6B5842",
          800: "#4A3C2D",
          900: "#2D251B",
        },
        primary: {
          50: "#FBF8F0",
          100: "#F5EDDD",
          200: "#EBD9B8",
          300: "#DFC28A",
          400: "#D4AF37",
          500: "#C9A961",
          600: "#B8860B",
          700: "#966C0E",
          800: "#7A5711",
          900: "#5F4214",
          950: "#3A2808",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        serif: ["Playfair Display", "Georgia", "serif"],
        mono: ["JetBrains Mono", "Menlo", "Monaco", "Courier New", "monospace"],
      },
      backgroundImage: {
        "gold-gradient":
          "linear-gradient(135deg, #FBF8F0 0%, #F5EDDD 50%, #EBD9B8 100%)",
        "gold-radial":
          "radial-gradient(at 30% 20%, rgba(212, 175, 55, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(201, 169, 97, 0.12) 0px, transparent 50%), radial-gradient(at 0% 80%, rgba(184, 134, 11, 0.08) 0px, transparent 50%)",
        "gold-shine":
          "linear-gradient(90deg, transparent 0%, rgba(212, 175, 55, 0.4) 50%, transparent 100%)",
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "fade-in-slow": "fadeIn 0.7s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
        "slide-in-right": "slideInRight 0.4s ease-out",
        "scale-in": "scaleIn 0.25s ease-out",
        "float-slow": "floatSlow 8s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        "shine": "shine 3s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(16px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideDown: {
          "0%": { transform: "translateY(-16px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideInRight: {
          "0%": { transform: "translateX(16px)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.96)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        floatSlow: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-12px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        glowPulse: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        shine: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      boxShadow: {
        gold: "0 4px 20px rgba(212, 175, 55, 0.25)",
        "gold-lg": "0 8px 40px rgba(212, 175, 55, 0.35)",
        "gold-inner": "inset 0 1px 0 0 rgba(255, 255, 255, 0.6)",
        cream: "0 4px 20px rgba(139, 115, 85, 0.1)",
        "cream-lg": "0 12px 48px rgba(139, 115, 85, 0.15)",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};