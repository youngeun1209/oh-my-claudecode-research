[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | Deutsch | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Multi-Agent-Orchestrierung für Claude Code — die Research-Edition. Null Lernkurve.**

_Lernen Sie keine Research-Tools. Nutzen Sie einfach OMCR._

OMCR ist ein Forschungs-Workspace für Claude Code: sechs Agents — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — mit denen Sie an Hypothese, Analyse, Schreiben, Figures, Citations, Review zusammenarbeiten. Sechs Orchestrierungs-Engines automatisieren die häufigen Loops, wenn Sie hands-off wollen. Kombinieren Sie es mit [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode), wenn Sie darüber generische Orchestrierung brauchen (Retries, Parallelität, Budget-Tracking).

Ein 6-Agenten-Forschungsteam + 6 Orchestrierungs-Engines + 7 Setup/Workflow/Utility-Commands + 18 Skills + 4 leichtgewichtige Hooks.

> **Status: v0.1.** Breaking Changes sind wahrscheinlich. Feedback und PRs willkommen.

> **Vollständige Dokumentation:** [`wiki/Home.md`](wiki/Home.md)

> **Verwenden Sie Codex CLI statt Claude Code?** Der Codex-Port liegt unter [oh-my-codex-research](https://github.com/youngeun1209/oh-my-codex-research) (OMXR) — dasselbe 6-Agenten-Forschungsteam, portiert auf OpenAI Codex CLI.

## Quick start

**Step 1: Installation**

**Wenn Sie OMCR zum ersten Mal installieren** — Marketplace-Flow (empfohlen). Das sind Claude-Code-Slash-Commands, **einzeln eingeben**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

Dann:

```
/plugin install oh-my-claudecode-research
```

**Wenn Sie manuellen Checkout bevorzugen** (ohne Plugin-Manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**Wenn OMCR bereits installiert ist und Sie es aktualisieren möchten** — diese zwei Slash-Commands einzeln ausführen:

```
/plugin marketplace update omcr
```

Dann:

```
/plugin update oh-my-claudecode-research
```

Der erste aktualisiert nur die Marketplace-Metadaten; der zweite holt tatsächlich die neuen Plugin-Dateien. OMCR folgt `main`, jeder neue Commit wird also als neue Version behandelt. Ihr Projekt-Status (CLAUDE.md, Agent-Memory, Settings) wird nicht angetastet — Step 2 muss nicht erneut ausgeführt werden.

**Step 2: Setup**

**Muss nur einmal pro Projekt ausgeführt werden.** In einer Claude-Code-Session in Ihrem Forschungsprojekt die Slash-Commands **einzeln** ausführen:

```
/omcr-setup
```

Dann:

```
/start-research
```

`/omcr-setup` legt Infrastruktur: leere `## Project context` / `## Research stack` / `## Language preference`-Blöcke in `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` für alle 6 Agents, leere `paper/references.bib` + `./references.csv` für den literature-curator, und eine kuratierte Permission-Allowlist in `.claude/settings.json`. **Keine Fragen zu Ihrer Forschung.**

`/start-research` ist das Interview. Es führt Sie durch das Füllen jener Platzhalter:
- **Project context** (Working Title, Fachgebiet, Ziel-Venue, zentrale Hypothese, Forschungsthema, Datasets, narrative Linie)
- **Research stack** (Deck-/Outline-Pfade, Figure-Anzahl, BibTeX- + Summary-Table-Pfade, optionale CrossRef-E-Mail)
- **Preset overlay** (optional — `examples/neuro-fmri/` etc. — ersetzt nur `MEMORY.md`-Dateien, die noch byte-identisch mit dem kanonischen Template sind)
- **Manuscript scaffold** (delegiert an den `manuscript-scaffold`-Skill: LaTeX-Skeleton + Journal-Template-Lookup + optionaler Overleaf-Clone)

Wenn Sie `/start-research` vor `/omcr-setup` ausführen, bietet es an, zuerst `/omcr-setup` auszuführen. Übersprungene wissenschaftliche Felder werden als `[TBD: <kurzer Hinweis>]` gespeichert — niemals erfunden — damit `@supervisor` weiß, dass Follow-up nötig ist. Wenn Sie beide überspringen, druckt der SessionStart-Hook `setup-nudge` jede Session einen einzeiligen Reminder, bis Sie initialisieren (mit `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` unterdrücken).

**Step 3: Loslegen**

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

### 7 slash commands (parametrisiert über die CLAUDE.md Ihres Projekts)

| Command | What it does |
|---|---|
| `/omcr-setup` | Installations-Stil: Legt leere `CLAUDE.md`-Markerblöcke, `.claude/agent-memory/`-Verzeichnisse, leere `references.bib`/`references.csv` und eine kuratierte Permission-Allowlist in `.claude/settings.json` an. **Stellt keine Fragen zu Ihrer Forschung.** Einmal pro Projekt ausführen. |
| `/start-research [minimal\|neuro-fmri]` | Interview-Stil: Füllt die `CLAUDE.md`-Platzhalter (Working Title, Hypothese, Ziel-Venue, Datasets, Narrative), wendet optional ein Preset auf Agent-Memory an, scaffoldet das LaTeX-Manuscript-Verzeichnis (via `manuscript-scaffold`-Skill, mit Journal-Template + optionalem Overleaf-Clone). Bietet `/omcr-setup` zuerst auszuführen, falls nicht geschehen. |
| `/todofig [Fig N]` | Vergleicht ein erfasstes Figure-Deck mit einem Outline → priorisierter P0/P1/P2-TODO. |
| `/sync` | Versöhnt den aktuellen Zustand (Deck) mit dem Ziel (Outline), aktualisiert Agent-Memories, bettet optional gecroppte Figures in ein Zieldokument ein. Status-Snapshot, kein TODO. |
| `/session-start [light\|full]` | Read-only Orientierung: liest den Projekt-Korpus (CLAUDE.md, Outline, MEMORY, Wiki-Landingpage), berichtet Zusammenfassung + ehrlichen Status. Keine Nebenwirkungen; light-/full-Modi. |
| `/save-session-log [slug]` | Schreibt einen datierten, getreuen Bericht der Session (Anfragen, Arbeit, berührte Dateien, Entscheidungen, nächste Schritte) in das Session-Logs-Verzeichnis und destilliert anschließend chirurgisch abgesichertes Wissen ins Wiki. |
| `/update-version [@new files]` | Wenn Outline oder Figure-Deck angehoben wird (v4→v5), propagiert den neuen Dateinamen in jede lebende Referenz; bietet an, obsolete Archive zu löschen (bestätigungspflichtig). Liest die alten Werte aus `## Research stack`. |

### 18 skills

Die 7 Setup/Workflow/Utility-Slash-Commands sind Thin Dispatcher — jeder leitet `$ARGUMENTS` an einen entsprechenden Skill weiter. `cropfig`, `verify-citation`, `manuscript-scaffold`, `paper-ingest` sind eigenständig aufrufbar. **Zusätzlich** 1 Primitive (`orchestrate` — intern, setzt sich aus 4 Phasen zusammen) + 6 Engine-Skills, die die 6 Orchestrierungs-Commands stützen; vollständiger Walkthrough in [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Die Tabelle unten deckt die 11 Setup/Workflow/Utility-Skills ab.

| Skill | What it does |
|---|---|
| `omcr-setup` | Stützt `/omcr-setup`. Installations-Stil: Scaffold von `CLAUDE.md`-Markerblöcken, agent-memory-Verzeichnissen, Bibliografie-Dateien, kuratierter Permission-Allowlist. |
| `start-research` | Stützt `/start-research`. Interview-artige Erst-Initialisierung: füllt die gescaffoldeten `CLAUDE.md`-Platzhalter, wendet optional ein Preset-Overlay an, delegiert manuscript scaffold an `manuscript-scaffold`. |
| `sync` | Stützt `/sync`. Versöhnt aktuellen Zustand (erfasstes Figure-Deck) mit Outline; aktualisiert Agent-Memories mit faktischen Drifts; nur Status-Snapshot (kein TODO). |
| `todofig` | Stützt `/todofig`. Vergleicht erfasstes Figure-Deck mit Outline; produziert priorisierten P0/P1/P2-TODO für Gaps. |
| `cropfig` | Drei-Schritt-Pipeline von einem `.key`/`.pptx`-Deck zu Manuscript- + Outline-Artefakten: pro-Slide-Vektor-PDFs (gecroppt, manuscript-grade) + outline-grade-PNGs. Direkt oder durch andere Commands aufgerufen; kein Slash. |
| `verify-citation` | Existenz- + Metadaten-Check via CrossRef/OpenAlex. Gatet jeden Eintrag, den `@literature-curator` hinzufügt, schreibt das Verifikations-Urteil in die Summary-Table des Projekts. |
| `manuscript-scaffold` | Kopiert das gebündelte LaTeX-Skeleton in das Manuscript-Verzeichnis des Nutzers, wendet optional ein journal-spezifisches `\documentclass` aus dem gebündelten Registry an, klont optional ein Overleaf-Projekt (Token wird nie in tracked Dateien persistiert), commitet auf den Default-Branch, fragt vor dem Push. Wird von `/start-research` Phase 6 aufgerufen; auch eigenständig aufrufbar. |
| `paper-ingest` | Nimmt ein gelesenes Paper (PDF / DOI / URL) in eine zweigeteilte **Reading Library** auf — projektunabhängige Zusammenfassung + gecroppte Hauptfigure + `index.csv`-Zeile, danach eine relevanzgegatete Projekt-Nutzungsnotiz. Nutzt `verify-citation` + `cropfig` wieder. Getrennt von der Manuscript-BibTeX. Eigenständig. |
| `session-start` | Stützt `/session-start`. Read-only Projekt-Orientierung (Korpus-Lektüre + Statusbericht; light-/full-Modi). |
| `save-session-log` | Stützt `/save-session-log`. Datierter Session-Bericht + chirurgische Wiki-Destillation abgesicherten Wissens. |
| `update-version` | Stützt `/update-version`. Propagiert Outline-/Deck-Versionssprünge über jeden lebenden Pointer; datierte historische Records bleiben eingefroren. |

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
- **[Reading Library](wiki/Reading-Library.md)** — `paper-ingest`: gelesene Papers ablegen (getrennt von der Manuscript-BibTeX)
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
