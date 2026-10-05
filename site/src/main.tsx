import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { assetUrl } from "../lib/base";

// Order matters: vendor/shadcn theme layer first, then the courtyard base,
// then the R4 terrain layer, then page-specific refinements.
import "../app/globals.css";
import "../app/courtyard.css";
import "../app/terrain.css";
import "../app/refinement.css";

import Soundings from "../app/soundings";

// Inject the self-hosted font faces with base-aware URLs so the subsets keep
// working under the nested GitHub Pages path and at a future custom-domain root.
const fontFaces = document.createElement("style");
fontFaces.textContent = [
  `@font-face{font-family:'Jiandi Song';src:url('${assetUrl("fonts/jiandi-song-regular.woff")}') format('woff');font-weight:400;font-style:normal;font-display:swap}`,
  `@font-face{font-family:'Jiandi Song';src:url('${assetUrl("fonts/jiandi-song-medium.woff")}') format('woff');font-weight:500 700;font-style:normal;font-display:swap}`,
].join("\n");
document.head.appendChild(fontFaces);

const container = document.getElementById("root");
if (!container) throw new Error("Missing #root mount node");

createRoot(container).render(
  <StrictMode>
    <Soundings />
  </StrictMode>
);
