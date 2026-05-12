[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | Português | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Orquestração multi-agente para o Claude Code — edição de pesquisa. Curva de aprendizado zero.**

_Não aprenda ferramentas de pesquisa. Apenas use o OMCR._

OMCR é o irmão voltado para pesquisa de [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode). Enquanto o OMC orquestra trabalho de código geral com engines de execução (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`), o OMCR orquestra o *fluxo de pesquisa* com **6 engines específicas do domínio** — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` e a autônoma `/supervisor-drive`. Use isoladamente ou combine: engines do OMCR rodam dentro dos loops genéricos do OMC para retries (`/ralph`), paralelismo (`/team`, `/ultrawork`), exploração multi-estratégia (`/ultraqa`) ou drives com orçamento (`/autopilot`). Veja [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md) para a matriz completa task → tool e [`wiki/With-OMC.md`](wiki/With-OMC.md) para receitas práticas.

Equipe de pesquisa com 6 agentes + 6 engines de orquestração + 4 comandos setup/workflow + 14 skills (1 primitive + 13 backing surfaces) + 4 hooks leves. Walkthrough completo das engines: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **Status: v0.1.** Mudanças incompatíveis são prováveis. Feedback e PRs são bem-vindos.

> **Documentação completa:** [`wiki/Home.md`](wiki/Home.md)

## Install

**Recomendado — fluxo Claude Code marketplace** (um comando slash por linha, digite um de cada vez):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Alternativa — checkout manual** (sem gerenciador de plugins):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Depois abra o Claude Code e rode `/plugin` para carregar. Após o load (qualquer caminho):
- 6 agentes aparecem no picker de `@`-mention
- 10 comandos slash aparecem no picker: `/omcr-setup`, `/start-research`, `/todofig`, `/sync` (setup/workflow) + `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` (engines de orquestração)
- 14 skills ficam invocáveis (7 setup/workflow + 1 primitive `orchestrate` + 6 engine skills)
- 4 hooks são registrados no início da sessão (guarda PII, auto-load de MEMORY, aviso de citação, setup nudge)

**Cherry-pick por arquivo** (sem gerenciador de plugins — copia agentes para um projeto específico):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Isso pula os comandos, as skills e os hooks. Para paridade completa, use a instalação do plugin.

## Quick start

Após instalar, abra um projeto de pesquisa e rode na ordem:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** é estilo instalação — nenhuma pergunta sobre sua pesquisa. Apenas planta infraestrutura: blocos vazios `## Project context` / `## Research stack` / `## Language preference` no `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` para todos os 6 agentes (template canônico), `paper/references.bib` + `./references.csv` vazios para o literature-curator, e uma allowlist de permissões curada em `.claude/settings.json` (git read-only, busca de arquivos, build LaTeX, API de citação, figure crop — opt-in para análise Python; git write e deleção de arquivos permanecem manuais).

**`/start-research`** é a entrevista. Ela guia você preenchendo esses placeholders:
- **Project context** (working title, campo, venue alvo, hipótese central, tópico de pesquisa, datasets, fio narrativo)
- **Research stack** (caminhos de deck/outline, contagem de figuras, caminhos BibTeX + summary-table, email CrossRef opcional)
- **Preset overlay** (opcional — `examples/neuro-fmri/` etc. — apenas substitui arquivos `MEMORY.md` de agentes ainda byte-identical com o template canônico)
- **Manuscript scaffold** (delega para a skill `manuscript-scaffold`: LaTeX skeleton + lookup de template de journal + clone Overleaf opcional)

Se você rodar `/start-research` antes de `/omcr-setup`, ele oferece rodar `/omcr-setup` primeiro. Campos científicos pulados são salvos como `[TBD: <nota curta>]` — nunca inventados — para que `@supervisor` saiba que precisa fazer follow-up.

Se você pular ambos, o hook `setup-nudge` no SessionStart imprime um lembrete de uma linha a cada sessão até você inicializar. Suprima com `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

Depois dos dois, comece uma conversa de verdade:

```
@supervisor where are we?
```

Walkthrough completo: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Guardião da visão científica em nível de PI + orquestrador do projeto. Mantém a hipótese central; delega para subagentes. |
| `@analysis-implementer` | Implementa pipelines, análises estatísticas, modelos de ML/simulação. Por padrão neutro de campo. |
| `@paper-writer` | Redige seções do manuscrito com qualidade de prosa de venue de alto impacto. |
| `@figure-descriptor` | Projeta figuras como briefs prontos para implementação — não gera imagens. |
| `@reviewer` | Revisão adversarial pré-submissão no nível do venue alvo. |
| `@literature-curator` | Mantém o BibTeX do projeto e a tabela-resumo da literatura em sincronia. Resolve placeholders `[CITE: ...]`, verifica citações via skill `verify-citation`, nunca fabrica. |

### 4 slash commands (parametrizados via o CLAUDE.md do seu projeto)

| Command | What it does |
|---|---|
| `/omcr-setup` | Estilo instalação: cria blocos marcadores vazios no `CLAUDE.md`, diretórios `.claude/agent-memory/`, `references.bib`/`references.csv` vazios, e uma allowlist de permissões curada em `.claude/settings.json`. **Não faz perguntas sobre sua pesquisa.** Rode uma vez por projeto. |
| `/start-research [minimal\|neuro-fmri]` | Estilo entrevista: preenche os placeholders no `CLAUDE.md` (working title, hipótese, venue alvo, datasets, fio narrativo), opcionalmente aplica um preset à memória dos agentes, faz scaffold do diretório LaTeX do manuscrito (via skill `manuscript-scaffold`, com template do journal + clone Overleaf opcional). Oferece rodar `/omcr-setup` antes se ainda não tiver sido feito. |
| `/todofig [Fig N]` | Compara um deck de figuras capturado contra um outline → TODO priorizado P0/P1/P2. |
| `/sync` | Reconcilia o estado atual (deck) com o objetivo (outline), atualiza a memória dos agentes, opcionalmente embute figuras croppadas em um documento alvo. Snapshot de estado, não um TODO. |

### 14 skills

Os 4 comandos slash setup/workflow são thin dispatchers — cada um encaminha `$ARGUMENTS` para uma skill correspondente. `cropfig`, `verify-citation`, `manuscript-scaffold` também podem ser invocados de forma independente. **Além disso** 1 primitive (`orchestrate` — interno, compõe via 4 fases) + 6 engine skills que suportam os 6 comandos de orquestração; walkthrough completo em [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). A tabela abaixo cobre as 7 skills setup/workflow.

| Skill | What it does |
|---|---|
| `omcr-setup` | Suporta `/omcr-setup`. Estilo instalação: scaffold de blocos marcadores no `CLAUDE.md`, diretórios agent-memory, arquivos de bibliografia, allowlist de permissões curada. |
| `start-research` | Suporta `/start-research`. Init estilo entrevista do primeiro projeto: preenche os placeholders já scaffoldados no `CLAUDE.md`, opcionalmente aplica uma preset overlay, delega o manuscript scaffold para `manuscript-scaffold`. |
| `sync` | Suporta `/sync`. Reconcilia o estado atual (deck de figuras capturado) com o outline; atualiza memória dos agentes com drifts factuais; apenas snapshot de estado (sem TODO). |
| `todofig` | Suporta `/todofig`. Compara um deck de figuras capturado com o outline; produz um TODO priorizado P0/P1/P2 dos gaps. |
| `cropfig` | Pipeline de três passos de um deck `.key`/`.pptx` para artefatos manuscrito + outline: PDFs vetoriais por slide (croppados, manuscript-grade) + PNGs nível outline. Invocada diretamente ou por outros comandos; sem slash. |
| `verify-citation` | Checagem de existência + metadados via CrossRef/OpenAlex. Faz gate de cada entrada que `@literature-curator` adiciona, escreve o veredito de verificação na tabela-resumo do projeto. |
| `manuscript-scaffold` | Copia o LaTeX skeleton incluído para o diretório de manuscrito do usuário, opcionalmente aplica um `\documentclass` específico do journal a partir do registry incluído, opcionalmente clona um projeto Overleaf (token nunca persistido em arquivos tracked), commit na branch padrão, pergunta antes de push. Chamado por `/start-research` fase 6; também invocável de forma independente. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Bloqueia writes contendo PII (padrão: emails / SSNs / IDs de sujeito; configurável). |
| `memory-load` | `SessionStart` | Auto-injeta `.claude/agent-memory/*/MEMORY.md` no contexto da sessão. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Aviso heurístico não bloqueante quando o markdown do manuscrito tem parágrafos sem citação. |
| `setup-nudge` | `SessionStart` | Cutucada de uma linha não bloqueante para rodar `/omcr-setup` e depois `/start-research` se o CLAUDE.md não tiver os blocos `## Project context` ou `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — hub de navegação
- **[Getting Started](wiki/Getting-Started.md)** — instalar + primeira sessão
- **[Configuration](wiki/Configuration.md)** — bloco Research stack, variáveis de ambiente, padrões PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — usando o OMCR sozinho, walkthrough completo
- **[With OMC](wiki/With-OMC.md)** — full stack: instalação OMCR + OMC companion
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — referências
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 ferramentas OMC MCP mapeadas para estágios de pesquisa
- **[Specializing](wiki/Specializing.md)** — autorando um preset específico do campo

## Specializing for your field

Agentes e comandos do core são neutros de campo. Para sabor específico do domínio (ex.: metodologia de neurociência, convenções wet-lab, idioms de avaliação ML), faça overlay de um preset de `examples/<field>/`. Atualmente disponíveis:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — especialização neuro-fMRI genérica. Fornece um corpo `analysis-implementer` com sabor neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + esqueletos MEMORY.md redacted para todos os 6 agentes.

Overlay rápido:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Para autorar seu próprio preset: veja [`wiki/Specializing.md`](wiki/Specializing.md). PRs adicionando novos presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) são bem-vindos.

## OMC companion (recommended)

OMCR trata [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) como um *companion*, não uma dependência. Com o OMC instalado ao lado, os componentes a seguir se encaixam naturalmente em fluxos de pesquisa. Escolha os relevantes para seu projeto — você não precisa usar todos.

| Component | Why for research |
|---|---|
| `@scientist` agent | Aplicador de rigor estatístico (ICs / p-valores / tamanhos de efeito / marcadores `[LIMITATION]`). Companion de `@analysis-implementer`. |
| `@document-specialist` agent | Pesquisa de literatura mais pesada apoiada pelo Context Hub do OMC (fetches cacheados, notas estruturadas). Use junto a `@literature-curator` quando precisar de um deep dive em escala de survey; o curator do OMCR cuida sozinho da resolução de citação por claim e da gestão BibTeX/summary-table. |
| `@verifier` agent | Verificação de completude baseada em evidência — rejeita afirmações "should work" sem output de teste fresco. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Ranking de hipóteses competidoras baseado em evidência + disconfirmation. Mapeia para validação de methods/results. |
| `@writer` agent | Escritor de documentação técnica para protocolos de lab, apêndices de methods, guias de reprodutibilidade. |
| `@test-engineer` agent | Disciplina TDD para cobertura de edge cases em scripts de análise. |
| `@git-master` agent | Disciplina atomic-commit — passos de análise revertíveis independentemente. |
| `/oh-my-claudecode:autoresearch` skill | Loop de iteração bounded evaluator-driven com JSON + decision log por iteração. |
| `/oh-my-claudecode:deep-interview` skill | Clarificação socrática de objetivos de pesquisa vagos em hipóteses testáveis. |
| Skills de orquestração OMC (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Orquestradores multi-iteração / paralelo / consenso para runs de análise, varreduras de literatura, revisões must-finish. Veja [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) para 5 receitas práticas. |
| Ferramentas MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki de literatura / registro de hipóteses / registry de runs de experimento / REPL Python stateful. |

Instale o OMC ao lado via Claude Code marketplace, ou `npm i -g oh-my-claude-sisyphus`. Mapeamento completo: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Nomes de arquivo em **kebab-case** para agentes, skills, comandos
- **YAML frontmatter** obrigatório em todo agente / skill / comando (`name`, `description`, opcionalmente `model` / `color` / `memory`)
- **Sem PII** em `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, ou docs de nível superior — instituições, orientadores, IDs reais de sujeito, emails, nomes de journals alvo, caminhos absolutos. Conteúdo específico do domínio vive apenas sob `examples/<field>/`.
- Diretiva de idioma **English-first** em todos os agentes (padrão de override no CLAUDE.md)

Contract completo: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — veja [LICENSE](LICENSE).
