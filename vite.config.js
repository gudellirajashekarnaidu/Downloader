import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, /api requests go to the FastAPI server.
// In production, serve both from one domain or set VITE_API_BASE.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});
