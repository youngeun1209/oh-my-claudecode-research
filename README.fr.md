[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | Français | [Italiano](README.it.md)

# oh-my-claudecode-research

**Orchestration multi-agents pour Claude Code — édition recherche. Courbe d'apprentissage zéro.**

_N'apprenez pas les outils de recherche. Utilisez simplement OMCR._

OMCR est un espace de travail de recherche pour Claude Code : six agents — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — avec qui vous travaillez côte à côte sur l'hypothèse, l'analyse, l'écriture, les figures, les citations, la review. Six moteurs d'orchestration automatisent les boucles courantes quand vous voulez du hands-off. Combinez-le avec [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) si vous avez besoin par-dessus d'orchestration générique (retries, parallélisme, contrôle de budget).

Une équipe de recherche de 6 agents + 6 moteurs d'orchestration + 7 commandes setup/workflow/utilitaires + 18 skills + 4 hooks légers.

> **Statut : v0.1.** Des breaking changes sont probables. Feedback et PRs bienvenus.

> **Documentation complète :** [`wiki/Home.md`](wiki/Home.md)

> **Vous utilisez Codex CLI plutôt que Claude Code ?** Le port Codex se trouve à [oh-my-codex-research](https://github.com/youngeun1209/oh-my-codex-research) (OMXR) — la même équipe de recherche de 6 agents, portée sur OpenAI Codex CLI.

## Quick start

**Step 1: Installation**

**Si vous installez OMCR pour la première fois** — flux marketplace (recommandé). Ce sont des commandes slash de Claude Code, saisissez-les **une à la fois** :

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

Ensuite :

```
/plugin install oh-my-claudecode-research
```

**Si vous préférez le checkout manuel** (sans gestionnaire de plugins) :

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**Si OMCR est déjà installé et que vous voulez le mettre à jour** — lancez ces deux commandes slash une à la fois :

```
/plugin marketplace update omcr
```

Ensuite :

```
/plugin update oh-my-claudecode-research
```

La première rafraîchit seulement les métadonnées du marketplace ; la seconde récupère réellement les nouveaux fichiers du plugin. OMCR suit `main`, donc chaque nouveau commit est traité comme une nouvelle version. L'état de votre projet (CLAUDE.md, mémoire d'agents, settings) n'est pas touché — pas besoin de relancer le Step 2.

**Step 2: Configuration**

**À faire une seule fois par projet.** Dans une session Claude Code de votre projet de recherche, lancez les commandes slash **une à la fois** :

```
/omcr-setup
```

Ensuite :

```
/start-research
```

`/omcr-setup` pose l'infrastructure — blocs vides `## Project context` / `## Research stack` / `## Language preference` dans `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` pour les 6 agents, `paper/references.bib` + `./references.csv` vides pour le literature-curator, et une allowlist de permissions curée dans `.claude/settings.json`. **Aucune question sur votre recherche.**

`/start-research` est l'entretien. Il vous guide pour remplir ces placeholders :
- **Project context** (working title, domaine, venue cible, hypothèse centrale, sujet de recherche, datasets, fil narratif)
- **Research stack** (chemins deck/outline, nombre de figures, chemins BibTeX + summary-table, email CrossRef optionnel)
- **Preset overlay** (optionnel — `examples/neuro-fmri/` etc. — remplace uniquement les fichiers `MEMORY.md` d'agents toujours byte-identiques au template canonique)
- **Manuscript scaffold** (délègue au skill `manuscript-scaffold` : LaTeX skeleton + lookup de template de revue + clone Overleaf optionnel)

Si vous lancez `/start-research` avant `/omcr-setup`, il propose de lancer `/omcr-setup` d'abord. Les champs scientifiques sautés sont sauvés comme `[TBD: <note courte>]` — jamais inventés — pour que `@supervisor` sache faire le suivi. Si vous sautez les deux, le hook `setup-nudge` de SessionStart imprime un rappel d'une ligne à chaque session jusqu'à initialisation (supprimer avec `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Démarrer**

```
@supervisor where are we?
```

Walkthrough complet : [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Gardien de la vision scientifique au niveau PI + orchestrateur de projet. Détient l'hypothèse centrale ; délègue aux sous-agents. |
| `@analysis-implementer` | Implémente des pipelines, analyses statistiques, modèles ML/simulation. Neutre par défaut quant au domaine. |
| `@paper-writer` | Rédige les sections du manuscrit à la qualité de prose d'une revue à fort impact. |
| `@figure-descriptor` | Conçoit des figures comme des briefs prêts à implémenter — ne génère pas d'images. |
| `@reviewer` | Review adversariale avant soumission au niveau du venue cible. |
| `@literature-curator` | Maintient en lockstep le BibTeX et la table récapitulative de la littérature du projet. Résout les placeholders `[CITE: ...]`, vérifie les citations via le skill `verify-citation`, ne fabrique jamais. |

### 7 slash commands (paramétrés via le CLAUDE.md de votre projet)

| Command | What it does |
|---|---|
| `/omcr-setup` | Style installation : pose des blocs marqueurs vides dans `CLAUDE.md`, les répertoires `.claude/agent-memory/`, des `references.bib`/`references.csv` vides, et une allowlist de permissions curée dans `.claude/settings.json`. **Aucune question sur votre recherche.** Exécuter une fois par projet. |
| `/start-research [minimal\|neuro-fmri]` | Style entretien : remplit les placeholders de `CLAUDE.md` (working title, hypothèse, venue cible, datasets, fil narratif), applique optionnellement un preset à la mémoire des agents, scaffold le répertoire LaTeX du manuscrit (via le skill `manuscript-scaffold`, avec template de revue + clone Overleaf optionnel). Propose de lancer `/omcr-setup` d'abord s'il n'a pas été fait. |
| `/todofig [Fig N]` | Compare un deck de figures capturé à un outline → TODO priorisé P0/P1/P2. |
| `/sync` | Réconcilie l'état courant (deck) avec l'objectif (outline), rafraîchit les mémoires des agents, embarque optionnellement les figures croppées dans un document cible. Snapshot d'état, pas un TODO. |
| `/session-start [light\|full]` | Orientation en lecture seule : lit le corpus du projet (CLAUDE.md, outline, MEMORY, page d'accueil du wiki), rapporte un résumé + un statut honnête. Zéro effet de bord ; modes light/full. |
| `/save-session-log [slug]` | Écrit un enregistrement daté et fidèle de la session (requêtes, travail effectué, fichiers touchés, décisions, prochaines étapes) dans le répertoire des session-logs, puis distille chirurgicalement les connaissances stabilisées dans le wiki. |
| `/update-version [@new files]` | Quand l'outline ou le deck de figures est bumpé (v4→v5), propage le nouveau nom de fichier dans chaque référence vivante ; propose de supprimer les archives obsolètes (confirmation requise). Lit les anciennes valeurs depuis `## Research stack`. |

### 18 skills

Les 7 commandes slash setup/workflow/utilitaires sont des thin dispatchers — chacune forwarde `$ARGUMENTS` à un skill correspondant. `cropfig`, `verify-citation`, `manuscript-scaffold`, `paper-ingest` sont aussi appelables de manière indépendante. **De plus** 1 primitive (`orchestrate` — interne, se compose via 4 phases) + 6 engine skills qui supportent les 6 commandes d'orchestration ; walkthrough complet dans [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Le tableau ci-dessous couvre les 11 skills setup/workflow/utilitaires.

| Skill | What it does |
|---|---|
| `omcr-setup` | Supporte `/omcr-setup`. Style installation : scaffold des blocs marqueurs `CLAUDE.md`, des répertoires agent-memory, des fichiers de bibliographie, d'une allowlist de permissions curée. |
| `start-research` | Supporte `/start-research`. Init style entretien du premier projet : remplit les placeholders `CLAUDE.md` déjà scaffoldés, applique optionnellement un preset overlay, délègue le manuscript scaffold à `manuscript-scaffold`. |
| `sync` | Supporte `/sync`. Réconcilie l'état courant (deck de figures capturé) avec l'outline ; rafraîchit les mémoires d'agents avec les drifts factuels ; uniquement snapshot d'état (pas de TODO). |
| `todofig` | Supporte `/todofig`. Compare un deck de figures capturé avec l'outline ; produit un TODO priorisé P0/P1/P2 des gaps. |
| `cropfig` | Pipeline en trois étapes d'un deck `.key`/`.pptx` aux artefacts manuscrit + outline : PDFs vectoriels par slide (croppés, manuscript-grade) + PNGs niveau outline. Appelée directement ou par d'autres commandes ; pas de slash. |
| `verify-citation` | Vérification d'existence + métadonnées via CrossRef/OpenAlex. Gate chaque entrée que `@literature-curator` ajoute, écrit le verdict de vérification dans la summary table du projet. |
| `manuscript-scaffold` | Copie le LaTeX skeleton fourni dans le répertoire manuscrit de l'utilisateur, applique optionnellement un `\documentclass` spécifique au journal depuis le registry fourni, clone optionnellement un projet Overleaf (token jamais persisté dans des fichiers tracked), commit sur la branche par défaut, demande avant push. Appelé par `/start-research` phase 6 ; aussi appelable de manière indépendante. |
| `paper-ingest` | Ingère un papier que vous avez lu (PDF/DOI/URL) dans une **reading library** à deux dossiers — résumé agnostique au projet + figure principale croppée + ligne `index.csv`, puis une note d'usage-projet gated par pertinence. Réutilise `verify-citation` + `cropfig`. Séparé du BibTeX du manuscrit. Standalone. |
| `session-start` | Supporte `/session-start`. Orientation de projet en lecture seule (lecture du corpus + rapport de statut ; modes light/full). |
| `save-session-log` | Supporte `/save-session-log`. Enregistrement daté de session + distillation chirurgicale des connaissances stabilisées dans le wiki. |
| `update-version` | Supporte `/update-version`. Propage les bumps de version de l'outline/deck à travers chaque pointeur vivant ; les enregistrements historiques datés restent figés. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Bloque les writes contenant des PII (par défaut : emails / SSNs / subject IDs ; configurable). |
| `memory-load` | `SessionStart` | Auto-injecte `.claude/agent-memory/*/MEMORY.md` dans le contexte de session. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Avertissement heuristique non bloquant quand le markdown du manuscrit a des paragraphes non cités. |
| `setup-nudge` | `SessionStart` | Coup de coude non bloquant en une ligne pour lancer `/omcr-setup` puis `/start-research` si CLAUDE.md n'a pas les blocs `## Project context` ou `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — hub de navigation
- **[Getting Started](wiki/Getting-Started.md)** — installation + première session
- **[Configuration](wiki/Configuration.md)** — bloc Research stack, variables d'env, patterns PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — utiliser OMCR seul, walkthrough complet
- **[With OMC](wiki/With-OMC.md)** — full stack : installation OMCR + companion OMC
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — références
- **[Reading Library](wiki/Reading-Library.md)** — `paper-ingest` : archivez les papiers que vous lisez (séparé du BibTeX du manuscrit)
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 outils OMC MCP mappés aux étapes de recherche
- **[Specializing](wiki/Specializing.md)** — créer un preset spécifique à un champ

## Specializing for your field

Les agents et commandes du core sont neutres quant au domaine. Pour une saveur spécifique au domaine (ex : méthodologie neuroscience, conventions wet-lab, idiomes d'évaluation ML), superposez un preset depuis `examples/<field>/`. Actuellement fournis :

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — spécialisation neuro-fMRI générique. Fournit un corps `analysis-implementer` à saveur neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + squelettes MEMORY.md redacted pour les 6 agents.

Overlay rapide :

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Pour créer votre propre preset : voir [`wiki/Specializing.md`](wiki/Specializing.md). Les PRs ajoutant de nouveaux presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) sont bienvenus.

## OMC companion (recommended)

OMCR traite [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) comme un *companion*, pas une dépendance. Avec OMC installé à côté, les composants suivants s'intègrent naturellement dans les workflows de recherche. Choisissez ceux pertinents pour votre projet — pas besoin de tout utiliser.

| Component | Why for research |
|---|---|
| `@scientist` agent | Imposant la rigueur statistique (intervalles de confiance / p-values / tailles d'effet / marqueurs `[LIMITATION]`). Companion de `@analysis-implementer`. |
| `@document-specialist` agent | Recherche de littérature plus lourde appuyée par le Context Hub d'OMC (fetches cachés, notes structurées). À utiliser avec `@literature-curator` quand un deep dive à l'échelle d'une survey est nécessaire ; le curator d'OMCR gère seul la résolution de citation par claim et la tenue BibTeX/summary-table. |
| `@verifier` agent | Vérifications de complétude basées preuves — rejette les affirmations "should work" sans output de test frais. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Classement d'hypothèses concurrentes basé preuves + disconfirmation. Se mappe à la validation methods/results. |
| `@writer` agent | Rédacteur de documentation technique pour protocoles de labo, appendices methods, guides de reproductibilité. |
| `@test-engineer` agent | Discipline TDD pour la couverture des edge cases des scripts d'analyse. |
| `@git-master` agent | Discipline atomic-commit — étapes d'analyse indépendamment revertables. |
| `/oh-my-claudecode:autoresearch` skill | Boucle d'itération bounded evaluator-driven avec JSON + decision log par itération. |
| `/oh-my-claudecode:deep-interview` skill | Clarification socratique d'objectifs de recherche flous en hypothèses testables. |
| Skills d'orchestration OMC (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Orchestrateurs multi-itération / parallèle / consensus pour les runs d'analyse, les balayages de littérature, les révisions must-finish. Voir [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) pour 5 recettes concrètes. |
| Outils MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki de littérature / registre d'hypothèses / registry de runs d'expérimentation / REPL Python stateful. |

Installez OMC à côté via le Claude Code marketplace, ou `npm i -g oh-my-claude-sisyphus`. Mapping complet : [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Noms de fichiers en **kebab-case** pour agents, skills, commandes
- **YAML frontmatter** obligatoire sur chaque agent / skill / commande (`name`, `description`, optionnellement `model` / `color` / `memory`)
- **Pas de PII** dans `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, ou les docs top-level — institutions, encadrants, IDs sujets réels, emails, noms de revues cibles, chemins absolus. Le contenu spécifique au domaine vit uniquement sous `examples/<field>/`.
- Directive de langue **English-first** sur tous les agents (pattern d'override dans CLAUDE.md)

Contract complet : [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — voir [LICENSE](LICENSE).
