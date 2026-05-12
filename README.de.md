[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | Deutsch | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Multi-Agent-Orchestrierung für Claude Code — die Research-Edition. Null Lernkurve.**

_Lernen Sie keine Research-Tools. Nutzen Sie einfach OMCR._

OMCR ist das forschungsorientierte Geschwister von [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode). Während OMC allgemeine Code-Arbeit mit Execution Engines (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`) orchestriert, orchestriert OMCR den *Forschungs-Workflow* mit **6 domänenspezifischen Engines** — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` und der autonomen `/supervisor-drive`. Einzeln oder kombiniert nutzbar: OMCR-Engines laufen innerhalb von OMCs generischen Loops für Retries (`/ralph`), Parallelität (`/team`, `/ultrawork`), Multi-Strategie-Erkundung (`/ultraqa`) oder budgetgetrackte Drives (`/autopilot`). Vollständige task → tool-Matrix in [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md), praktische Rezepte in [`wiki/With-OMC.md`](wiki/With-OMC.md).

Ein 6-Agenten-Forschungsteam + 6 Orchestrierungs-Engines + 4 Setup/Workflow-Commands + 14 Skills (1 Primitive + 13 Backing Surfaces) + 4 leichtgewichtige Hooks. Vollständiger Engine-Walkthrough: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **Status: v0.1.** Breaking Changes sind wahrscheinlich. Feedback und PRs willkommen.

> **Vollständige Dokumentation:** [`wiki/Home.md`](wiki/Home.md)

## Install

**Empfohlen — Claude Code Marketplace** (ein Slash-Command pro Zeile, einzeln eingeben):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Alternative — manueller Checkout** (ohne Plugin-Manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Dann Claude Code öffnen und `/plugin` ausführen, um zu laden. Nach dem Laden (egal über welchen Pfad):
- 6 Agents erscheinen im `@`-mention-Picker
- 10 Slash-Commands erscheinen im Picker: `/omcr-setup`, `/start-research`, `/todofig`, `/sync` (Setup/Workflow) + `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` (Orchestrierungs-Engines)
- 14 Skills werden aufrufbar (7 Setup/Workflow + 1 Primitive `orchestrate` + 6 Engine-Skills)
- 4 Hooks registrieren sich beim Session-Start (PII-Schutz, MEMORY-Auto-Load, Citation-Warnung, Setup-Nudge)

**Cherry-Pick pro Datei** (ohne Plugin-Manager — kopiert Agents in ein bestimmtes Projekt):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Dieser Weg überspringt Commands, Skills und Hooks. Für vollständige Funktion verwenden Sie die Plugin-Installation.

## Quick start

Nach Installation ein Research-Projekt öffnen und in dieser Reihenfolge ausführen:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** ist installations-artig — keine Fragen zu Ihrer Forschung. Legt nur Infrastruktur: leere `## Project context` / `## Research stack` / `## Language preference`-Blöcke in `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` für alle 6 Agents (kanonisches Template), leere `paper/references.bib` + `./references.csv` für den literature-curator, und eine kuratierte Permission-Allowlist in `.claude/settings.json` (read-only git, Dateisuche, LaTeX-Build, Citation-API, Figure-Crop — opt-in für Python-Analyse; git write und Dateilöschung bleiben manuell).

**`/start-research`** ist das Interview. Es führt Sie durch das Füllen jener Platzhalter:
- **Project context** (Working Title, Fachgebiet, Ziel-Venue, zentrale Hypothese, Forschungsthema, Datasets, narrative Linie)
- **Research stack** (Deck-/Outline-Pfade, Figure-Anzahl, BibTeX- + Summary-Table-Pfade, optionale CrossRef-E-Mail)
- **Preset overlay** (optional — `examples/neuro-fmri/` etc. — ersetzt nur `MEMORY.md`-Dateien, die noch byte-identisch mit dem kanonischen Template sind)
- **Manuscript scaffold** (delegiert an den `manuscript-scaffold`-Skill: LaTeX-Skeleton + Journal-Template-Lookup + optionaler Overleaf-Clone)

Wenn Sie `/start-research` vor `/omcr-setup` ausführen, bietet es an, zuerst `/omcr-setup` auszuführen. Übersprungene wissenschaftliche Felder werden als `[TBD: <kurzer Hinweis>]` gespeichert — niemals erfunden — damit `@supervisor` weiß, dass Follow-up nötig ist.

Wenn Sie beide überspringen, druckt der SessionStart-Hook `setup-nudge` jede Session einen einzeiligen Reminder, bis Sie initialisieren. Mit `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` unterdrücken.

Nach beidem ein echtes Gespräch beginnen:

```
@supervisor where are we?
```

Vollständiger Walkthrough: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Hüter der wissenschaftlichen Vision auf PI-Niveau + Projekt-Orchestrator. Besitzt die zentrale Hypothese; delegiert an Subagents. |
| `@analysis-implementer` | Implementiert Pipelines, statistische Analysen, ML-/Simulationsmodelle. Standardmäßig fachneutral. |
| `@paper-writer` | Verfasst Manuscript-Abschnitte in der Prosa-Qualität von High-Impact-Journals. |
| `@figure-descriptor` | Entwirft Abbildungen als implementierungsreife Briefs — generiert keine Bilder. |
| `@reviewer` | Adversariale Vor-Einreichungs-Review auf Niveau des Ziel-Venues. |
| `@literature-curator` | Pflegt BibTeX und Literatur-Summary-Tabelle des Projekts im Lockstep. Löst `[CITE: ...]`-Platzhalter auf, verifiziert Zitate per `verify-citation`-Skill, fabriziert niemals. |

### 4 slash commands (parametrisiert über die CLAUDE.md Ihres Projekts)

| Command | What it does |
|---|---|
| `/omcr-setup` | Installations-Stil: Legt leere `CLAUDE.md`-Markerblöcke, `.claude/agent-memory/`-Verzeichnisse, leere `references.bib`/`references.csv` und eine kuratierte Permission-Allowlist in `.claude/settings.json` an. **Stellt keine Fragen zu Ihrer Forschung.** Einmal pro Projekt ausführen. |
| `/start-research [minimal\|neuro-fmri]` | Interview-Stil: Füllt die `CLAUDE.md`-Platzhalter (Working Title, Hypothese, Ziel-Venue, Datasets, Narrative), wendet optional ein Preset auf Agent-Memory an, scaffoldet das LaTeX-Manuscript-Verzeichnis (via `manuscript-scaffold`-Skill, mit Journal-Template + optionalem Overleaf-Clone). Bietet `/omcr-setup` zuerst auszuführen, falls nicht geschehen. |
| `/todofig [Fig N]` | Vergleicht ein erfasstes Figure-Deck mit einem Outline → priorisierter P0/P1/P2-TODO. |
| `/sync` | Versöhnt den aktuellen Zustand (Deck) mit dem Ziel (Outline), aktualisiert Agent-Memories, bettet optional gecroppte Figures in ein Zieldokument ein. Status-Snapshot, kein TODO. |

### 14 skills

Die 4 Setup/Workflow-Slash-Commands sind Thin Dispatcher — jeder leitet `$ARGUMENTS` an einen entsprechenden Skill weiter. `cropfig`, `verify-citation`, `manuscript-scaffold` sind eigenständig aufrufbar. **Zusätzlich** 1 Primitive (`orchestrate` — intern, setzt sich aus 4 Phasen zusammen) + 6 Engine-Skills, die die 6 Orchestrierungs-Commands stützen; vollständiger Walkthrough in [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Die Tabelle unten deckt die 7 Setup/Workflow-Skills ab.

| Skill | What it does |
|---|---|
| `omcr-setup` | Stützt `/omcr-setup`. Installations-Stil: Scaffold von `CLAUDE.md`-Markerblöcken, agent-memory-Verzeichnissen, Bibliografie-Dateien, kuratierter Permission-Allowlist. |
| `start-research` | Stützt `/start-research`. Interview-artige Erst-Initialisierung: füllt die gescaffoldeten `CLAUDE.md`-Platzhalter, wendet optional ein Preset-Overlay an, delegiert manuscript scaffold an `manuscript-scaffold`. |
| `sync` | Stützt `/sync`. Versöhnt aktuellen Zustand (erfasstes Figure-Deck) mit Outline; aktualisiert Agent-Memories mit faktischen Drifts; nur Status-Snapshot (kein TODO). |
| `todofig` | Stützt `/todofig`. Vergleicht erfasstes Figure-Deck mit Outline; produziert priorisierten P0/P1/P2-TODO für Gaps. |
| `cropfig` | Drei-Schritt-Pipeline von einem `.key`/`.pptx`-Deck zu Manuscript- + Outline-Artefakten: pro-Slide-Vektor-PDFs (gecroppt, manuscript-grade) + outline-grade-PNGs. Direkt oder durch andere Commands aufgerufen; kein Slash. |
| `verify-citation` | Existenz- + Metadaten-Check via CrossRef/OpenAlex. Gatet jeden Eintrag, den `@literature-curator` hinzufügt, schreibt das Verifikations-Urteil in die Summary-Table des Projekts. |
| `manuscript-scaffold` | Kopiert das gebündelte LaTeX-Skeleton in das Manuscript-Verzeichnis des Nutzers, wendet optional ein journal-spezifisches `\documentclass` aus dem gebündelten Registry an, klont optional ein Overleaf-Projekt (Token wird nie in tracked Dateien persistiert), commitet auf den Default-Branch, fragt vor dem Push. Wird von `/start-research` Phase 6 aufgerufen; auch eigenständig aufrufbar. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Blockt Writes mit PII (standardmäßig: E-Mails / SSNs / Subject-IDs; konfigurierbar). |
| `memory-load` | `SessionStart` | Injiziert `.claude/agent-memory/*/MEMORY.md` automatisch in den Session-Kontext. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Heuristische, nicht-blockierende Warnung, wenn Manuscript-Markdown unzitierte Absätze hat. |
| `setup-nudge` | `SessionStart` | Einzeiliger, nicht-blockierender Anstoß, `/omcr-setup` dann `/start-research` zu starten, wenn in CLAUDE.md die Blöcke `## Project context` oder `## Research stack` fehlen. |

## Documentation

- **[Wiki home](wiki/Home.md)** — Navigations-Hub
- **[Getting Started](wiki/Getting-Started.md)** — Installation + erste Session
- **[Configuration](wiki/Configuration.md)** — Research-stack-Block, env-Variablen, PII-Pattern
- **[Standalone Usage](wiki/Standalone-Usage.md)** — OMCR allein nutzen, vollständiger Walkthrough
- **[With OMC](wiki/With-OMC.md)** — Full Stack: OMCR + OMC-Companion-Installation
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — Referenzen
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 OMC-MCP-Tools auf Forschungsphasen gemappt
- **[Specializing](wiki/Specializing.md)** — fachspezifisches Preset autoren

## Specializing for your field

Core-Agents und -Commands sind fachneutral. Für domänenspezifischen Geschmack (z. B. Neuroscience-Methodologie, Wet-Lab-Konventionen, ML-Eval-Idiome) ein Preset aus `examples/<field>/` überlagern. Aktuell ausgeliefert:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generische neuro-fMRI-Spezialisierung. Liefert einen neuro-gefärbten `analysis-implementer`-Body (preprocessing / parcellation / connectivity / ISC / spin tests) + redacted MEMORY.md-Skelette für alle 6 Agents.

Schnelles Overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Eigenes Preset autoren: siehe [`wiki/Specializing.md`](wiki/Specializing.md). PRs mit neuen Presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) willkommen.

## OMC companion (recommended)

OMCR behandelt [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) als *Companion*, nicht als Dependency. Mit nebenher installiertem OMC passen folgende Komponenten natürlich in Forschungs-Workflows. Wählen Sie die, die für Ihr Projekt relevant sind — Sie müssen nicht alle nutzen.

| Component | Why for research |
|---|---|
| `@scientist` agent | Durchsetzer statistischer Strenge (CIs / p-Werte / Effektgrößen / `[LIMITATION]`-Marker). Companion zu `@analysis-implementer`. |
| `@document-specialist` agent | Schwerergewichtige Literatur-Recherche gestützt auf OMCs Context Hub (gecachte Fetches, strukturierte Notizen). Mit `@literature-curator` verwenden, wenn ein Deep Dive in Survey-Größe nötig ist; OMCRs Curator erledigt per-claim-Citation-Auflösung und BibTeX-/Summary-Table-Buchhaltung selbst. |
| `@verifier` agent | Evidenzbasierte Fertigstellungs-Checks — lehnt "should work"-Behauptungen ohne frischen Test-Output ab. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Evidenzgetriebene Ranking-Konkurrenz-Hypothesen + Disconfirmation. Mappt auf Methods/Results-Validierung. |
| `@writer` agent | Tech-Dokumentations-Schreiber für Lab-Protokolle, Methods-Appendices, Reproduzierbarkeits-Guides. |
| `@test-engineer` agent | TDD-Disziplin für Edge-Case-Coverage von Analyse-Skripten. |
| `@git-master` agent | Atomic-Commit-Disziplin — unabhängig revertierbare Analyseschritte. |
| `/oh-my-claudecode:autoresearch` skill | Bounded evaluator-driven Iterations-Loop mit Per-Iteration-JSON + Decision-Log. |
| `/oh-my-claudecode:deep-interview` skill | Sokratische Klärung vager Forschungsziele in testbare Hypothesen. |
| OMC-Orchestrierungs-Skills (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Multi-Iteration- / Parallel- / Konsens-Orchestratoren für Analyse-Runs, Literatur-Scans, Must-Finish-Revisions. 5 praktische Rezepte: [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc). |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP-Tools | Literatur-Wiki / Hypothesen-Register / Experiment-Run-Registry / stateful Python-REPL. |

OMC nebenher über Claude Code Marketplace oder `npm i -g oh-my-claude-sisyphus` installieren. Vollständiges Mapping: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- **kebab-case**-Dateinamen für Agents, Skills, Commands
- **YAML-Frontmatter** verpflichtend auf jedem Agent / Skill / Command (`name`, `description`, optional `model` / `color` / `memory`)
- **Kein PII** in `agents/`, `commands/`, `skills/`, `templates/`, `hooks/` oder Top-Level-Docs — Institutionen, Betreuer, echte Subject-IDs, E-Mails, Ziel-Journal-Namen, absolute Pfade. Domänenspezifischer Inhalt lebt nur unter `examples/<field>/`.
- **English-first**-Sprachdirektive auf allen Agents (Override-in-CLAUDE.md-Pattern)

Vollständiger Contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — siehe [LICENSE](LICENSE).
