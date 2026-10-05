/**
 * Resolve a public asset path against the configured Vite base.
 *
 * `import.meta.env.BASE_URL` is injected at build time and always ends with a
 * slash (default `/soundings/`). This keeps images, fonts and downloads working
 * both on the nested GitHub Pages path and at a future custom-domain root.
 */
export function assetUrl(path: string): string {
  const base = import.meta.env.BASE_URL || "/";
  return base.replace(/\/$/, "") + "/" + path.replace(/^\//, "");
}
