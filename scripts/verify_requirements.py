#!/usr/bin/env python3
"""Verify that every REQ-* ID in source/tests exists in docs/REQUIREMENTS-TREE.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOC = Path("docs/REQUIREMENTS-TREE.md")

if not DOC.exists():
    print(f"❌ Missing {DOC}")
    sys.exit(1)

doc_text = DOC.read_text()
code_files = list(Path("src").rglob("*.py")) + list(Path("tests").rglob("*.py"))

doc_ids = set(re.findall(r"REQ-[A-Z]+-\d+", doc_text))
code_ids = set()

for f in code_files:
    text = f.read_text()
    code_ids.update(re.findall(r"REQ-[A-Z]+-\d+", text))

missing = []
for req_id in sorted(code_ids):
    if req_id not in doc_ids:
        missing.append(req_id)

if missing:
    print("❌ REQ IDs in code but missing from docs:")
    for m in missing:
        print(f"   {m}")
    sys.exit(1)

print(f"✅ Docs integrity OK — {len(code_ids)} requirement IDs verified.")
