#!/bin/sh
# Documentation tooling only. Requires an operator-installed Mermaid CLI (mmdc).
# This script does not install packages, contact services or change runtime code.
set -eu
cd "$(dirname "$0")"
command -v mmdc >/dev/null 2>&1 || { echo "Install Mermaid CLI in your documentation environment first." >&2; exit 1; }
for source in 01-responsibilities 02-evidence 03-installation; do
  mmdc -i "$source.mmd" -o "$source.svg" -c mermaid-config.json -b '#F7F5EF'
done
