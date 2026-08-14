# OSS Landscape — Manim + LLM + Classroom
## Research: 2026-08-13

> **Method:** GitHub API search + local repo inspection
> **Query terms:** `manim llm generation`, `google classroom api`, `manim render automation docker`
> **Scope:** Top 10 results per query, filtered by relevance

---

## 1. Existing Projects

### 1.1 manim-generator ⭐113 (makefinks)
**URL:** https://github.com/makefinks/manim-generator  
**Lang:** Python | **Updated:** 2026-08-11  
**License:** None specified  
**Topics:** agents, ai, anthropic, deepseek-r1, gemini, llms, manim, openai

**What it does:**
- Automatic LLM-based video generation using Manim
- Code-writer + code-reviewer feedback loop with execution logs
- Supports multiple LLM providers (Gemini, OpenAI, Anthropic, DeepSeek)

**Strengths:**
- Active development (updated 2 days ago)
- Multi-provider support
- Feedback loop architecture (writer + reviewer)

**Gaps vs our project:**
- No Google Classroom/Drive integration
- No hexagonal architecture
- No ERP integration
- No cache/idempotency layer
- No quiz generation
- No template system

**Reusability:** Medium — we can learn from the writer/reviewer pattern

---

### 1.2 text2manim ⭐3 (KinjiKawaguchi)
**URL:** https://github.com/KinjiKawaguchi/text2manim  
**Lang:** Python | **Updated:** 2026-08-03  
**License:** None specified

**What it does:**
- CLI + Python library + stateless API server
- Sandboxed rendering
- Self-repairing generation loop

**Strengths:**
- Sandboxed execution (security)
- Self-repairing loop (resilience)
- API server design (reusability)

**Gaps vs our project:**
- No Google integration
- No educational workflow
- No Classroom publish
- No ERP bridge

**Reusability:** High — sandboxed rendering + self-repair loop are directly applicable

---

### 1.3 EduVids ⭐7 (namanbnsl)
**URL:** https://github.com/namanbnsl/eduvids  
**Lang:** TypeScript | **Updated:** 2026-07-23  
**License:** MIT

**What it does:**
- AI-generated educational videos with Manim
- Free, no sign-up required
- Web interface

**Strengths:**
- MIT license (permissive)
- Web UI exists
- Focused on education

**Gaps vs our project:**
- No Google Classroom integration
- TypeScript stack (we chose Python)
- No ERP bridge
- No hexagonal architecture

**Reusability:** Low — different stack, but UI patterns could inspire

---

### 1.4 EduVid-LLM ⭐4 (gokul6350)
**URL:** https://github.com/gokul6350/EduVid-LLM  
**Lang:** Python | **Updated:** 2026-01-29  
**License:** None specified  
**Topics:** ai, educational-software, llm, manim, python, research-project, video

**What it does:**
- Planning-centric architecture for automated educational video generation
- Research project

**Strengths:**
- Academic rigor
- Planning-centric approach (scene decomposition)

**Gaps vs our project:**
- Stale (last updated 6 months ago)
- No Google integration
- Research-only, not production-ready

**Reusability:** Medium — planning-centric architecture could inform our prompt engineering

---

### 1.5 ManimMathVideoGenerator ⭐5 (Shub500)
**URL:** https://github.com/Shub500/ManimMathVideoGenerator  
**Lang:** Jupyter Notebook | **Updated:** 2026-06-08  
**License:** None specified

**What it does:**
- Fine-tuned LLM for explanatory math video generation
- Notebook-based workflow

**Strengths:**
- Fine-tuned model (domain-specific)
- Math focus (our use case includes math)

**Gaps vs our project:**
- Jupyter-only (not productionizable)
- No Google integration
- No deployment workflow

**Reusability:** Low — fine-tuning approach is interesting but not directly applicable

---

### 1.6 manim-gpt ⭐4 (ajha-dev)
**URL:** https://github.com/ajha-dev/manim-gpt  
**Lang:** Not specified | **Updated:** Unknown

**What it does:**
- AI-Powered Manim Video Generation
- Transform text prompts into mathematical animations

**Strengths:**
- Simple concept
- Focus on math

**Gaps vs our project:**
- No details available
- No Google integration
- No production features

**Reusability:** Low

---

### 1.7 enginimate ⭐1 (MSVelan)
**URL:** https://github.com/MSVelan/enginimate  
**Lang:** Python | **Updated:** 2026-02-02  
**License:** None specified

**What it does:**
- Automated prompt-to-Manim video generation
- Multi-agent LLM orchestration
- Website: https://enginimate.vercel.app/

**Strengths:**
- Multi-agent orchestration
- Web demo exists

**Gaps vs our project:**
- Very low adoption (1 star)
- No Google integration
- No production features

**Reusability:** Low

---

## 2. Google Classroom API Ecosystem

### 2.1 teach-online ⭐9 (WBWeb)
**URL:** https://github.com/WBWeb/teach-online  
**License:** None specified

**What it does:**
- Complete solution for online teaching
- Powered by Google Classroom APIs + YouTube APIs
- 0 server cost (serverless)

**Strengths:**
- Classroom API integration exists
- YouTube integration (video delivery)
- Serverless architecture

**Gaps vs our project:**
- No Manim generation
- YouTube-centric (not Drive)
- No ERP integration

**Reusability:** Medium — Classroom API patterns are directly applicable

---

### 2.2 google-classroom-cli ⭐5 (gmurayama)
**URL:** https://github.com/gmurayama/google-classroom-cli  
**Lang:** Python | **Updated:** Unknown

**What it does:**
- CLI tool to automate tasks via Google Classroom API

**Strengths:**
- Python (our stack)
- CLI design

**Gaps vs our project:**
- No Manim integration
- No video generation

**Reusability:** Low — API wrapper only

---

### 2.3 Classroom-Downloader ⭐5 (sauriol)
**URL:** https://github.com/sauriol/Classroom-Downloader  
**Lang:** Python | **Updated:** Unknown

**What it does:**
- Download all file submissions from Google Classroom assignments
- Drive + Classroom API integration

**Strengths:**
- Drive + Classroom API combined
- Python

**Gaps vs our project:**
- Read-only (download, not upload/publish)
- No Manim integration

**Reusability:** Medium — Drive + Classroom API patterns are applicable

---

## 3. Local Repo Inspection

### 3.1 agent-lisp-animation (local)
**Path:** `/var/home/bruno/repos/agent-lisp-animation/`  
**Files:** `agent_lisp_core.py`, `round1_futebol.py`  
**Status:** Proof-of-concept Manim animations

**Findings:**
- Already has Manim CE installed (`.venv/lib/python3.14/site-packages/manimpango`)
- Two working scenes: Agent-Lisp orchestration + Futebol estados
- Render commands: `manim -pql file.py SceneName`
- Manim CE is proven to work in this environment

**Reusability:** High — confirms Manim CE works locally, patterns can be extracted

---

## 4. Gap Analysis

### What exists in OSS:
| Feature | Project | Maturity |
|---------|---------|----------|
| LLM → Manim script | manim-generator ⭐113 | Medium |
| Sandboxed render | text2manim ⭐3 | Low |
| Self-repair loop | text2manim ⭐3 | Low |
| Classroom API wrapper | teach-online ⭐9 | Low |
| Drive + Classroom | Classroom-Downloader ⭐5 | Low |
| Local Manim CE | agent-lisp-animation (local) | Proven |

### What does NOT exist in OSS:
| Feature | Our Project | Rationale |
|---------|-------------|-----------|
| LLM → Manim → Classroom (end-to-end) | ✅ | No project connects all three |
| ERP event → video trigger | ✅ | Unique clinical workflow |
| Hexagonal architecture | ✅ | No Manim project uses ports/adapters |
| Template system with versioning | ✅ | No template inheritance found |
| Quiz generation from video | ✅ | Not found in any project |
| Cache by prompt hash | ✅ | Not found |
| Drive folder by patient CPF | ✅ | Clinical-specific |
| Google Meet integration (assisted) | ✅ | Not found as automated workflow |

---

## 5. Competitive Positioning

### Our differentiation:
1. **End-to-end workflow:** Not just generation, but delivery (Classroom + Drive)
2. **ERP integration:** Clinical appointment context (unique)
3. **Architecture quality:** Hexagonal, test-first, requirements-driven
4. **Portuguese-first:** pt-BR educational content ( underserved niche)
5. **Open-source with ADRs:** Transparent decision-making

### Risks from existing projects:
- **manim-generator** (⭐113) could add Classroom integration faster than us
- **text2manim** has sandboxing + self-repair we should adopt
- **EduVids** has web UI we could fork

### Opportunity:
- No project has **clinical ERP + Classroom** workflow
- Most projects are toys/scripts, not production architecture
- Gap in Portuguese educational content

---

## 6. Recommendations

### Adopt from OSS:
1. **text2manim's sandboxed renderer** — security model for untrusted Manim scripts
2. **manim-generator's writer/reviewer loop** — improve script quality
3. **teach-online's Classroom API patterns** — avoid reinventing auth flows

### Differentiate:
1. **Clinical ERP integration** — no one else has this
2. **Hexagonal architecture** — maintainability advantage
3. **Portuguese educational focus** — underserved market

### Speed bumps to watch:
- manim-generator is actively maintained (⭐113, updated 2 days ago) — monitor for Classroom integration features
- Google Classroom API quotas may limit scale
- Manim CE rendering speed is the bottleneck (5min timeout)

---

*Research completed: 2026-08-13*  
*Sources: GitHub API (search), local repo inspection*  
*Confidence: High for existence claims, Medium for feature completeness (projects may have undocumented features)*
