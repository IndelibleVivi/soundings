# Soundings website (`site/`)

The public bilingual website for the Soundings Codex plugin. It is a static
React + TypeScript + Vite build with no backend, no server rendering, and no
connector or authentication runtime. GitHub Pages serves the built output under
the nested base path `/soundings/`.

The site presents the plugin and its four independent methods (Search 访求,
Study 会通, Explore 营造, Shape 辨定). It does not own Skill behavior and does
not establish behavior acceptance.

## Local development

```bash
cd site
npm ci          # install the pinned toolchain (Node 24+; Node 26 works locally)
npm run dev     # Vite dev server with hot reload
```

## Build and verification

```bash
npm run typecheck  # tsc -b, project references (no emit)
npm run build      # vite build -> site/dist
npm run check      # typecheck + build + distribution notices
npm run preview    # serve the production build after building it
```

`site/dist/` is generated static output and stays untracked. `npm run check` is
the provider-neutral verification entrypoint used by
`.github/workflows/pages.yml`. `npm ci` requires the committed
`site/package-lock.json`; use `npm install` only when deliberately updating dependencies and the lockfile.

## Deployment contract

- Build output: `site/dist`.
- Canonical base: `/soundings/` (see `base` in `vite.config.ts`).
- Custom-domain override: set `VITE_SITE_BASE=/` for a build served at a site
  root. Reconcile the build base and the public metadata (`index.html`
  canonical/OG URLs) together when moving to a custom domain.
- All image, font, favicon and download URLs are resolved against
  `import.meta.env.BASE_URL` (via `lib/base.ts`), so they keep working at the
  nested Pages base.
- Publishing is a separate fact from a successful local build. A green
  `npm run check` does not by itself prove Pages deployment or runtime behavior.

## Publish and verify

GitHub Pages uses **GitHub Actions** as its build source (repository Settings →
Pages → Build and deployment). The `website` workflow builds on changes to
`site/` or its workflow on `main`, and can also be run through Actions → website
→ Run workflow. Pull requests build without publishing.

Run `npm run check` and inspect the production preview before pushing. After
publishing, confirm both jobs succeeded and open
[the public website](https://indeliblevivi.github.io/soundings/). Check the nested
asset paths, Chinese/English switch, method entrances, and reading dialog on the
live host. To restore an earlier published version, revert the relevant source
change and let the same workflow rebuild; do not manually edit `dist/`.

## Project-relative path map

- `index.html` — static document shell: title, description, canonical,
  OG/Twitter metadata, favicon.
- `src/main.tsx` — React entry; mounts `app/soundings.tsx` and imports the CSS
  layers in order.
- `app/soundings.tsx` — page composition: header, method sections, reading room,
  about, start, footer, reading dialog.
- `app/garden-terrain.tsx` — the oblique whole-garden hero and its four landmark
  entry points.
- `app/garden-architecture.tsx` — shared SVG architecture: lattice, method
  glyphs, interactive porch, quiet window.
- `app/garden-scenes.tsx` — the four fixed method demonstrations
  (Search/Explore/Shape).
- `app/study-evidence.tsx` — the fixed Study demonstration.
- `components/ui/` — vendored shadcn/ui wrappers (tabs, dialog, slider, button).
- `lib/` — base-URL helper, copy-to-clipboard helper, class merge helper.
- `app/globals.css` — Tailwind + shadcn theme tokens.
- `app/courtyard.css` — base layout/presentation for the garden composition.
- `app/terrain.css` — R4 terrain layer: the whole-garden scale and method scenes.
- `app/refinement.css` — architectural/book refinement layer, loaded last.
- `public/assets/` — paintings and method glyph SVGs.
- `public/fonts/` — self-hosted subset fonts and their OFL sources.
- `public/favicon.svg` — site favicon.
- `scripts/third-party-notices.mjs` — retains third-party notices in the static build.
- `scripts/subset-brand-fonts.py` — rebuilds the subset fonts from the licensed
  originals.
- `vendor/` — bundled shadcn/tailwind stylesheet and its MIT notice.

## Design commitments

The whole oblique garden is the visual centre, not a hero image beside ordinary
sections. Garden identity carries through the header, method navigation, prompt
sheets, the bound album leaves of the reading room, the album reading dialog,
and the desk controls. Details are original and code-native (CSS/SVG/HTML): slim
lattice joinery, hung paper title slips, stitched spines, folded source sheets,
deliberate album margins, and restrained roof/water/botanical motifs at section
transitions. No detail claims historical authority or imitates a seal. See
[website design](../docs/website-design.md) for the accepted visual commitments.

The final logo remains a candidate; the marks shipped are functional joinery.

## Self-hosted fonts

The Chinese reading font is **Jiandi Song**, a renamed, content-subset build of
Adobe Source Han Serif SC 2.003 (Regular and Medium).

- License: SIL Open Font License 1.1, retained in `public/fonts/OFL.txt`.
- Sources, byte sizes and SHA-256 hashes: `public/fonts/SOURCES.json`.
- Requested family names avoid the reserved name "Source" per the OFL.
- Rebuild with `python3 scripts/subset-brand-fonts.py /path/to/original-fonts`
  after adding new Chinese text (requires fontTools); the script scans the site source for the glyph
  set and writes `public/fonts/jiandi-song-{regular,medium}.woff`.

## Bundled stylesheet notice

The vendored stylesheet in `vendor/shadcn-tailwind-4.13.0.css` and the adapted
components in `components/ui/` derive from shadcn/ui (MIT). The MIT notice is
retained in `vendor/shadcn-tailwind-4.13.0.LICENSE.md`.

Runtime dependencies bundled into the static artifact (React, React DOM,
radix-ui, lucide-react, class-variance-authority, clsx, tailwind-merge) carry
their own package licenses and copyright notices, retained in the generated `dist/THIRD_PARTY_NOTICES.txt` and pinned in
`package-lock.json`. The build also retains the notices for incorporated
Tailwind CSS, `tw-animate-css`, shadcn UI, and the fonts. See [third-party material](../docs/website-third-party.md).

Publication of this site does not add or expand any public license grant. See
[the repository rights map](../LICENSING.md); unlisted files remain all rights reserved
unless a file-level notice says otherwise.

## Fixed-example limits

The four demonstrations and both reading-room cases are **fixed, constructed
examples**. They:

- do not run a live model, retrieval engine, or agent;
- do not prove plugin acceptance, trigger quality, or real task outcomes;
- preserve their explicit qualifications in the interface;
- are shown for illustration and are edited as source, not generated live.

Timing and enjoyment claims (for example, the six-minute paper activity) have
not been tested with human players; the interface says so where relevant.
