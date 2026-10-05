import { readFile, readdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
// This published npm tarball omits its license file. Retain the upstream notice.
const retainedLicenses = { "react-remove-scroll-bar": "vendor/react-remove-scroll-bar.LICENSE.txt" };
const lock = JSON.parse(await readFile(path.join(root, "package-lock.json"), "utf8"));
// Include the runtime dependency tree and the two incorporated CSS packages.
const packages = Object.entries(lock.packages).filter(([location, entry]) =>
  location && (!entry.dev || ["node_modules/tailwindcss", "node_modules/tw-animate-css"].includes(location))
);
const notices = ["Soundings website — third-party notices\nOriginal website material is governed by the repository's LICENSING.md. These notices preserve the terms of incorporated third-party material.\n"];
for (const [location] of packages) {
  const directory = path.join(root, location);
  const manifest = JSON.parse(await readFile(path.join(directory, "package.json"), "utf8"));
  const files = (await readdir(directory)).filter(name => /^(licen[sc]e|notice)(\.|$)/i.test(name)).sort();
  notices.push(`\n${"=".repeat(72)}\n${manifest.name} ${manifest.version} (${manifest.license})\n`);
  if (!files.length) {
    if (!retainedLicenses[manifest.name]) throw new Error(`Missing license notice for ${manifest.name}`);
    notices.push(await readFile(path.join(root, retainedLicenses[manifest.name]), "utf8"));
  }
  for (const file of files) notices.push(await readFile(path.join(directory, file), "utf8"));
}
notices.push("\n" + "=".repeat(72) + "\nAdapted shadcn UI components and theme CSS\n", await readFile(path.join(root, "vendor/shadcn-tailwind-4.13.0.LICENSE.md"), "utf8"));
notices.push("\n" + "=".repeat(72) + "\nJiandi Song — renamed Adobe Source Han Serif subsets\n", await readFile(path.join(root, "public/fonts/OFL.txt"), "utf8"));
await writeFile(path.join(root, "dist/THIRD_PARTY_NOTICES.txt"), notices.join("\n"));
console.log(`Retained ${packages.length} package notices, shadcn MIT and font OFL in dist/THIRD_PARTY_NOTICES.txt`);
