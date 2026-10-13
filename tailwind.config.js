/** Design tokens: Samsung Digital Wellbeing-style light mode. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F4F5F7", // page background, soft grey
        surface: "#FFFFFF", // cards
        ink: "#17191C", // primary text
        muted: "#5B6370", // secondary text
        track: "#E6E9EE", // ring track and dividers
        brand: { DEFAULT: "#1F6FEB", light: "#3E91FF", cyan: "#0A9AD0" },
        danger: "#C93434",
      },
      fontFamily: {
        sans: ["Figtree", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
      },
      borderRadius: { card: "28px" },
      boxShadow: { card: "0 1px 2px rgba(23,25,28,0.05), 0 10px 28px -16px rgba(23,25,28,0.12)" },
    },
  },
  plugins: [],
};
