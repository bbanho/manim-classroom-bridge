# Manim × Classroom Bridge
## Open-Source Engineering Rules

> **Philosophy:** Requirements first. Code is intent captured, not the source of truth.
> **Golden rule:** Changing a requirement changes the `.md` AND the test. Always both.

---

## 1. Git — Always SSH
```bash
# ✅ Correct
git clone git@github.com:bbanho/manim-classroom-bridge.git
git remote set-url origin git@github.com:bbanho/manim-classroom-bridge.git

# ❌ Wrong
git clone https://github.com/bbanho/manim-classroom-bridge.git
```

## 2. Architecture — Hexagonal, strict
```
src/
├── domain/          ← Pure business logic. ZERO external imports.
├── ports/           ← Interfaces (what the domain needs)
├── adapters/        ← Implementations (outside the core)
│   ├── google/      ← Classroom, Drive APIs
│   ├── llm/         ← LLM providers (Gemini, OpenAI, Nexus)
│   ├── render/      ← Manim execution
│   └── cache/       ← Hash-based artifact cache
├── usecases/        ← Application orchestration (pure functions, typed)
└── main.py          ← Entry point (CLI/API)
```

**Rules:**
- `domain/` **never imports** from `adapters/` or `usecases/`
- `usecases/` imports from `domain/` + `ports/`, never from `adapters/`
- Adding a new ERP = new adapter. No domain changes.

## 3. Requirements Integrity
- Each `REQ-*` in `docs/REQUIREMENTS-TREE.md` must have a corresponding test
- Changing a requirement = update `.md` AND update test
- Tests are the **executable specification**

## 4. Quality Gates
```bash
# Type check
mypy src/

# Lint
ruff check src/ tests/

# Test
pytest tests/ -v

# All must pass before commit
```

## 5. Documentation
- ADRs in `docs/adr/ADR-NNN-title.md` before code
- Requirements in `docs/requirements/REQ-XXX.md`
- Diagrams in `docs/diagrams/` (Mermaid or PlantUML)
- README.md is the entry point — keep it updated

## 6. Secrets
- No hardcoded credentials
- Use `.env` (gitignored) + `python-dotenv`
- Google service account: `credentials.json` (gitignored)

## 7. No Cascading Debug
- If a generative model (LLM, Manim) produces wrong output, **fix the prompt/contract**, not the model
- Capture intent in tests, rewrite from scratch if needed
- Avoid fixing symptoms in loops

---

*Last updated: 2026-08-13*
