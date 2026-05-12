[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | Русский | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Мультиагентная оркестрация для Claude Code — редакция для исследований. Нулевая кривая обучения.**

_Не изучайте инструменты для исследований. Просто используйте OMCR._

OMCR — это исследовательский собрат [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode). Если OMC оркестрирует общую работу с кодом через исполняющие движки (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`), то OMCR оркестрирует *исследовательский воркфлоу* через **6 доменно-специфичных движков** — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` и автономный `/supervisor-drive`. Используйте по отдельности или комбинируйте: движки OMCR работают внутри универсальных циклов OMC для ретраев (`/ralph`), параллелизма (`/team`, `/ultrawork`), многострагической разведки (`/ultraqa`) или прогонов с бюджетом (`/autopilot`). Полная матрица task → tool в [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md), реальные рецепты в [`wiki/With-OMC.md`](wiki/With-OMC.md).

Исследовательская команда из 6 агентов + 6 движков оркестрации + 4 setup/workflow команды + 14 скиллов (1 primitive + 13 backing surfaces) + 4 лёгких хука. Полный гайд по движкам: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **Статус: v0.1.** Возможны breaking changes. Фидбек и PR-ы приветствуются.

> **Полная документация:** [`wiki/Home.md`](wiki/Home.md)

## Install

**Рекомендуется — поток Claude Code marketplace** (по одной слеш-команде на строку, вводите по одной):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Альтернатива — ручной checkout** (без плагин-менеджера):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Затем откройте Claude Code и выполните `/plugin` для загрузки. После загрузки (любым путём):
- 6 агентов появляются в picker-е `@`-mention
- 10 слеш-команд появляются в picker-е: `/omcr-setup`, `/start-research`, `/todofig`, `/sync` (setup/workflow) + `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` (оркестрационные движки)
- 14 скиллов становятся вызываемыми (7 setup/workflow + 1 primitive `orchestrate` + 6 engine-скиллов)
- 4 хука регистрируются на старте сессии (PII-страж, авто-загрузка MEMORY, предупреждение о цитатах, setup nudge)

**Cherry-pick по файлам** (без плагин-менеджера — копируем агентов в конкретный проект):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Этот способ пропускает команды, скиллы и хуки. Для полного функционала используйте установку плагина.

## Quick start

После установки откройте исследовательский проект и запустите по порядку:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** — установочный режим, никаких вопросов о вашем исследовании. Просто кладёт инфраструктуру: пустые блоки `## Project context` / `## Research stack` / `## Language preference` в `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` для всех 6 агентов (канонический шаблон), пустые `paper/references.bib` + `./references.csv` для literature-curator, и курированный allowlist прав в `.claude/settings.json` (read-only git, поиск файлов, LaTeX build, citation API, figure crop — opt-in для Python-анализа; git write и удаление файлов остаются ручными).

**`/start-research`** — это интервью. Оно ведёт вас по заполнению этих плейсхолдеров:
- **Project context** (working title, область, целевой venue, центральная гипотеза, тема исследования, датасеты, нарративная линия)
- **Research stack** (пути deck/outline, число figure, пути BibTeX + summary-table, опциональный CrossRef email)
- **Preset overlay** (опционально — `examples/neuro-fmri/` и т. д. — заменяет только агентские `MEMORY.md`, ещё byte-identical с каноническим шаблоном)
- **Manuscript scaffold** (делегирует скиллу `manuscript-scaffold`: LaTeX skeleton + lookup шаблона журнала + опциональный Overleaf clone)

Если вы запустите `/start-research` до `/omcr-setup`, он предложит сначала запустить `/omcr-setup`. Пропущенные научные поля сохраняются как `[TBD: <короткая заметка>]` — никогда не выдумываются — чтобы `@supervisor` знал, что нужно follow-up.

Если пропустить оба, хук `setup-nudge` на SessionStart печатает однострочное напоминание каждую сессию до инициализации. Отключается через `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

После обоих — начинайте реальный разговор:

```
@supervisor where are we?
```

Полный гайд: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Хранитель научного видения уровня PI + оркестратор проекта. Владеет центральной гипотезой; делегирует субагентам. |
| `@analysis-implementer` | Реализует пайплайны, статистический анализ, ML/симуляционные модели. По умолчанию domain-neutral. |
| `@paper-writer` | Пишет секции manuscript на уровне прозы high-impact журнала. |
| `@figure-descriptor` | Проектирует figure как готовые к реализации briefs — изображения не генерирует. |
| `@reviewer` | Соревновательная пред-сабмиссионная ревью на уровне целевого venue. |
| `@literature-curator` | Синхронно владеет BibTeX и literature summary table проекта. Разрешает плейсхолдеры `[CITE: ...]`, верифицирует цитирования через скилл `verify-citation`, никогда не фабрикует. |

### 4 slash commands (параметризуются через CLAUDE.md вашего проекта)

| Command | What it does |
|---|---|
| `/omcr-setup` | Установочный режим: раскладывает пустые маркерные блоки в `CLAUDE.md`, директории `.claude/agent-memory/`, пустые `references.bib`/`references.csv`, и курированный allowlist прав в `.claude/settings.json`. **Не задаёт вопросов о вашем исследовании.** Запускайте один раз на проект. |
| `/start-research [minimal\|neuro-fmri]` | Интервью-режим: заполняет плейсхолдеры в `CLAUDE.md` (working title, гипотеза, целевой venue, датасеты, нарративная линия), опционально применяет пресет к памяти агентов, scaffold LaTeX-директории manuscript (через скилл `manuscript-scaffold`, с шаблоном журнала + опциональным Overleaf clone). Если `/omcr-setup` ещё не выполнялся — предложит выполнить сначала. |
| `/todofig [Fig N]` | Сравнивает захваченный figure deck с outline → приоритизированный TODO P0/P1/P2. |
| `/sync` | Согласовывает текущее состояние (deck) с целью (outline), обновляет память агентов, опционально встраивает cropped figure в целевой документ. Снимок состояния, не TODO. |

### 14 skills

4 setup/workflow слеш-команды — это thin dispatcher: каждая форвардит `$ARGUMENTS` соответствующему скиллу. `cropfig`, `verify-citation`, `manuscript-scaffold` также вызываются самостоятельно. **Плюс** 1 primitive (`orchestrate` — внутренний, состоит из 4 фаз) + 6 engine-скиллов, backing 6 оркестрационных команд; полный гайд в [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Таблица ниже покрывает 7 setup/workflow скиллов.

| Skill | What it does |
|---|---|
| `omcr-setup` | Бэкает `/omcr-setup`. Установочный режим: scaffold маркерных блоков `CLAUDE.md`, agent-memory директорий, файлов библиографии, курированного allowlist прав. |
| `start-research` | Бэкает `/start-research`. Интервью-режим инициализации первого проекта: заполняет уже scaffold-нутые плейсхолдеры `CLAUDE.md`, опционально применяет preset overlay, делегирует manuscript scaffold в `manuscript-scaffold`. |
| `sync` | Бэкает `/sync`. Согласовывает текущее состояние (захваченный figure deck) с outline; обновляет память агентов фактическими дрифтами; только снимок состояния (без TODO). |
| `todofig` | Бэкает `/todofig`. Сравнивает захваченный figure deck с outline; выдаёт приоритизированный TODO P0/P1/P2 по gap-ам. |
| `cropfig` | Трёхшаговый пайплайн от `.key`/`.pptx` deck до артефактов manuscript + outline: per-slide векторные PDF (cropped, manuscript-grade) + outline-grade PNG. Вызывается напрямую или другими командами; без слеша. |
| `verify-citation` | Проверка существования + метаданных через CrossRef/OpenAlex. Гейтит каждую запись, которую добавляет `@literature-curator`, пишет вердикт верификации в summary table проекта. |
| `manuscript-scaffold` | Копирует встроенный LaTeX skeleton в директорию manuscript пользователя, опционально применяет journal-специфичный `\documentclass` из встроенного registry, опционально клонирует Overleaf проект (токен никогда не persist-ится в tracked файлы), коммитит в default branch, спрашивает перед push. Вызывается из `/start-research` фазы 6; также вызывается самостоятельно. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Блокирует запись с PII (по умолчанию: email / SSN / subject ID; конфигурируется). |
| `memory-load` | `SessionStart` | Авто-инжектит `.claude/agent-memory/*/MEMORY.md` в контекст сессии. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Эвристическое не-блокирующее предупреждение, когда в manuscript markdown есть абзацы без цитат. |
| `setup-nudge` | `SessionStart` | Не-блокирующее однострочное напоминание запустить `/omcr-setup`, затем `/start-research`, если в CLAUDE.md нет блоков `## Project context` или `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — навигационный хаб
- **[Getting Started](wiki/Getting-Started.md)** — установка + первая сессия
- **[Configuration](wiki/Configuration.md)** — блок Research stack, env vars, PII-паттерны
- **[Standalone Usage](wiki/Standalone-Usage.md)** — использование OMCR в одиночку, полный гайд
- **[With OMC](wiki/With-OMC.md)** — full stack: установка OMCR + OMC companion
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — справочники
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 инструментов OMC MCP, замапленных на стадии исследования
- **[Specializing](wiki/Specializing.md)** — создание field-специфичного пресета

## Specializing for your field

Core-агенты и команды — domain-neutral. Для доменного оттенка (например, методология neuroscience, конвенции wet-lab, идиомы ML-оценки) накладывайте пресет из `examples/<field>/`. Сейчас доступно:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generic neuro-fMRI специализация. Предоставляет neuro-окрашенное тело `analysis-implementer` (preprocessing / parcellation / connectivity / ISC / spin tests) + redacted MEMORY.md скелеты для всех 6 агентов.

Быстрый overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Чтобы написать свой пресет: см. [`wiki/Specializing.md`](wiki/Specializing.md). PR с новыми пресетами (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) приветствуются.

## OMC companion (recommended)

OMCR относится к [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) как к *companion*, а не зависимости. С установленным рядом OMC следующие компоненты естественно вписываются в исследовательские воркфлоу. Выбирайте релевантные вашему проекту — необязательно использовать всё.

| Component | Why for research |
|---|---|
| `@scientist` agent | Энфорсер статистической строгости (CI / p-values / effect sizes / маркеры `[LIMITATION]`). Companion для `@analysis-implementer`. |
| `@document-specialist` agent | Тяжёлое literature-исследование на бэке Context Hub OMC (кешированные fetches, структурированные заметки). Используйте вместе с `@literature-curator`, когда нужен deep dive масштаба survey; curator OMCR сам обслуживает per-claim citation resolution и ведение BibTeX/summary-table. |
| `@verifier` agent | Evidence-based проверки завершённости — отвергает заявления "should work" без свежего test output. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Evidence-driven ранжирование конкурирующих гипотез + disconfirmation. Мапится на валидацию methods/results. |
| `@writer` agent | Технический документатор для лабораторных протоколов, methods appendix, гайдов воспроизводимости. |
| `@test-engineer` agent | TDD-дисциплина для покрытия edge case в скриптах анализа. |
| `@git-master` agent | Atomic-commit дисциплина — независимо ревертируемые шаги анализа. |
| `/oh-my-claudecode:autoresearch` skill | Bounded evaluator-driven итерационный цикл с per-iteration JSON + decision log. |
| `/oh-my-claudecode:deep-interview` skill | Сократическое прояснение размытых целей исследования до проверяемых гипотез. |
| OMC orchestration скиллы (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Мульти-итерационные / параллельные / консенсусные оркестраторы для analysis runs, literature scans, must-finish ревизий. См. [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) — 5 реальных рецептов. |
| MCP-инструменты `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Literature wiki / реестр гипотез / реестр experiment runs / stateful Python REPL. |

Установите OMC рядом через Claude Code marketplace или `npm i -g oh-my-claude-sisyphus`. Полная мапа: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Имена файлов в **kebab-case** для агентов, скиллов, команд
- **YAML frontmatter** обязателен на каждом агенте / скилле / команде (`name`, `description`, опциональные `model` / `color` / `memory`)
- **Никакого PII** в `agents/`, `commands/`, `skills/`, `templates/`, `hooks/` или top-level документах — учреждения, научные руководители, реальные subject ID, email-ы, имена целевых журналов, абсолютные пути. Доменно-специфичный контент живёт только под `examples/<field>/`.
- **English-first** языковая директива на всех агентах (паттерн override-in-CLAUDE.md)

Полный contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — см. [LICENSE](LICENSE).
