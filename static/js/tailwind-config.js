tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: "#003366",
        "on-primary": "#ffffff",
        "primary-container": "#0d4d8c",
        secondary: "#1cbe70",
        "secondary-fixed": "#6bfe9c",
        "on-secondary-fixed": "#00210f",
        "surface-white": "#ffffff",
        "on-surface": "#1a1c1e",
        "on-surface-variant": "#43474e",
        outline: "#73777f",
        "outline-variant": "#c3c6cf",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f3f3f3",
        "rail-red": "#d92d20",
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
        body: ["Inter", "sans-serif"],
        label: ["Inter", "sans-serif"],
        headline: ["Inter", "sans-serif"],
      },
      fontSize: {
        "display-lg": ["3.5rem", { lineHeight: "1.1", fontWeight: "600" }],
        "headline-xl": ["1.75rem", { lineHeight: "1.3", fontWeight: "600" }],
        "headline-lg": ["1.375rem", { lineHeight: "1.3", fontWeight: "600" }],
        "body-lg": ["1.125rem", { lineHeight: "1.6" }],
        "body-md": ["1rem", { lineHeight: "1.5" }],
        "label-md": ["0.875rem", { lineHeight: "1.4", fontWeight: "600" }],
        "label-sm": ["0.75rem", { lineHeight: "1.3", fontWeight: "600" }],
      },
    },
  },
};