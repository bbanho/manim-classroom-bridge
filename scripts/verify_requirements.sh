#!/usr/bin/env bash
set -euo pipefail

DOC="docs/REQUIREMENTS-TREE.md"

if [ ! -f "$DOC" ]; then
  echo "Missing $DOC"
  exit 1
fi

# Extract all REQ-IDs from docs
DOC_IDS=$(grep -oE 'REQ-[A-Z]+-[0-9]+' "$DOC" | sort -u)

# Extract all REQ-IDs from source/tests
CODE_IDS=$(grep -rohE 'REQ-[A-Z]+-[0-9]+' src/ tests/ | sort -u)

# Check every code ID exists in docs
missing=0
for id in $CODE_IDS; do
  if ! echo "$DOC_IDS" | grep -q "$id"; then
    echo "❌ REQ ID in code but not in docs: $id"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  exit 1
fi

echo "✅ Docs integrity OK — $(echo "$CODE_IDS" | wc -l) requirement IDs verified."
