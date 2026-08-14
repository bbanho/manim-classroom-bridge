# Manim × Classroom Bridge
## Requirements Dependency Tree + Latent Space
### v0.1 | 2026-08-13

> **Input:** `docs/FOUNDATION.md` use cases UC-01 through UC-06
> **Output:** Atomic requirements with dependency graph + latent embedding
> **Method:** Decompose each UC into testable, implementable units; extract cross-cutting concerns

---

## 1. Nomenclatura

| Prefix | Domínio | Exemplo |
|--------|---------|---------|
| `REQ-MJ` | Manim Job (render pipeline) | REQ-MJ-01 |
| `REQ-LLM` | Geração de script via LLM | REQ-LLM-01 |
| `REQ-GAPI` | Google API integration | REQ-GAPI-01 |
| `REQ-CACHE` | Cache e idempotency | REQ-CACHE-01 |
| `REQ-AUTH` | Autenticação e autorização | REQ-AUTH-01 |
| `REQ-UI` | Interface do usuário | REQ-UI-01 |
| `REQ-ERP` | Integração Amplainformática | REQ-ERP-01 |
| `REQ-OBS` | Observabilidade | REQ-OBS-01 |
| `REQ-QUEUE` | Fila assíncrona | REQ-QUEUE-01 |

---

## 2. Árvore de Dependências (nível 0 → 3)

```
NÍVEL 0 — Fundação (sem dependências externas)
│
├── REQ-AUTH-01  Service account Google (credentials + scopes)
├── REQ-MJ-01    Container Manim headless (Docker image)
├── REQ-LLM-01   Prompt engineering base (template pedagógico)
├── REQ-CACHE-01 Hash-based cache key (SHA-256 do prompt)
│
NÍVEL 1 — Depende apenas do Nível 0
│
├── REQ-LLM-02  Gerar script Python válido (usa REQ-LLM-01)
├── REQ-MJ-02   Compilar e validar script (usa REQ-MJ-01)
├── REQ-CACHE-02 Armazenar/recuperar artefato (usa REQ-CACHE-01)
├── REQ-GAPI-01 Google Drive API upload (usa REQ-AUTH-01)
│
NÍVEL 2 — Depende do Nível 1
│
├── REQ-MJ-03   Render MP4 com timeout (usa REQ-MJ-02)
├── REQ-LLM-03  Validação semântica do script (usa REQ-LLM-02)
├── REQ-GAPI-02 Classroom API publish (usa REQ-GAPI-01)
├── REQ-CACHE-03 Invalidation policy (usa REQ-CACHE-02)
│
NÍVEL 3 — Depende do Nível 2
│
├── REQ-UI-01   Dashboard professor (usa REQ-GAPI-02)
├── REQ-LLM-04  Quiz generator (usa REQ-LLM-03)
├── REQ-ERP-01  Event consumer (ERP → vídeo) (usa REQ-GAPI-02)
│
NÍVEL 4 — Depende do Nível 3
│
├── REQ-QUEUE-01 Fila assíncrona (usa REQ-MJ-03, REQ-UI-01)
├── REQ-OBS-01   Observability stack (usa tudo acima)
```

---

## 3. Decomposição Atômica por Caso de Uso

### UC-01 — Gerar vídeo a partir de prompt

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-LLM-01 | Template de prompt pedagógico funciona com modelo alvo | Temperature fixa (0.2), retorna Python parseável em 100% dos testes | — |
| REQ-LLM-02 | Script gerado compila sem erros de sintaxe | `python -m py_compile` passa | REQ-LLM-01 |
| REQ-LLM-03 | Script gerado instancia pelo menos 1 Scene do Manim | AST analysis: classe filha de `Scene` encontrada | REQ-LLM-02 |
| REQ-MJ-01 | Container headless renderiza cena básica (círculo + texto) | Output: MP4 legível, duração 3±0.5s, resolução 480p | — |
| REQ-MJ-02 | Script passa por validador estático antes do render | Sem imports proibidos, sem `os.system`, sem file I/O | REQ-MJ-01 |
| REQ-MJ-03 | Render completo em ≤ 2min para cena de 3min em -ql | Timeout hard 5min; falha gera log + retry 3x | REQ-MJ-02, REQ-LLM-03 |
| REQ-CACHE-01 | Chave de cache é determinística | Mesmo prompt → mesmo hash SHA-256 | — |
| REQ-CACHE-02 | Hit de cache retorna artefato sem re-renderizar | Latência < 1s; log hit/miss | REQ-CACHE-01, REQ-MJ-03 |
| REQ-OBS-01 | Logs estruturados por render job | JSON com campos: `job_id`, `prompt_hash`, `duration_ms`, `status` | REQ-MJ-03 |

### UC-02 — Publicar vídeo no Google Classroom

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-AUTH-01 | Service account autentica com scopes mínimos | Token obtido; scopes: `classroom.courses`, `drive.file` | — |
| REQ-AUTH-02 | Refresh automático de token sem interação | Token expira em 3600s; refresh < 5s | REQ-AUTH-01 |
| REQ-GAPI-01 | Upload resumível para Drive (até 100MB) | Arquivo chega; permissões `reader` para domínio | REQ-AUTH-01 |
| REQ-GAPI-02 | Cria CourseWorkMaterial no Classroom | Aparece no curso do professor; link Drive funcional | REQ-GAPI-01 |
| REQ-GAPI-03 | Permissões de Drive propagam para alunos do curso | Aluno do curso vê vídeo sem link direto | REQ-GAPI-02 |
| REQ-CACHE-03 | Re-publish do mesmo vídeo não duplica | GET antes de POST; compara `drive_file_id` | REQ-CACHE-02, REQ-GAPI-02 |

### UC-03 — Assistir vídeo durante Google Meet

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-UI-02 | Botão "Abrir no Meet" abre vídeo em aba | URL `meet.google.com/lookup/...` com vídeo como aba compartilhada | REQ-GAPI-02 |
| REQ-UI-03 | Link de apresentação direta funciona sem auth extra | Professor compartilha tela; alunos veem sem login extra | REQ-UI-02 |

**Nota:** Não há dependência de API do Meet além de deep-link. O "Workspace Add-on" fica como `REQ-UI-04` (futuro).

### UC-04 — Quiz automático pós-vídeo

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-LLM-04 | Gera 5–10 questões de múltipla escolha | 4 alternativas, 1 correta, explicação por resposta | REQ-LLM-03 |
| REQ-LLM-05 | Questões alinhadas ao conteúdo do vídeo | Prompt inclui transcrição/summary do vídeo | REQ-LLM-04, REQ-CACHE-02 |
| REQ-GAPI-04 | Cria CourseWork (quiz) no Classroom | Tipo `QUIZ`; múltipla escolha; data limite configurável | REQ-GAPI-02 |
| REQ-GAPI-05 | Lê respostas dos alunos via API | Score por aluno por questão | REQ-GAPI-04 |

### UC-05 — Reutilizar template de vídeo

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-LLM-06 | Diff entre template e customização é detectável | Git-like diff: linhas modificadas, inseridas, removidas | REQ-LLM-02 |
| REQ-CACHE-04 | Template versionado; version filha herda cache parcial | Mudança em template → re-render de filhos afetados | REQ-CACHE-03, REQ-LLM-06 |
| REQ-UI-04 | Editor de template (diff view + edit) | Professor vê diff, aceita/rejeita mudanças | REQ-CACHE-04 |

### UC-06 — Sincronizar com ERP/agenda (PROPRIETÁRIO)

**⚠️ Este caso de uso NÃO está no repositório open-source.**  
Implementação: `manim-classroom-bridge-erp` (repositório privado).

| ID | Requisito | Critério de Aceite | Depende de |
|----|-----------|---------------------|------------|
| REQ-ERP-01 | Consome evento `consulta_agendada` da fila | Message ID dedup; `idempotencyKey` respeitado | REQ-GAPI-02 |
| REQ-ERP-02 | Mapeia tipo de consulta → template de vídeo | Regra: retorno → template_revisao, inicial → template_introducao | REQ-ERP-01, REQ-LLM-06 |
| REQ-ERP-03 | Upload por CPF cria estrutura de pastas | `drive/patients/{cpf}/{consulta_id}/` | REQ-ERP-01, REQ-GAPI-01 |
| REQ-UI-05 | Notificação para professor revisar antes do envio | E-mail ou banner no dashboard | REQ-ERP-01, REQ-UI-01 |

**Nota:** Estes requisitos estão documentados aqui para rastreabilidade, mas a implementação está em repositório fechado.

---

## 4. Espaço Latente (agrupamento por afinidade)

### Cluster A — Render Core (REQ-MJ-*)
**Conceito:** Container headless que transforma Python em vídeo.
**Requisitos:** REQ-MJ-01, REQ-MJ-02, REQ-MJ-03
**Dependência externa:** Nenhuma (pode ser desenvolvido isoladamente)
**Risco técnico:** Baixo — Manim CE é maduro, Dockerfile padrão.

### Cluster B — LLM Script Generator (REQ-LLM-*)
**Conceito:** Modelo que converte intenção pedagógica em código Manim válido.
**Requisitos:** REQ-LLM-01 a REQ-LLM-06
**Dependência externa:** Modelo Gemini/OpenAI via Nexus Gateway ou direto
**Risco técnico:** Médio — LLM pode gerar código que compila mas não renderiza cena significativa. Validação semântica (REQ-LLM-03) é o gargalo.

### Cluster C — Google API Integration (REQ-GAPI-*)
**Conceito:** Ponte entre artefatos locais e ecossistema Google do professor.
**Requisitos:** REQ-GAPI-01 a REQ-GAPI-05, REQ-AUTH-01, REQ-AUTH-02
**Dependência externa:** Google Cloud project, service account, domínio verificado
**Risco técnico:** Baixo — APIs maduras, mas quotas e scopes requerem configuração inicial.

### Cluster D — Cache e Idempotency (REQ-CACHE-*)
**Conceito:** Evitar re-trabalho e garantir consistência entre render e upload.
**Requisitos:** REQ-CACHE-01 a REQ-CACHE-04
**Dependência externa:** Drive ou filesystem local (primeira versão)
**Risco técnico:** Baixo — hash + lookup. Invalidation policy (REQ-CACHE-03) é o ponto de atenção.

### Cluster E — UI Professor (REQ-UI-*)
**Conceito:** Interface onde o professor dispara ações e acompanha progresso.
**Requisitos:** REQ-UI-01 a REQ-UI-05
**Dependência externa:** Nenhuma se for API-only; Google Apps Script se quiser embedding nativo
**Risco técnico:** Médio — UX de "gerar vídeo assistido" pode ser tricky. Sugiro começar API-only + CLI.

### Cluster F — ERP Bridge (REQ-ERP-*)
**Conceito:** Eventos do agendamento clínico disparam geração de conteúdo educativo.
**Requisitos:** REQ-ERP-01 a REQ-ERP-03
**Dependência externa:** ERP Amplainformática (fila de eventos existente)
**Risco técnico:** Médio — depende de formato de mensagem do ERP e contrato de idempotência.

### Cluster G — Observabilidade (REQ-OBS-*)
**Conceito:** Logs, métricas, tracing de ponta a ponta.
**Requisitos:** REQ-OBS-01
**Dependência externa:** Nenhuma
**Risco técnico:** Baixo — JSON logs + contador de jobs.

---

## 5. Matriz de Dependências Cruzadas

| Requisito | A | B | C | D | E | F | G |
|-----------|---|---|---|---|---|---|---|
| REQ-AUTH-01 | — | ○ | ● | ○ | ○ | ○ | ○ |
| REQ-MJ-01    | — | ○ | ○ | ○ | ○ | ○ | ○ |
| REQ-LLM-01   | — | ● | ○ | ○ | ○ | ○ | ○ |
| REQ-CACHE-01 | — | ○ | ○ | ● | ○ | ○ | ○ |
| REQ-MJ-03    | — | ● | ○ | ● | ○ | ○ | ● |
| REQ-GAPI-02 | — | ○ | ● | ○ | ○ | ○ | ○ |
| REQ-ERP-01  | — | ○ | ● | ○ | ○ | ● | ○ |

Legenda:
- **●** dependência direta (bloqueante)
- **○** dependência indireta ou compartilha infra
- **—** não aplicável

---

## 6. Ordem de Implementação Sugerida (camadas)

### Sprint 0 — Fundação (sem dependências externas)
**Objetivo:** Provar que o núcleo funciona sem Google nem ERP.

| Ordem | Requisito | Esforço | Risco |
|-------|-----------|---------|-------|
| S0-1 | REQ-MJ-01: Container Manim headless | 2h | Baixo |
| S0-2 | REQ-LLM-01: Prompt template base | 4h | Médio |
| S0-3 | REQ-CACHE-01: Hash + lookup local | 1h | Baixo |
| S0-4 | REQ-MJ-02: Validação estática de script | 2h | Baixo |
| S0-5 | REQ-LLM-02: Gerar script que compila | 4h | Médio |

**Entregável:** `python scripts/generate_video.py --prompt "Pitágoras" --output /tmp/test.mp4`

### Sprint 1 — Google Integration (apenas auth + Drive)
**Objetivo:** Provar que vídeo chega no Classroom.

| Ordem | Requisito | Esforço | Risco |
|-------|-----------|---------|-------|
| S1-1 | REQ-AUTH-01: Service account setup | 2h | Baixo |
| S1-2 | REQ-GAPI-01: Upload Drive resumível | 3h | Baixo |
| S1-3 | REQ-LLM-03: Validação semântica | 3h | Médio |
| S1-4 | REQ-MJ-03: Render com timeout + retry | 2h | Baixo |
| S1-5 | REQ-CACHE-02: Cache por hash | 1h | Baixo |
| S1-6 | REQ-GAPI-02: Publish no Classroom | 3h | Baixo |

**Entregável:** Professor recebe link no Classroom após 3min de processamento.

### Sprint 2 — UX e Automação
**Objetivo:** Interface + ERP hook.

| Ordem | Requisito | Esforço | Risco |
|-------|-----------|---------|-------|
| S2-1 | REQ-UI-01: Dashboard professor (API-only) | 8h | Médio |
| S2-2 | REQ-LLM-04: Quiz generator | 4h | Médio |
| S2-3 | REQ-GAPI-04: Quiz no Classroom | 2h | Baixo |
| S2-4 | REQ-ERP-01: Event consumer | 4h | Médio |

**Entregável:** Professor usa web UI; ERP dispara vídeo automaticamente.

### Sprint 3 — Production-ready
**Objetivo:** Resiliência e escala.

| Ordem | Requisito | Esforço | Risco |
|-------|-----------|---------|-------|
| S3-1 | REQ-QUEUE-01: Fila assíncrona | 6h | Médio |
| S3-2 | REQ-CACHE-03: Invalidation policy | 2h | Baixo |
| S3-3 | REQ-OBS-01: Observabilidade | 3h | Baixo |
| S3-4 | REQ-ERP-03: Pasta por CPF | 2h | Baixo |

---

## 7. Requisitos Transversais (aplicam a todos os clusters)

| ID | Requisito | Aplicação |
|----|-----------|-----------|
| REQ-X-01 | Todo requisito deve ter teste automatizado | Todos |
| REQ-X-02 | Todo erro de infraestrutura gera retry com backoff exponencial | A, C, D, E, F |
| REQ-X-03 | Nenhum segredo hardcoded; usar env vars ou secret manager | Todos |
| REQ-X-04 | Todos os artefatos de saída têm checksum SHA-256 | A, B, C, D |
| REQ-X-05 | Timeout global por job: 5min hard, 2min soft | A, B, C |
| REQ-X-06 | Schema de logs: `job_id`, `actor`, `action`, `status`, `duration_ms`, `error` | Todos |
| REQ-X-07 | Service account respeita princípio de menor privilégio | C |
| REQ-X-08 | Cache hit ratio target: > 60% em produção | D |
| REQ-X-09 | UI responsiva (mobile-first) para professores | E |
| REQ-X-10 | ERP events são at-least-once delivery; receptor é idempotente | F |

---

## 8. Árvore de Decisões (ADR candidates)

Dependendo das escolhas de stack, alguns requisitos viram ADR:

```
ADR-001 (Stack render)
  ├── Se Manim CE puro → REQ-MJ-01 é Dockerfile padrão
  ├── Se manim-slides → REQ-MJ-01 vira container com Vite + HTML output
  └── Se MoviePy pós-processamento → REQ-MJ-03 ganha etapa de composição

ADR-002 (Queue backend)
  ├── Se Redis + BullMQ → REQ-QUEUE-01 usa Node worker
  ├── Se Celery → REQ-QUEUE-01 usa Python worker
  └── Se síncrono (v1) → REQ-QUEUE-01 fica como "futuro", timeout em REQ-MJ-03

ADR-003 (LLM provider)
  ├── Se Nexus Gateway → REQ-LLM-01 usa QuantaNode + RoutingOutboundAdapter
  ├── Se direto Gemini → REQ-LLM-01 usa google-generativeai SDK
  └── Se OpenAI → REQ-LLM-01 usa openai SDK (fallback)
```

---

## 9. Checklist de Prontidão por Sprint

### Sprint 0 ready quando:
- [ ] REQ-MJ-01: Container renderiza cena "Hello World"
- [ ] REQ-LLM-01: Prompt template aprovado
- [ ] REQ-MJ-02: `py_compile` + AST check passam
- [ ] REQ-LLM-02: 3 vídeos gerados com sucesso (Pitágoras, Δ, frações)
- [ ] REQ-CACHE-01: Cache local funciona

### Sprint 1 ready quando:
- [ ] REQ-AUTH-01: Service account criada + scopes aprovados
- [ ] REQ-GAPI-02: Vídeo aparece em curso de teste no Classroom
- [ ] REQ-CACHE-02: Re-render do mesmo prompt não acontece (log mostra HIT)
- [ ] REQ-LLM-03: Scripts inválidos são rejeitados antes do render

### Sprint 2 ready quando:
- [ ] REQ-UI-01: Professor cria vídeo via web UI sem terminal
- [ ] REQ-ERP-01: Evento de teste dispara geração
- [ ] REQ-GAPI-04: Quiz aparece no Classroom após vídeo

### Sprint 3 ready quando:
- [ ] REQ-QUEUE-01: 10 jobs simultâneos sem bloqueio
- [ ] REQ-OBS-01: Dashboard mostra jobs pendentes, falhas, duração média
- [ ] REQ-CACHE-03: Mudança de template invalida filhos corretamente

---

*Documento vivo. Cada requisito deve virar arquivo em `docs/requirements/REQ-XXX.md` com critérios de aceite detalhados.*
