[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | Italiano

# oh-my-codex-research

**Orchestrazione multi-agente per Codex — l'edizione research. Curva di apprendimento zero.**

_Non imparare strumenti di ricerca. Usa semplicemente OMXR._

OMXR è un workspace di ricerca per Codex: sei agenti — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — con cui lavori fianco a fianco su ipotesi, analisi, scrittura, figure, citazioni, review. Sei motori di orchestrazione automatizzano i loop comuni quando vuoi hands-off. Combinalo con [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) quando ti serve orchestrazione generica sopra (retry, parallelismo, controllo del budget).

Un team di ricerca da 6 agenti + 6 motori di orchestrazione + 4 comandi setup/workflow + 14 skill + 4 hook leggeri.

> **Stato: v0.1.** Sono probabili breaking change. Feedback e PR sono benvenuti.

> **Documentazione completa:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: Installazione**

**Se installi OMXR per la prima volta** — flusso marketplace (consigliato). Sono workflow command di Codex, inseriscili **uno alla volta**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-codex-research
```

Poi:

```
/plugin install oh-my-codex-research
```

**Se preferisci il checkout manuale** (senza plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-codex-research \
  ~/.codex/plugins/oh-my-codex-research
```

**Se OMXR è già installato e vuoi aggiornarlo** — esegui questi due workflow command uno alla volta:

```
/plugin marketplace update omxr
```

Poi:

```
/plugin update oh-my-codex-research
```

Il primo aggiorna solo i metadati del marketplace; il secondo prende davvero i nuovi file del plugin. OMXR segue `main`, quindi ogni commit nuovo è trattato come una versione nuova. Lo stato del tuo progetto (AGENTS.md, memoria degli agenti, settings) non viene toccato — non serve rilanciare lo Step 2.

**Step 2: Setup**

**Va fatto una volta sola per progetto.** Dentro una sessione Codex nel tuo progetto di ricerca, esegui gli workflow command **uno alla volta**:

```
$omxr-setup
```

Poi:

```
$start-research
```

`$omxr-setup` posa l'infrastruttura — blocchi vuoti `## Project context` / `## Research stack` / `## Language preference` in `AGENTS.md`, `.omx/omxr/agent-memory/<agent>/MEMORY.md` per tutti i 6 agenti, `paper/references.bib` + `./references.csv` vuoti per il literature-curator, e una hook/check readiness di permessi curata. **Nessuna domanda sulla tua ricerca.**

`$start-research` è l'intervista. Ti guida nel riempire quei placeholder:
- **Project context** (working title, campo, venue target, ipotesi centrale, tema di ricerca, dataset, filo narrativo)
- **Research stack** (percorsi deck/outline, numero di figure, percorsi BibTeX + summary-table, email CrossRef opzionale)
- **Preset overlay** (opzionale — `examples/neuro-fmri/` ecc. — sostituisce solo i file `MEMORY.md` degli agenti ancora byte-identici al template canonico)
- **Manuscript scaffold** (delega allo skill `manuscript-scaffold`: LaTeX skeleton + lookup di template di rivista + clone Overleaf opzionale)

Se esegui `$start-research` prima di `$omxr-setup`, offre di eseguire `$omxr-setup` per primo. I campi scientifici saltati sono salvati come `[TBD: <nota breve>]` — mai inventati — così `@supervisor` sa di dover fare follow-up. Se salti entrambi, l'hook `setup-nudge` su SessionStart stampa un promemoria di una riga ogni sessione finché non inizializzi (sopprimi con `CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Inizia**

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

### 4 workflow commands (parametrizzati tramite il AGENTS.md del tuo progetto)

| Command | What it does |
|---|---|
| `$omxr-setup` | Stile installazione: posa blocchi marker vuoti in `AGENTS.md`, le directory `.omx/omxr/agent-memory/`, `references.bib`/`references.csv` vuoti, e una hook/check readiness di permessi curata. **Non fa domande sulla tua ricerca.** Eseguire una volta per progetto. |
| `$start-research [minimal\|neuro-fmri]` | Stile intervista: riempie i placeholder di `AGENTS.md` (working title, ipotesi, venue target, dataset, filo narrativo), applica opzionalmente un preset alla memoria degli agenti, scaffold della directory LaTeX del manuscript (via lo skill `manuscript-scaffold`, con template di rivista + clone Overleaf opzionale). Offre di eseguire `$omxr-setup` prima se non è stato fatto. |
| `$todofig [Fig N]` | Confronta un deck di figure catturato con un outline → TODO prioritizzato P0/P1/P2. |
| `$sync` | Riconcilia lo stato corrente (deck) con l'obiettivo (outline), aggiorna le memorie degli agenti, opzionalmente incorpora figure croppate in un documento target. Snapshot di stato, non un TODO. |

### 14 skills

I 4 workflow command setup/workflow sono thin dispatcher — ognuno inoltra `$ARGUMENTS` a uno skill corrispondente. `cropfig`, `verify-citation`, `manuscript-scaffold` sono anche invocabili in modo indipendente. **Inoltre** 1 primitive (`orchestrate` — interno, si compone tramite 4 fasi) + 6 engine skill che supportano i 6 comandi di orchestrazione; walkthrough completo in [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). La tabella sotto copre i 7 skill setup/workflow.

| Skill | What it does |
|---|---|
| `omxr-setup` | Supporta `$omxr-setup`. Stile installazione: scaffold di blocchi marker `AGENTS.md`, directory agent-memory, file di bibliografia, hook/check readiness di permessi curata. |
| `start-research` | Supporta `$start-research`. Init stile intervista del primo progetto: riempie i placeholder già scaffoldati di `AGENTS.md`, applica opzionalmente un preset overlay, delega il manuscript scaffold a `manuscript-scaffold`. |
| `sync` | Supporta `$sync`. Riconcilia lo stato corrente (deck di figure catturato) con l'outline; aggiorna le memorie degli agenti con drift fattuali; solo snapshot di stato (nessun TODO). |
| `todofig` | Supporta `$todofig`. Confronta un deck di figure catturato con l'outline; produce un TODO prioritizzato P0/P1/P2 dei gap. |
| `cropfig` | Pipeline a tre step da un deck `.key`/`.pptx` agli artifact manuscript + outline: PDF vettoriali per slide (croppati, manuscript-grade) + PNG outline-grade. Invocato direttamente o da altri comandi; nessuno slash. |
| `verify-citation` | Controllo di esistenza + metadati via CrossRef/OpenAlex. Fa da gate per ogni voce aggiunta da `@literature-curator`, scrive il verdetto di verifica nella summary table del progetto. |
| `manuscript-scaffold` | Copia lo skeleton LaTeX incluso nella directory manuscript dell'utente, applica opzionalmente un `\documentclass` specifico della rivista dal registry incluso, opzionalmente clona un progetto Overleaf (il token non viene mai persistito in file tracked), commit sul branch di default, chiede prima di pushare. Chiamato da `$start-research` fase 6; anche invocabile in modo indipendente. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Blocca le write contenenti PII (default: email / SSN / subject ID; configurabile). |
| `memory-load` | `SessionStart` | Auto-inietta `.omx/omxr/agent-memory/*/MEMORY.md` nel contesto di sessione. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Avviso euristico non bloccante quando il markdown del manuscript ha paragrafi non citati. |
| `setup-nudge` | `SessionStart` | Spintarella non bloccante di una riga per eseguire `$omxr-setup` e poi `$start-research` se AGENTS.md non ha i blocchi `## Project context` o `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — hub di navigazione
- **[Getting Started](wiki/Getting-Started.md)** — installazione + prima sessione
- **[Configuration](wiki/Configuration.md)** — blocco Research stack, variabili env, pattern PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — usare OMXR da solo, walkthrough completo
- **[With OMX](wiki/With-OMX.md)** — full stack: installazione OMXR + companion OMX
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — riferimenti
- **[OMX Tool Reference](wiki/OMX-Tool-Reference.md)** — 47 strumenti OMX MCP mappati alle fasi di ricerca
- **[Specializing](wiki/Specializing.md)** — scrivere un preset specifico di campo

## Specializing for your field

Gli agenti e i comandi del core sono neutrali rispetto al campo. Per sapore specifico del dominio (es. metodologia di neuroscienza, convenzioni wet-lab, idioms di valutazione ML), sovrapponi un preset da `examples/<field>/`. Attualmente disponibili:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — specializzazione neuro-fMRI generica. Fornisce un corpo `analysis-implementer` con sapore neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + scheletri MEMORY.md redacted per tutti i 6 agenti.

Overlay rapido:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .omx/omxr/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .omx/omxr/agent-memory/$agent/MEMORY.md
done
```

Per scrivere il tuo preset: vedi [`wiki/Specializing.md`](wiki/Specializing.md). PR che aggiungono nuovi preset (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) sono benvenute.

## OMX companion (recommended)

OMXR tratta [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex) come un *companion*, non come dipendenza. Con OMX installato a fianco, i seguenti componenti si incastrano naturalmente nei workflow di ricerca. Scegli quelli rilevanti per il tuo progetto — non devi usarli tutti.

| Component | Why for research |
|---|---|
| `@scientist` agent | Imponente di rigore statistico (CI / p-value / dimensioni dell'effetto / marker `[LIMITATION]`). Companion di `@analysis-implementer`. |
| `@document-specialist` agent | Ricerca di letteratura più pesante supportata dal Context Hub di OMX (fetch cachati, note strutturate). Da usare insieme a `@literature-curator` quando serve un deep dive in scala di survey; il curator di OMXR gestisce da solo la risoluzione di citazione per claim e la gestione di BibTeX/summary-table. |
| `@verifier` agent | Controlli di completamento basati su evidenze — rifiuta le affermazioni "should work" senza output di test fresco. |
| `@tracer` agent + `/oh-my-codex:trace` | Ranking di ipotesi concorrenti guidato da evidenze + disconfirmation. Si mappa alla validazione methods/results. |
| `@writer` agent | Scrittore di documentazione tecnica per protocolli di lab, appendici methods, guide di riproducibilità. |
| `@test-engineer` agent | Disciplina TDD per copertura di edge case negli script di analisi. |
| `@git-master` agent | Disciplina atomic-commit — step di analisi indipendentemente revertibili. |
| `/oh-my-codex:autoresearch` skill | Loop di iterazione bounded evaluator-driven con JSON + decision log per iterazione. |
| `/oh-my-codex:deep-interview` skill | Chiarificazione socratica di obiettivi di ricerca vaghi in ipotesi testabili. |
| Skill di orchestrazione OMX (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Orchestratori multi-iterazione / paralleli / consenso per run di analisi, scan di letteratura, revisioni must-finish. Vedi [`wiki/With-OMX.md#recipes--pairing-omxr-with-omc`](wiki/With-OMX.md#recipes--pairing-omxr-with-omc) per 5 ricette pratiche. |
| Strumenti MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki di letteratura / register di ipotesi / registry di run di esperimenti / REPL Python con stato. |

Installa OMX accanto via Codex marketplace, oppure `npm i -g oh-my-codex`. Mappatura completa: [`wiki/With-OMX.md`](wiki/With-OMX.md) + [`wiki/OMX-Tool-Reference.md`](wiki/OMX-Tool-Reference.md)

## Conventions (contributors)

- Nomi file in **kebab-case** per agenti, skill, comandi
- **YAML frontmatter** obbligatorio su ogni agente / skill / comando (`name`, `description`, opzionali `model` / `color` / `memory`)
- **Niente PII** in `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, o nei doc top-level — istituzioni, advisor, ID di soggetti reali, email, nomi di riviste target, percorsi assoluti. Il contenuto specifico del dominio vive solo sotto `examples/<field>/`.
- Direttiva di lingua **English-first** su tutti gli agenti (pattern di override in AGENTS.md)

Contract completo: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — vedi [LICENSE](LICENSE).
