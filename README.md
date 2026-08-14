# Manim × Classroom Bridge

> **AI-generated educational videos → Google Classroom**

Open-source bridge that lets language models generate Manim CE animations from pedagogical prompts, render them headlessly, and publish to Google Classroom — with ERP integration for clinical appointment workflows.

---

## Status

**v0.1 — Foundation** | Use cases defined | Requirements decomposed | Domain scaffolded

See [docs/FOUNDATION.md](docs/FOUNDATION.md) and [docs/REQUIREMENTS-TREE.md](docs/REQUIREMENTS-TREE.md).

---

## Architecture

Hexagonal (ports & adapters). Pure domain, zero external imports in `src/domain/`.

```
src/
├── domain/          # Entities, value objects, business rules
├── ports/           # Interfaces (domain depends on these)
├── adapters/        # Implementations (Google, LLM, Render, Cache)
├── usecases/        # Orchestration layer
└── main.py          # Entry point
```

---

## Quick Start

```bash
# Clone
git clone git@github.com:bbanho/manim-classroom-bridge.git
cd manim-classroom-bridge

# Install
pip install -e ".[dev]"

# Run tests
pytest tests/

# Type check
mypy src/
```

---

## Use Cases

| UC | Description | Status |
|----|-------------|--------|
| UC-01 | Generate video from prompt | 🟡 Planned |
| UC-02 | Publish to Google Classroom | 🟡 Planned |
| UC-03 | Present in Google Meet | 🔵 Future |
| UC-04 | Auto-quiz after video | 🟡 Planned |
| UC-05 | Template reuse | 🟡 Planned |
| UC-06 | ERP event → video | 🟡 Planned |

---

## Tech Stack

- **Render:** Manim CE (headless Docker)
- **LLM:** Gemini/OpenAI via Nexus Gateway or direct
- **Storage:** Google Drive API
- **LMS:** Google Classroom API
- **Language:** Python 3.11+, typed, strict mypy
- **Tests:** pytest + pytest-asyncio

---

## Documentation

- [Foundation](docs/FOUNDATION.md) — Purpose, actors, use cases
- [Requirements Tree](docs/REQUIREMENTS-TREE.md) — Atomic requirements with dependency graph
- [ADR Index](docs/adr/) — Architecture Decision Records

---

## License

MIT
