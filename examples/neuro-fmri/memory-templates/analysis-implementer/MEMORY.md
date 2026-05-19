# analysis-implementer agent — memory (redacted skeleton)

> **Skeleton only.** Concrete pipeline parameters, subject IDs, atlas choices,
> and bug-fix narratives have been stripped. Copy into your own project's
> `.claude/agent-memory/analysis-implementer/MEMORY.md` and fill in.

**Last synced:** [YYYY-MM-DD]

---

## Pipeline state
| Stage | Status | Canonical params | Output path |
|-------|--------|------------------|-------------|
| 1. [Stage name] | validated / draft / TODO | [param block ref] | [path] |
| 2. [Stage name] | ... | ... | ... |

## Result-to-code mapping
| Result | Script(s) | Inputs | Outputs |
|--------|-----------|--------|---------|
| R1 | `[script.py]` | [...] | [...] |

## Subject inclusion / exclusion
- **N included:** [N] / **N excluded:** [N]
- **Exclusion criteria:**
  - [criterion 1] → excludes [count]
  - [criterion 2] → excludes [count]
- **Pre-registered or post-hoc?** [pre / post]

## Canonical hyperparameters
[Block of locked-in numbers — the result of any parameter sweep / sensitivity analysis. Cite the file or sweep that justifies each.]

## Linked topic files
- `pipeline-status.md` — per-stage detail + commit hashes for validated runs
- `bugs-log.md` — non-obvious bugs and their fixes (one per entry)
- `subject-exclusions.md` — full exclusion table with reasons

## Drifts flagged at last sync
- [...]
