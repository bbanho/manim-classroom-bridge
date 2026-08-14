# Manim × Classroom Bridge
## Engenharia — Documento Fundacional v0.1

> **Status:** Draft | **Created:** 2026-08-13 | **Authors:** bbanho + AI-assisted
> **Próximo passo:** Validar use cases → escrever ADR-001 (stack) → scaffold repo

---

## 1. Propósito

Permitir que um modelo de linguagem gere vídeos educacionais via **Manim CE**, renderize-os automaticamente e publique-os em **Google Classroom** — com rota alternativa de entrega via **Google Meet** (screen-share assistido).

**Não é um LMS.** É uma ponte entre geração procedural de conteúdo audiovisual e plataformas de distribuição educacional já existentes.

---

## 2. Atores

| Ator | Descrição |
|------|-----------|
| **Professor** | Cria assignment/quiz no Classroom, seleciona template de vídeo, dispara geração |
| **Aluno** | Consome vídeo publicado, submete respostas, recebe feedback automático |
| **IA (Manim Agent)** | Recebe prompt pedagógico → escreve script Python Manim → renderiza |
| **Render Worker** | Container headless que executa Manim + ffmpeg + texlive; produz MP4/WebM |
| **Classroom Adapter** | Service account que autentica no Google Classroom API, faz uploads |
| **Drive Cache** | Armazena vídeos renderizados antes do upload (evita re-renderizar) |

---

## 3. Casos de Uso

### UC-01 — Gerar vídeo a partir de prompt
**Ator primário:** Professor (via UI ou API direta)

**Fluxo:**
1. Professor fornece: tópico + dificuldade + duração alvo + estilo visual
2. Sistema envia prompt ao LLM (via Nexus Gateway ou direto)
3. LLM retorna script Python Manim válido
4. Render Worker executa: `manim -ql --format=mp4 script.py Scene`
5. Vídeo é armazenado em Drive Cache (hash do prompt como idempotency key)
6. Se vídeo já existe → skip render, retorna cached

**Critérios de aceite:**
- Render ≤ 2min para vídeos de 3min em `-ql` (480p)
- Script gerado deve passar `python -m py_compile` antes de render
- Falha de render → log estruturado + retry automático (3x) + fallback para template humano

### UC-02 — Publicar vídeo no Google Classroom
**Ator primário:** Professor (confirma) / Sistema (automático)

**Fluxo:**
1. Professor seleciona Course + Topic existente
2. Sistema cria `CourseWorkMaterial` ou `Announcement` com link do Drive
3. Vídeo é tornado visível para alunos do curso (permissões Drive gerenciadas)
4. Retorna URL público (view) para compartilhamento em Meet

**Critérios de aceite:**
- Upload via resumable upload (arquivos até 100MB)
- Permissões: `reader` para domínio do curso, `writer` para professor
- Idempotente: re-publicar mesmo vídeo não cria duplicata

### UC-03 — Assistir vídeo durante Google Meet
**Ator primário:** Professor (ação manual assistida)

**Fluxo:**
1. Sistema fornece link direto + botão "Abrir no Meet"
2. Professor clica → vídeo abre em aba separada (ou nativo Meet Presentar)
3. Meet compartilha a aba; vídeo toca para todos
4. (Futuro) Meet Add-on que injeta player no sidebar — requer Google Workspace Add-on

**Nota:** Injeção direta no stream de vídeo do Meet **não é possível via API pública**. Esta é a melhor alternativa automatizável hoje.

### UC-04 — Quiz automático pós-vídeo
**Ator primário:** Professor (configura) / Aluno (responde)

**Fluxo:**
1. Após publicar vídeo, professor marca "criar quiz"
2. LLM gera 5–10 questões de múltipla escolha alinhadas ao conteúdo
3. Sistema cria `CourseWork` (quiz) no Classroom via API
4. Aluno responde; sistema registra score
5. (Futuro) Analytics de desempenho correlaciona respostas com timestamp do vídeo

**Critérios de aceite:**
- Questões devem ter explicação de feedback por resposta
- Suporte a múltipla escolha (4 alternativas) inicialmente
- Integração com Google Forms API como fallback se Classroom quiz não suportar

### UC-05 — Reutilizar template de vídeo
**Ator primário:** Professor

**Fluxo:**
1. Professor marca vídeo como "template"
2. Templates são versionados: `templates/{topic}/{difficulty}/scene.py`
3. Novo vídeo herda scaffold visual + estilo, professor só edita conteúdo específico
4. Sistema detecta diff entre template e versão customizada para cache

### UC-06 — Sincronizar com ERP/agenda (Amplainformática)
**Ator primário:** Sistema (background job)

**Fluxo:**
1. ERP envia evento `consulta_agendada` com dados do paciente
2. Worker consome, identifica tipo de consulta (retorno, inicial, exame)
3. Dispara geração de vídeo educativo correspondente
4. Vídeo é associado ao paciente no Drive (pasta por CPF)
5. Professor/recepcionista é notificado para revisar antes do envio

**Nota:** Este UC é específico do contexto clínico Amplainformática, mas faz parte do core open-source.

---

## 4. Requisitos Não-Funcionais

| ID | Requisito | Criticidade |
|----|-----------|-------------|
| RNF-01 | Render headless 100% containerizado (sem display server) | Must |
| RNF-02 | Timeout de render: 5min hard, 2min soft | Must |
| RNF-03 | LLM prompt deve ser determinístico para mesmo input (temperature=0.2) | Should |
| RNF-04 | Cache por hash SHA-256 do prompt pedagógico | Should |
| RNF-05 | Service account com princípio de menor privilégio (apenas Classroom + Drive) | Must |
| RNF-06 | Logs estruturados JSON (render, upload, errors) | Must |
| RNF-07 | Queue assíncrona para renders (não bloquear API) | Should |
| RNF-08 | Vídeos devem ser acessíveis (legendas WebVTT geradas automaticamente) | Could |
| RNF-09 | Suporte a pt-BR nativo (estilo de narração, exemplos, fontes) | Must |
| RNF-10 | Custo de render por vídeo < R$ 0,50 (Colab GPU gratuito preferencial) | Should |

---

## 5. Fora do Escopo (v1)

- Edição interativa de vídeo (WYSIWYG timeline)
- Suporte a outros LMS além de Google Classroom
- Streaming ao vivo (WebRTC/RTMP)
- Reconhecimento de voz/vídeo do aluno
- Mobile app nativo

---

## 6. Decisões Pendentes (serão ADRs)

| # | Tema | Opções |
|---|------|--------|
| ADR-001 | Stack de render | Manim CE puro vs manim-slides (HTML5) vs MoviePy pós-processamento |
| ADR-002 | Queue backend | Redis + BullMQ (Node) vs Celery (Python) vs Cloudflare Queues |
| ADR-003 | Auth Google | Service account direto vs OAuth2 flow com refresh token |
| ADR-004 | LLM provider | Nexus Gateway (multi-provider) vs chamada direta Gemini/OpenAI |
| ADR-005 | Deploy render | Colab GPU (gratuito, não-Docker) vs Docker self-hosted vs GCP Cloud Run |
| ADR-006 | Storage | Google Drive (nativo) vs GCS (maior throughput) vs S3-compatible |
| ADR-007 | Frontend | App HTML estático (Vite) vs Google Apps Script Web App vs nada (API-only) |

---

## 7. Dependências Externas

```
manim-ce>=0.19
google-api-python-client>=2.100
google-auth>=2.23
google-auth-httplib2>=0.2
ffmpeg-python>=0.2
pydantic>=2.0
```

---

## 8. Próximos Passos

1. Validar este documento com você → ajustar use cases
2. Escrever ADR-001 (stack) + ADR-002 (auth)
3. Scaffold repo com estrutura hexagonal (inspirado em agendamento-universal)
4. Proof-of-concept: UC-01 end-to-end (prompt → MP4 local)
5. Proof-of-concept: UC-02 (upload Drive → Classroom API)

---

*Documento vivo. Editar via PR. Mudanças estruturais requerem ADR.*
