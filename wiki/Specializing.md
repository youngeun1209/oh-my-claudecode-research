# Specializing for Your Field

OMCR's 5 core agents are field-neutral. To make them concrete for your domain, author a **preset** under `examples/<field>/`. The shipped example is `examples/neuro-fmri/` (Mapper-on-fMRI). This page walks through authoring your own.

## When you need a preset

You probably need a preset if any of these are true:

- Your field has specific libraries / atlases / databases that `@analysis-implementer` should know about by default (e.g., `nilearn` for fMRI, `Biopython` for genomics, `astropy` for astronomy).
- Your field has venue-specific conventions for figures (e.g., neuroscience figures use the Schaefer atlas color scheme; particle physics has specific plot types).
- Your field has typical reviewer attacks `@reviewer` should be primed for (e.g., "are you sure this isn't a confound from X?").
- Your project's memory files would benefit from field-specific scaffolds (e.g., a neuro project tracks atlas choice, scrubbing thresholds; a wet-lab project tracks PCR conditions, antibody lot numbers).

You probably **don't** need a preset if:
- You're an early-career researcher who hasn't locked into specific tooling yet — the generic agents will do.
- Your project crosses multiple fields (preset = single field).
- You want maximum portability and minimal customization.

## Preset structure

```
examples/<field>/
├── README.md                              # this preset's overview + install recipe
├── agents/
│   └── analysis-implementer.md            # field-flavored body (almost always present)
│   └── reviewer.md                        # if your field has specific attack vectors
│   └── figure-descriptor.md               # if your field has specific plot conventions
└── memory-templates/                      # redacted MEMORY.md skeletons per agent
    ├── supervisor/MEMORY.md
    ├── analysis-implementer/MEMORY.md
    ├── paper-writer/MEMORY.md
    ├── figure-descriptor/MEMORY.md
    └── reviewer/MEMORY.md
```

Not all 5 agents need a preset variant. In practice:
- **`analysis-implementer`** — almost always needs a preset (tooling and methodology differ most)
- **`figure-descriptor`** — often needs a preset (plot conventions differ)
- **`reviewer`** — sometimes needs a preset (attack vectors differ)
- **`supervisor`** — rarely needs a preset (PI role is field-agnostic)
- **`paper-writer`** — rarely needs a preset (high-impact prose is similar everywhere)

## 4-step recipe

### Step 1 — Identify needed agent overlays

Read each core agent (`agents/*.md`) and ask: "Would a domain expert add anything domain-specific to this?" For each one where the answer is yes, you'll create an overlay.

### Step 2 — Decide what specific knowledge each overlay needs

For `analysis-implementer`, typically:
- Canonical libraries (e.g., `nilearn`, `Biopython`, `astropy`, `huggingface-transformers`, `torch-geometric`)
- Methodology overview (e.g., "preprocessing → modeling → statistical test" specific to your pipeline)
- Common pitfalls (e.g., "TR not accounted for in bandpass filter" — fMRI; "p-value inflation from peeking" — RCT)
- Statistical conventions (e.g., spin tests for parcellated brain data; FDR vs FWER preference)

For `figure-descriptor`, typically:
- Canonical color palette (with hex codes)
- Plot-type conventions (e.g., raincloud > bar plot for group comparisons in neuro)
- Atlas / chart / map conventions (e.g., MNI space orientation labels for brain figures)
- Field-specific typography or sizing conventions

For `reviewer`, typically:
- Specific attack vectors (e.g., "your method is just dimensional reduction with extra steps")
- Field-specific significance thresholds (e.g., p < 0.001 for fMRI vs p < 0.05 elsewhere)
- Reproducibility expectations (e.g., must show test-retest reliability for fMRI methods)

### Step 3 — Produce redacted memory skeletons

For each of the 5 agents (including ones whose body you didn't overlay), produce a `MEMORY.md` skeleton showing what an agent in your field typically tracks. **Redact concrete project content** — leave placeholder fields (`[PROJECT_TITLE]`, `[TARGET_VENUE]`, etc.) but show the structure.

For example, a wet-lab biology `analysis-implementer/MEMORY.md` might track:
- Cell line identity + STR profile date
- Antibody lot numbers + validation status
- PCR primer sequences + Tm
- Statistical analysis software version
- Data deposition (GEO / SRA / ENA) submission status

A particle physics version might track:
- Detector configuration version
- Triggering thresholds
- Monte Carlo generator + version
- Pile-up correction method
- Systematic uncertainty estimation approach

Use the canonical `templates/MEMORY.template.md` as a starting structure, then add field-specific sections.

### Step 4 — Write a `README.md` for the preset

Mirror `examples/neuro-fmri/README.md`. Include:

- One-paragraph description of the preset
- File tree of what's in this directory
- Install recipe (overlay commands)
- "What this preset adds vs. the field-neutral core" table
- "Adapt to your stack" notes for users in adjacent fields
- (Optional) "Author your own preset" pointer back here

### Step 5 (optional) — Submit a PR

PRs adding new presets are welcome on the main repo. Quality bar:

- Field-specific content stays under `examples/<field>/` — does not leak into `agents/` or `commands/` at the repo root
- No PII (advisor names, real subject IDs, lab-internal URLs)
- Redacted memory skeletons (no real project data)
- `README.md` follows the canonical structure
- Frontmatter on every `.md` agent / skill file

## Worked example — what `examples/neuro-fmri/` does

The neuro-fmri preset overlays only `analysis-implementer` because:
- `supervisor`, `paper-writer`, `figure-descriptor`, `reviewer` work as-is with placeholder fills via project CLAUDE.md
- `analysis-implementer`'s neuro-flavored body adds: nilearn / kepler-mapper / Schaefer parcellation expertise, fMRI preprocessing pitfalls (TR / scrubbing / confound regression), Mapper-specific debugging patterns, MATLAB-Python interop conventions

It also ships redacted memory skeletons for all 5 agents because each agent in a Mapper-on-fMRI project tracks a distinctive set of state:
- `supervisor/MEMORY.md` — hypothesis log, literature anchors, narrative spine evolution
- `analysis-implementer/MEMORY.md` — Mapper hyperparameters, subject exclusions, pipeline state
- `paper-writer/MEMORY.md` — section status, nomenclature decisions (intrinsic scaffold vs. manifold), venue requirements
- `figure-descriptor/MEMORY.md` — color system (condition → color mapping), figure list with status
- `reviewer/MEMORY.md` — Mapper-specific attack vectors (parameter sensitivity, projection circularity), open concerns

The pattern transfers to other fields with substitutions: swap "Mapper" for your method, swap "fMRI" for your data modality, swap the attack vectors for the ones reviewers in your field use.

## See also

- [`examples/neuro-fmri/README.md`](../examples/neuro-fmri/README.md) — the canonical worked example
- [Agents](Agents.md) — the 5 core agents being overlaid
- [CONTRIBUTING](../CONTRIBUTING.md) — full contribution contract (frontmatter / MEMORY schema / PII / commits)
