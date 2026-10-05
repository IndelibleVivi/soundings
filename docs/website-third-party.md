# Website third-party material

The website's original material remains subject to [LICENSING.md](../LICENSING.md)'s existing rule for unlisted files. Publishing it does not add a new public reuse grant or change the plugin and documentation licenses.

| Material | Source and continuing terms | Notice |
| --- | --- | --- |
| Jiandi Song Regular / Medium WOFF subsets | Renamed subsets of Adobe Source Han Serif SC 2.003; SIL Open Font License 1.1, reserved name “Source” | [OFL text](../site/public/fonts/OFL.txt), [source record](../site/public/fonts/SOURCES.json) |
| Jiandi Kai Regular / Medium WOFF subsets | Renamed subsets of LXGW WenKai 1.522, derived from Klee; SIL Open Font License 1.1 | [OFL text](../site/public/fonts/OFL-WenKai.txt), [source record](../site/public/fonts/KAI-SOURCES.json) |
| Incorporated shadcn UI wrappers and theme CSS | shadcn/ui, MIT, copyright 2023 shadcn | [MIT notice](../site/vendor/shadcn-tailwind-4.13.0.LICENSE.md) |
| react-remove-scroll-bar notice | Its npm tarball omits the license file; MIT notice retained from [upstream commit 7301c16](https://github.com/theKashey/react-remove-scroll-bar/blob/7301c160fda44cb8cf2b9fdfde61efad35736196/LICENSE) | [retained MIT notice](../site/vendor/react-remove-scroll-bar.LICENSE.txt) |
| npm runtime dependencies and incorporated CSS | Their own package licenses and copyright notices; exact versions are recorded in the website lockfile | [package manifest](../site/package.json), [lockfile](../site/package-lock.json); the build retains full package notices in `THIRD_PARTY_NOTICES.txt` |

The garden, reading-album, unfolding-map, magnolia-and-bird, and lotus paintings are original AI-generated illustrations. They do not incorporate historical museum scans. They receive no additional license through this publication. A visual reference does not supply permission to redistribute an unrelated reference image.

Font changes must retain the OFL notice and use the renamed subset family. Keep third-party notices with future copies or changes to incorporated material; project license terms do not replace those continuing terms.

The production build serves `THIRD_PARTY_NOTICES.txt` alongside the website. Its notice generator reads installed packages pinned by the lockfile; it does not confer a license on original website material.
