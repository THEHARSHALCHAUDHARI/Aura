import type { Config } from "tailwindcss";

export default {
  content: [
    "../../apps/**/*.{ts,tsx,js,jsx}",
    "../../packages/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
