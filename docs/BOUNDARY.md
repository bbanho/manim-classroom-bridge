# Manim × Classroom Bridge — Architecture Boundary

> **Created:** 2026-08-13  
> **Status:** Open Source (all adapters welcome)  
> **Rationale:** Core + ERP bridge are both open. External adapters are pluggable.

---

## 1. Open Core + Pluggable Adapters

```
┌─────────────────────────────────────────────────────────────────┐
│  manim-classroom-bridge (OPEN SOURCE — MIT)                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Domain    │  │   Ports     │  │  Adapters   │            │
│  │  (entities) │  │ (interfaces)│  │ (Google,    │            │
│  │             │  │             │  │  LLM, Cache, │            │
│  │             │  │             │  │  ERP[...])  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         ↓               ↓               ↓                      │
│  ┌─────────────────────────────────────────────┐               │
│  │           Use Cases (orchestration)         │               │
│  │  UC-01: generate_video                      │               │
│  │  UC-02: publish_to_classroom                │               │
│  │  UC-04: generate_quiz                       │               │
│  │  UC-06: handle_erp_appointment_event        │               │
│  └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Adapter Ecosystem

**Built-in adapters (this repo):**
- `adapters.google.*` — Drive, Classroom
- `adapters.llm.*` — Gemini, OpenAI, Nexus Gateway
- `adapters.render.*` — Manim local, Docker
- `adapters.cache.*` — Local filesystem, Drive
- `adapters.erp.*` — Amplainformática (clinical)

**External adapters (third-party, pluggable):**
- Anyone can implement `ERPPort` for their ERP
- Anyone can implement `LLMPort` for their LLM provider
- Anyone can implement `RendererPort` for their render backend

---

## 3. ERP Bridge — Open Source

UC-06 and `REQ-ERP-*` are part of the open-source core.

**Why open:**
- Algorithm is simple: map appointment_type → template → prompt → render
- Clinical workflow rules are not secret — they're standard medical practice
- Value is in the **integration**, not the logic
- Community can contribute adapters for other clinical systems

**What remains proprietary (if anything):**
- Specific patient data (obviously)
- Branding/customization for Amplainformática clients
- SLA/support contracts

---

## 4. Dependency Rule (still applies)

**Core NEVER imports concrete adapters directly.**

```python
# ✅ Core imports port interface
from ports import ERPPort

# ✅ Core uses adapters via dependency injection
usecase = handle_erp_appointment_event(
    erp=AmplainformaticaAdapter(),  # Injected at runtime
    ...
)

# ❌ Core never hardcodes adapter imports
```

This allows:
- Third parties to drop in their ERP adapter without forking core
- Clinical workflow to evolve independently
- Multiple ERP adapters to coexist

---

## 5. Distribution

| Component | License | PyPI Package |
|-----------|---------|--------------|
| Core + all built-in adapters | MIT | `manim-classroom-bridge` |
| Third-party adapters | Varies | Separate packages |

**Installation:**

```bash
# Install core + all built-in adapters
pip install manim-classroom-bridge

# Install third-party ERP adapter
pip install manim-classroom-bridge-erp-foo  # community adapter
```

---

## 6. UC-06 — Fully Open

| Use Case | Status | Location |
|----------|--------|----------|
| UC-01 | ✅ Planned | Open source |
| UC-02 | ✅ Planned | Open source |
| UC-03 | 🔵 Future | Open source |
| UC-04 | ✅ Planned | Open source |
| UC-05 | ✅ Planned | Open source |
| UC-06 | ✅ Open | Open source (was: proprietary) |

---

## 7. Design Principle

> **"Ideas already understood are not IP. Implementation details are."**

What's open:
- Clinical workflow rules (standard medical practice)
- ERP event structure (simple JSON)
- Template mapping logic (few tokens)
- Integration patterns

What's not in this repo (but could be):
- Production deployment configs for specific hospitals
- Branded UI themes
- Support contracts

---

*Revisado em 2026-08-13 — decisão revertida: ERP bridge é open source.*
