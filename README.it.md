[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | Italiano

# oh-my-claudecode-research

**Orchestrazione multi-agente per Claude Code — l'edizione research. Curva di apprendimento zero.**

_Non imparare strumenti di ricerca. Usa semplicemente OMCR._

OMCR è il fratello orientato alla ricerca di [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode). Mentre OMC orchestra il lavoro di codice generico con motori di esecuzione (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`), OMCR orchestra il *workflow di ricerca* con **6 motori specifici del dominio** — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` e l'autonomo `/supervisor-drive`. Usali da soli o componili: i motori di OMCR girano dentro i loop generici di OMC per retry (`/ralph`), parallelismo (`/team`, `/ultrawork`), esplorazione multi-strategia (`/ultraqa`) o drive con budget tracciato (`/autopilot`). Vedi [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md) per la matrice task → tool completa e [`wiki/With-OMC.md`](wiki/With-OMC.md) per ricette pratiche.

Un team di ricerca da 6 agenti + 6 motori di orchestrazione + 4 comandi setup/workflow + 14 skill (1 primitive + 13 backing surface) + 4 hook leggeri. Walkthrough completo dei motori: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **Stato: v0.1.** Sono probabili breaking change. Feedback e PR sono benvenuti.

> **Documentazione completa:** [`wiki/Home.md`](wiki/Home.md)

## Install

**Consigliato — flusso Claude Code marketplace** (uno slash command per riga, da inserire uno alla volta):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Alternativa — checkout manuale** (senza plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Poi apri Claude Code ed esegui `/plugin` per caricarlo. Dopo il caricamento (in entrambi i casi):
- 6 agenti appaiono nel picker `@`-mention
- 10 slash command appaiono nel picker: `/omcr-setup`, `/start-research`, `/todofig`, `/sync` (setup/workflow) + `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` (motori di orchestrazione)
- 14 skill diventano invocabili (7 setup/workflow + 1 primitive `orchestrate` + 6 engine skill)
- 4 hook si registrano all'avvio di sessione (guardia PII, auto-load di MEMORY, avviso di citazione, setup nudge)

**Cherry-pick per file** (senza plugin manager — copia gli agenti in un progetto specifico):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Questa via salta comandi, skill e hook. Per la parità completa di funzionalità, usa l'installazione del plugin.

## Quick start

Dopo l'installazione, apri un progetto di ricerca ed esegui nell'ordine:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** è stile installazione — nessuna domanda sulla tua ricerca. Posa solo l'infrastruttura: blocchi vuoti `## Project context` / `## Research stack` / `## Language preference` in `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` per tutti i 6 agenti (template canonico), `paper/references.bib` + `./references.csv` vuoti per il literature-curator, e una allowlist di permessi curata in `.claude/settings.json` (git read-only, ricerca file, build LaTeX, API di citazione, figure crop — opt-in per l'analisi Python; git write e cancellazione file restano manuali).

**`/start-research`** è l'intervista. Ti guida nel riempire quei placeholder:
- **Project context** (working title, campo, venue target, ipotesi centrale, tema di ricerca, dataset, filo narrativo)
- **Research stack** (percorsi deck/outline, numero di figure, percorsi BibTeX + summary-table, email CrossRef opzionale)
- **Preset overlay** (opzionale — `examples/neuro-fmri/` ecc. — sostituisce solo i file `MEMORY.md` degli agenti ancora byte-identici al template canonico)
- **Manuscript scaffold** (delega allo skill `manuscript-scaffold`: LaTeX skeleton + lookup di template di rivista + clone Overleaf opzionale)

Se esegui `/start-research` prima di `/omcr-setup`, offre di eseguire `/omcr-setup` per primo. I campi scientifici saltati sono salvati come `[TBD: <nota breve>]` — mai inventati — così `@supervisor` sa di dover fare follow-up.

Se salti entrambi, l'hook `setup-nudge` su SessionStart stampa un promemoria di una riga ogni sessione finché non inizializzi. Sopprimi con `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

Dopo entrambi, inizia una vera conversazione:

```
@supervisor where are we?
```

Walkthrough completo: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Custode della visione scientifica a livello PI + orchestratore del progetto. Possiede l'ipotesi centrale; delega ai subagent. |
| `@analysis-implementer` | Implementa pipeline, analisi statistiche, modelli ML/simulazione. Per default neutrale rispetto al campo. |
| `@paper-writer` | Redige sezioni del manuscript con qualità di prosa da rivista ad alto impatto. |
| `@figure-descriptor` | Progetta figure come brief pronti per l'implementazione — non genera immagini. |
| `@reviewer` | Review adversariale pre-submission al livello del venue target. |
| `@literature-curator` | Mantiene in lockstep il BibTeX e la summary table della letteratura del progetto. Risolve i placeholder `[CITE: ...]`, verifica le citazioni tramite lo skill `verify-citation`, non fabbrica mai. |

### 4 slash commands (parametrizzati tramite il CLAUDE.md del tuo progetto)

| Command | What it does |
|---|---|
| `/omcr-setup` | Stile installazione: posa blocchi marker vuoti in `CLAUDE.md`, le directory `.claude/agent-memory/`, `references.bib`/`references.csv` vuoti, e una allowlist di permessi curata in `.claude/settings.json`. **Non fa domande sulla tua ricerca.** Eseguire una volta per progetto. |
| `/start-research [minimal\|neuro-fmri]` | Stile intervista: riempie i placeholder di `CLAUDE.md` (working title, ipotesi, venue target, dataset, filo narrativo), applica opzionalmente un preset alla memoria degli agenti, scaffold della directory LaTeX del manuscript (via lo skill `manuscript-scaffold`, con template di rivista + clone Overleaf opzionale). Offre di eseguire `/omcr-setup` prima se non è stato fatto. |
| `/todofig [Fig N]` | Confronta un deck di figure catturato con un outline → TODO prioritizzato P0/P1/P2. |
| `/sync` | Riconcilia lo stato corrente (deck) con l'obiettivo (outline), aggiorna le memorie degli agenti, opzionalmente incorpora figure croppate in un documento target. Snapshot di stato, non un TODO. |

### 14 skills

I 4 slash command setup/workflow sono thin dispatcher — ognuno inoltra `$ARGUMENTS` a uno skill corrispondente. `cropfig`, `verify-citation`, `manuscript-scaffold` sono anche invocabili in modo indipendente. **Inoltre** 1 primitive (`orchestrate` — interno, si compone tramite 4 fasi) + 6 engine skill che supportano i 6 comandi di orchestrazione; walkthrough completo in [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). La tabella sotto copre i 7 skill setup/workflow.

| Skill | What it does |
|---|---|
| `omcr-setup` | Supporta `/omcr-setup`. Stile installazione: scaffold di blocchi marker `CLAUDE.md`, directory agent-memory, file di bibliografia, allowlist di permessi curata. |
| `start-research` | Supporta `/start-research`. Init stile intervista del primo progetto: riempie i placeholder già scaffoldati di `CLAUDE.md`, applica opzionalmente un preset overlay, delega il manuscript scaffold a `manuscript-scaffold`. |
| `sync` | Supporta `/sync`. Riconcilia lo stato corrente (deck di figure catturato) con l'outline; aggiorna le memorie degli agenti con drift fattuali; solo snapshot di stato (nessun TODO). |
| `todofig` | Supporta `/todofig`. Confronta un deck di figure catturato con l'outline; produce un TODO prioritizzato P0/P1/P2 dei gap. |
| `cropfig` | Pipeline a tre step da un deck `.key`/`.pptx` agli artifact manuscript + outline: PDF vettoriali per slide (croppati, manuscript-grade) + PNG outline-grade. Invocato direttamente o da altri comandi; nessuno slash. |
| `verify-citation` | Controllo di esistenza + metadati via CrossRef/OpenAlex. Fa da gate per ogni voce aggiunta da `@literature-curator`, scrive il verdetto di verifica nella summary table del progetto. |
| `manuscript-scaffold` | Copia lo skeleton LaTeX incluso nella directory manuscript dell'utente, applica opzionalmente un `\documentclass` specifico della rivista dal registry incluso, opzionalmente clona un progetto Overleaf (il token non viene mai persistito in file tracked), commit sul branch di default, chiede prima di pushare. Chiamato da `/start-research` fase 6; anche invocabile in modo indipendente. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Blocca le write contenenti PII (default: email / SSN / subject ID; configurabile). |
| `memory-load` | `SessionStart` | Auto-inietta `.claude/agent-memory/*/MEMORY.md` nel contesto di sessione. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Avviso euristico non bloccante quando il markdown del manuscript ha paragrafi non citati. |
| `setup-nudge` | `SessionStart` | Spintarella non bloccante di una riga per eseguire `/omcr-setup` e poi `/start-research` se CLAUDE.md non ha i blocchi `## Project context` o `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — hub di navigazione
- **[Getting Started](wiki/Getting-Started.md)** — installazione + prima sessione
- **[Configuration](wiki/Configuration.md)** — blocco Research stack, variabili env, pattern PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — usare OMCR da solo, walkthrough completo
- **[With OMC](wiki/With-OMC.md)** — full stack: installazione OMCR + companion OMC
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — riferimenti
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 strumenti OMC MCP mappati alle fasi di ricerca
- **[Specializing](wiki/Specializing.md)** — scrivere un preset specifico di campo

## Specializing for your field

Gli agenti e i comandi del core sono neutrali rispetto al campo. Per sapore specifico del dominio (es. metodologia di neuroscienza, convenzioni wet-lab, idioms di valutazione ML), sovrapponi un preset da `examples/<field>/`. Attualmente disponibili:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — specializzazione neuro-fMRI generica. Fornisce un corpo `analysis-implementer` con sapore neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + scheletri MEMORY.md redacted per tutti i 6 agenti.

Overlay rapido:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Per scrivere il tuo preset: vedi [`wiki/Specializing.md`](wiki/Specializing.md). PR che aggiungono nuovi preset (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) sono benvenute.

## OMC companion (recommended)

OMCR tratta [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) come un *companion*, non come dipendenza. Con OMC installato a fianco, i seguenti componenti si incastrano naturalmente nei workflow di ricerca. Scegli quelli rilevanti per il tuo progetto — non devi usarli tutti.

| Component | Why for research |
|---|---|
| `@scientist` agent | Imponente di rigore statistico (CI / p-value / dimensioni dell'effetto / marker `[LIMITATION]`). Companion di `@analysis-implementer`. |
| `@document-specialist` agent | Ricerca di letteratura più pesante supportata dal Context Hub di OMC (fetch cachati, note strutturate). Da usare insieme a `@literature-curator` quando serve un deep dive in scala di survey; il curator di OMCR gestisce da solo la risoluzione di citazione per claim e la gestione di BibTeX/summary-table. |
| `@verifier` agent | Controlli di completamento basati su evidenze — rifiuta le affermazioni "should work" senza output di test fresco. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Ranking di ipotesi concorrenti guidato da evidenze + disconfirmation. Si mappa alla validazione methods/results. |
| `@writer` agent | Scrittore di documentazione tecnica per protocolli di lab, appendici methods, guide di riproducibilità. |
| `@test-engineer` agent | Disciplina TDD per copertura di edge case negli script di analisi. |
| `@git-master` agent | Disciplina atomic-commit — step di analisi indipendentemente revertibili. |
| `/oh-my-claudecode:autoresearch` skill | Loop di iterazione bounded evaluator-driven con JSON + decision log per iterazione. |
| `/oh-my-claudecode:deep-interview` skill | Chiarificazione socratica di obiettivi di ricerca vaghi in ipotesi testabili. |
| Skill di orchestrazione OMC (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Orchestratori multi-iterazione / paralleli / consenso per run di analisi, scan di letteratura, revisioni must-finish. Vedi [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) per 5 ricette pratiche. |
| Strumenti MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki di letteratura / register di ipotesi / registry di run di esperimenti / REPL Python con stato. |

Installa OMC accanto via Claude Code marketplace, oppure `npm i -g oh-my-claude-sisyphus`. Mappatura completa: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Nomi file in **kebab-case** per agenti, skill, comandi
- **YAML frontmatter** obbligatorio su ogni agente / skill / comando (`name`, `description`, opzionali `model` / `color` / `memory`)
- **Niente PII** in `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, o nei doc top-level — istituzioni, advisor, ID di soggetti reali, email, nomi di riviste target, percorsi assoluti. Il contenuto specifico del dominio vive solo sotto `examples/<field>/`.
- Direttiva di lingua **English-first** su tutti gli agenti (pattern di override in CLAUDE.md)

Contract completo: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — vedi [LICENSE](LICENSE).
