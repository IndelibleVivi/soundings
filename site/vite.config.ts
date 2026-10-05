import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";

// Canonical production base for GitHub Pages: https://indeliblevivi.github.io/soundings/
// A future custom domain (served at the site root) can set VITE_SITE_BASE=/ .
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const base = env.VITE_SITE_BASE || "/soundings/";

  return {
    base,
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./", import.meta.url)),
      },
    },
    build: {
      outDir: "dist",
      emptyOutDir: true,
      assetsDir: "assets",
    },
  };
});
