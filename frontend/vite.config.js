import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuration for the Vite development server
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy setup to seamlessly route API calls from the frontend to the FastAPI backend
    proxy: {
      // If the frontend calls an endpoint starting with '/api', it gets routed to the backend
      "/api": {
        target: "http://localhost:8000", // FastAPI runs here
        changeOrigin: true,
        secure: false,
        // The LoginPage.jsx uses API_BASE_URL = "http://localhost:8000/api/v1"
        // This rewrite simplifies paths if you wish to use just '/v1' later.
        // For now, it routes '/api/v1' to 'http://localhost:8000/api/v1'.
        // No rewrite needed if using the full URL in the frontend code.
      },
    },
  },
});
