[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | Español | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Orquestación multi-agente para Claude Code — edición para investigación. Curva de aprendizaje cero.**

_No aprendas herramientas de investigación. Simplemente usa OMCR._

OMCR es un espacio de trabajo de investigación para Claude Code: seis agentes — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — con los que trabajas codo a codo en hipótesis, análisis, escritura, figuras, citas, revisión. Seis motores de orquestación automatizan los bucles habituales cuando lo quieres hands-off. Combínalo con [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) cuando necesites orquestación genérica por encima (reintentos, paralelismo, presupuestos).

Un equipo de investigación de 6 agentes + 6 motores de orquestación + 4 comandos setup/workflow + 14 skills + 4 hooks ligeros.

> **Estado: v0.1.** Es probable que haya cambios incompatibles. Se aceptan comentarios y PRs.

> **Documentación completa:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: Instalación**

**Si instalas OMCR por primera vez** — flujo marketplace (recomendado). Son comandos slash de Claude Code, introdúcelos **uno a uno**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

Después:

```
/plugin install oh-my-claudecode-research
```

**Si prefieres checkout manual** (sin gestor de plugins):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**Si OMCR ya está instalado y quieres actualizarlo** — ejecuta estos dos comandos slash, uno a uno:

```
/plugin marketplace update omcr
```

Después:

```
/plugin update oh-my-claudecode-research
```

El primero refresca los metadatos del marketplace; el segundo realmente trae los nuevos archivos del plugin. OMCR sigue `main`, así que cada commit nuevo se trata como una versión nueva. El estado de tu proyecto (CLAUDE.md, memoria de agentes, settings) no se toca — no hace falta volver a ejecutar Step 2.

**Step 2: Configuración**

**Solo se necesita una vez por proyecto.** Dentro de una sesión de Claude Code en tu proyecto de investigación, ejecuta los comandos slash **uno a uno**:

```
/omcr-setup
```

Después:

```
/start-research
```

`/omcr-setup` planta la infraestructura — bloques vacíos `## Project context` / `## Research stack` / `## Language preference` en `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` para los 6 agentes, `paper/references.bib` + `./references.csv` vacíos para el literature-curator, y una allowlist de permisos curada en `.claude/settings.json`. **No pregunta nada sobre tu investigación.**

`/start-research` es la entrevista. Te guía rellenando esos placeholders:
- **Project context** (working title, campo, venue objetivo, hipótesis central, tema de investigación, datasets, hilo narrativo)
- **Research stack** (rutas de deck/outline, número de figuras, rutas de BibTeX + summary-table, email CrossRef opcional)
- **Preset overlay** (opcional — `examples/neuro-fmri/` etc. — solo reemplaza archivos `MEMORY.md` de agentes que siguen siendo byte-identical al template canónico)
- **Manuscript scaffold** (delega a la skill `manuscript-scaffold`: LaTeX skeleton + lookup de plantilla de revista + Overleaf clone opcional)

Si ejecutas `/start-research` antes que `/omcr-setup`, ofrece ejecutar `/omcr-setup` primero. Los campos científicos saltados se guardan como `[TBD: <nota breve>]` — nunca se inventan — para que `@supervisor` sepa hacer seguimiento. Si saltas ambos, el hook `setup-nudge` de SessionStart imprime un recordatorio de una línea en cada sesión hasta que inicialices (suprime con `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Empezar a trabajar**

```
@supervisor where are we?
```

Recorrido completo: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Guardián de la visión científica a nivel de PI + orquestador del proyecto. Posee la hipótesis central; delega en subagentes. |
| `@analysis-implementer` | Implementa pipelines, análisis estadísticos, modelos de ML/simulación. Por defecto neutral al campo. |
| `@paper-writer` | Redacta secciones del manuscrito con calidad de prosa de revista de alto impacto. |
| `@figure-descriptor` | Diseña figuras como briefs listos para implementar — no genera imágenes. |
| `@reviewer` | Revisión adversaria pre-envío al nivel del venue objetivo. |
| `@literature-curator` | Mantiene en lockstep el BibTeX y la summary table de literatura del proyecto. Resuelve placeholders `[CITE: ...]`, verifica citas vía la skill `verify-citation`, nunca fabrica. |

### 4 slash commands (parametrizados vía el CLAUDE.md de tu proyecto)

| Command | What it does |
|---|---|
| `/omcr-setup` | Estilo instalación: planta bloques marcadores vacíos en `CLAUDE.md`, directorios `.claude/agent-memory/`, `references.bib`/`references.csv` vacíos, y una allowlist de permisos curada en `.claude/settings.json`. **No hace preguntas sobre tu investigación.** Ejecutar una vez por proyecto. |
| `/start-research [minimal\|neuro-fmri]` | Estilo entrevista: rellena los placeholders de `CLAUDE.md` (working title, hipótesis, venue objetivo, datasets, hilo narrativo), aplica opcionalmente un preset a la memoria de los agentes, hace scaffold del directorio LaTeX del manuscrito (vía la skill `manuscript-scaffold`, con plantilla de revista + Overleaf clone opcional). Ofrece ejecutar `/omcr-setup` primero si no se ha hecho. |
| `/todofig [Fig N]` | Compara un deck de figuras capturado contra un outline → TODO priorizado P0/P1/P2. |
| `/sync` | Reconcilia el estado actual (deck) con el objetivo (outline), refresca la memoria de los agentes, opcionalmente embebe figuras croppeadas en un documento objetivo. Snapshot de estado, no un TODO. |

### 14 skills

Los 4 comandos slash setup/workflow son thin dispatchers — cada uno reenvía `$ARGUMENTS` a una skill correspondiente. `cropfig`, `verify-citation`, `manuscript-scaffold` son invocables de forma independiente. **Además** 1 primitive (`orchestrate` — interna, compone vía 4 fases) + 6 engine skills que respaldan los 6 comandos de orquestación; recorrido completo en [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). La tabla debajo cubre las 7 skills setup/workflow.

| Skill | What it does |
|---|---|
| `omcr-setup` | Respalda `/omcr-setup`. Estilo instalación: scaffold de bloques marcadores en `CLAUDE.md`, directorios agent-memory, archivos de bibliografía, allowlist de permisos curada. |
| `start-research` | Respalda `/start-research`. Init estilo entrevista del primer proyecto: rellena los placeholders de `CLAUDE.md` ya scaffoldeados, aplica opcionalmente una preset overlay, delega el manuscript scaffold a `manuscript-scaffold`. |
| `sync` | Respalda `/sync`. Reconcilia el estado actual (deck de figuras capturado) con el outline; refresca la memoria de los agentes con drifts factuales; sólo snapshot de estado (sin TODO). |
| `todofig` | Respalda `/todofig`. Compara un deck de figuras capturado con el outline; produce un TODO priorizado P0/P1/P2 de los gaps. |
| `cropfig` | Pipeline de tres pasos desde un deck `.key`/`.pptx` a artefactos de manuscrito + outline: PDFs vectoriales por slide (croppeados, calidad manuscrito) + PNGs calidad outline. Invocada directamente o por otros comandos; sin slash. |
| `verify-citation` | Comprobación de existencia + metadatos vía CrossRef/OpenAlex. Hace de gate para cada entrada que `@literature-curator` añade, escribe el veredicto de verificación en la summary table del proyecto. |
| `manuscript-scaffold` | Copia el LaTeX skeleton incluido al directorio de manuscrito del usuario, aplica opcionalmente un `\documentclass` específico de revista desde el registry incluido, opcionalmente clona un proyecto Overleaf (el token nunca se persiste en archivos tracked), commit en la rama por defecto, pregunta antes de push. Llamado por `/start-research` fase 6; también invocable de forma independiente. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Bloquea writes que contengan PII (por defecto: emails / SSN / IDs de sujeto; configurable). |
| `memory-load` | `SessionStart` | Auto-inyecta `.claude/agent-memory/*/MEMORY.md` en el contexto de la sesión. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Aviso heurístico no bloqueante cuando el markdown del manuscrito tiene párrafos sin citar. |
| `setup-nudge` | `SessionStart` | Empujón de una línea no bloqueante para ejecutar `/omcr-setup` y después `/start-research` si CLAUDE.md no tiene los bloques `## Project context` o `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — hub de navegación
- **[Getting Started](wiki/Getting-Started.md)** — instalar + primera sesión
- **[Configuration](wiki/Configuration.md)** — bloque Research stack, variables de entorno, patrones PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — usar OMCR solo, recorrido completo
- **[With OMC](wiki/With-OMC.md)** — full stack: instalación OMCR + OMC companion
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — referencias
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 herramientas OMC MCP mapeadas a etapas de investigación
- **[Specializing](wiki/Specializing.md)** — escribir un preset específico de campo

## Specializing for your field

Los agentes y comandos del core son neutrales al campo. Para sabor específico del dominio (p. ej. metodología de neurociencia, convenciones wet-lab, idioms de evaluación ML), superpón un preset de `examples/<field>/`. Actualmente disponibles:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — especialización genérica neuro-fMRI. Proporciona un cuerpo `analysis-implementer` con sabor neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + esqueletos MEMORY.md redacted para los 6 agentes.

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

Para escribir tu propio preset: ver [`wiki/Specializing.md`](wiki/Specializing.md). Se aceptan PRs añadiendo nuevos presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …).

## OMC companion (recommended)

OMCR trata a [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) como *companion*, no como dependencia. Con OMC instalado al lado, los siguientes componentes encajan de forma natural en flujos de investigación. Elige los relevantes para tu proyecto — no hace falta usarlos todos.

| Component | Why for research |
|---|---|
| `@scientist` agent | Aplicador de rigor estadístico (CIs / p-values / tamaños de efecto / marcadores `[LIMITATION]`). Companion de `@analysis-implementer`. |
| `@document-specialist` agent | Investigación literaria más pesada respaldada por el Context Hub de OMC (fetches cacheados, notas estructuradas). Úsalo junto a `@literature-curator` cuando se necesite un deep dive a escala de survey; el curator de OMCR maneja por su cuenta la resolución de citas por claim y la gestión BibTeX/summary-table. |
| `@verifier` agent | Comprobación de completitud basada en evidencia — rechaza afirmaciones "should work" sin output de test fresco. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Ranking de hipótesis competidoras basado en evidencia con disconfirmation. Mapea a validación de methods/results. |
| `@writer` agent | Escritor de documentación técnica para protocolos de laboratorio, anexos de methods, guías de reproducibilidad. |
| `@test-engineer` agent | Disciplina TDD para cobertura de edge cases en scripts de análisis. |
| `@git-master` agent | Disciplina atomic-commit — pasos de análisis independientemente revertibles. |
| `/oh-my-claudecode:autoresearch` skill | Bucle de iteración bounded evaluator-driven con JSON + decision log por iteración. |
| `/oh-my-claudecode:deep-interview` skill | Clarificación socrática de objetivos de investigación vagos en hipótesis testables. |
| Skills de orquestación OMC (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Orquestadores multi-iteración / paralelo / consenso para corridas de análisis, escaneos de literatura, revisiones must-finish. Ver [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) para 5 recetas reales. |
| Herramientas MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki de literatura / registro de hipótesis / registro de runs experimentales / REPL Python con estado. |

Instala OMC al lado vía el Claude Code marketplace, o `npm i -g oh-my-claude-sisyphus`. Mapeo completo: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Nombres de archivo en **kebab-case** para agentes, skills, comandos
- **YAML frontmatter** obligatorio en cada agente / skill / comando (`name`, `description`, opcionalmente `model` / `color` / `memory`)
- **Sin PII** en `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, ni en docs de nivel superior — instituciones, asesores, IDs reales de sujeto, emails, nombres de revistas objetivo, paths absolutos. El contenido específico del dominio vive solo bajo `examples/<field>/`.
- Directiva de idioma **English-first** en todos los agentes (patrón de override en CLAUDE.md)

Contract completo: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — ver [LICENSE](LICENSE).
