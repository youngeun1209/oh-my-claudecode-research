[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | Русский | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-codex-research

**Мультиагентная оркестрация для Codex — редакция для исследований. Нулевая кривая обучения.**

_Не изучайте инструменты для исследований. Просто используйте OMXR._

OMXR — это исследовательское рабочее пространство для Codex: шесть агентов — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — с которыми вы работаете бок о бок над гипотезой, анализом, написанием, figure, цитатами, ревью. Шесть оркестрационных движков автоматизируют типичные циклы, когда вы хотите hands-off. Комбинируйте с [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex), если сверху нужна универсальная оркестрация (ретраи, параллелизм, контроль бюджета).

Исследовательская команда из 6 агентов + 6 движков оркестрации + 4 setup/workflow команды + 14 скиллов + 4 лёгких хука.

> **Статус: v0.1.** Возможны breaking changes. Фидбек и PR-ы приветствуются.

> **Полная документация:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: Установка**

**Если устанавливаете OMXR в первый раз** — marketplace-поток (рекомендуется). Это слеш-команды Codex, вводите **по одной**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-codex-research
```

Затем:

```
/plugin install oh-my-codex-research
```

**Если предпочитаете ручной checkout** (без плагин-менеджера):

```bash
git clone https://github.com/youngeun1209/oh-my-codex-research \
  ~/.codex/plugins/oh-my-codex-research
```

**Если OMXR уже установлен и вы хотите его обновить** — запустите эти две слеш-команды по одной:

```
/plugin marketplace update omxr
```

Затем:

```
/plugin update oh-my-codex-research
```

Первая обновляет только метаданные маркетплейса; вторая уже подтягивает новые файлы плагина. OMXR следует за `main`, так что каждый новый коммит считается новой версией. Состояние вашего проекта (AGENTS.md, память агентов, настройки) не трогается — Step 2 запускать заново не нужно.

**Step 2: Настройка**

**Делается один раз на проект.** Внутри сессии Codex в вашем исследовательском проекте запускайте слеш-команды **по одной**:

```
$omxr-setup
```

Затем:

```
$start-research
```

`$omxr-setup` кладёт инфраструктуру — пустые блоки `## Project context` / `## Research stack` / `## Language preference` в `AGENTS.md`, `.omx/omxr/agent-memory/<agent>/MEMORY.md` для всех 6 агентов, пустые `paper/references.bib` + `./references.csv` для literature-curator, и hook/check readiness.**Никаких вопросов о вашем исследовании.**

`$start-research` — это интервью. Оно ведёт вас по заполнению этих плейсхолдеров:
- **Project context** (working title, область, целевой venue, центральная гипотеза, тема исследования, датасеты, нарративная линия)
- **Research stack** (пути deck/outline, число figure, пути BibTeX + summary-table, опциональный CrossRef email)
- **Preset overlay** (опционально — `examples/neuro-fmri/` и т. д. — заменяет только агентские `MEMORY.md`, ещё byte-identical с каноническим шаблоном)
- **Manuscript scaffold** (делегирует скиллу `manuscript-scaffold`: LaTeX skeleton + lookup шаблона журнала + опциональный Overleaf clone)

Если вы запустите `$start-research` до `$omxr-setup`, он предложит сначала запустить `$omxr-setup`. Пропущенные научные поля сохраняются как `[TBD: <короткая заметка>]` — никогда не выдумываются — чтобы `@supervisor` знал, что нужно follow-up. Если пропустить оба, хук `setup-nudge` на SessionStart печатает однострочное напоминание каждую сессию до инициализации (отключается через `CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Начать работу**

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

### 4 workflow commands (параметризуются через AGENTS.md вашего проекта)

| Command | What it does |
|---|---|
| `$omxr-setup` | Установочный режим: раскладывает пустые маркерные блоки в `AGENTS.md`, директории `.omx/omxr/agent-memory/`, пустые `references.bib`/`references.csv`, и hook/check readiness.**Не задаёт вопросов о вашем исследовании.** Запускайте один раз на проект. |
| `$start-research [minimal\|neuro-fmri]` | Интервью-режим: заполняет плейсхолдеры в `AGENTS.md` (working title, гипотеза, целевой venue, датасеты, нарративная линия), опционально применяет пресет к памяти агентов, scaffold LaTeX-директории manuscript (через скилл `manuscript-scaffold`, с шаблоном журнала + опциональным Overleaf clone). Если `$omxr-setup` ещё не выполнялся — предложит выполнить сначала. |
| `$todofig [Fig N]` | Сравнивает захваченный figure deck с outline → приоритизированный TODO P0/P1/P2. |
| `$sync` | Согласовывает текущее состояние (deck) с целью (outline), обновляет память агентов, опционально встраивает cropped figure в целевой документ. Снимок состояния, не TODO. |

### 14 skills

4 setup/workflow слеш-команды — это thin dispatcher: каждая форвардит `$ARGUMENTS` соответствующему скиллу. `cropfig`, `verify-citation`, `manuscript-scaffold` также вызываются самостоятельно. **Плюс** 1 primitive (`orchestrate` — внутренний, состоит из 4 фаз) + 6 engine-скиллов, backing 6 оркестрационных команд; полный гайд в [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Таблица ниже покрывает 7 setup/workflow скиллов.

| Skill | What it does |
|---|---|
| `omxr-setup` | Бэкает `$omxr-setup`. Установочный режим: scaffold маркерных блоков `AGENTS.md`, agent-memory директорий, файлов библиографии, hook/check readiness. |
| `start-research` | Бэкает `$start-research`. Интервью-режим инициализации первого проекта: заполняет уже scaffold-нутые плейсхолдеры `AGENTS.md`, опционально применяет preset overlay, делегирует manuscript scaffold в `manuscript-scaffold`. |
| `sync` | Бэкает `$sync`. Согласовывает текущее состояние (захваченный figure deck) с outline; обновляет память агентов фактическими дрифтами; только снимок состояния (без TODO). |
| `todofig` | Бэкает `$todofig`. Сравнивает захваченный figure deck с outline; выдаёт приоритизированный TODO P0/P1/P2 по gap-ам. |
| `cropfig` | Трёхшаговый пайплайн от `.key`/`.pptx` deck до артефактов manuscript + outline: per-slide векторные PDF (cropped, manuscript-grade) + outline-grade PNG. Вызывается напрямую или другими командами; без слеша. |
| `verify-citation` | Проверка существования + метаданных через CrossRef/OpenAlex. Гейтит каждую запись, которую добавляет `@literature-curator`, пишет вердикт верификации в summary table проекта. |
| `manuscript-scaffold` | Копирует встроенный LaTeX skeleton в директорию manuscript пользователя, опционально применяет journal-специфичный `\documentclass` из встроенного registry, опционально клонирует Overleaf проект (токен никогда не persist-ится в tracked файлы), коммитит в default branch, спрашивает перед push. Вызывается из `$start-research` фазы 6; также вызывается самостоятельно. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Блокирует запись с PII (по умолчанию: email / SSN / subject ID; конфигурируется). |
| `memory-load` | `SessionStart` | Авто-инжектит `.omx/omxr/agent-memory/*/MEMORY.md` в контекст сессии. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Эвристическое не-блокирующее предупреждение, когда в manuscript markdown есть абзацы без цитат. |
| `setup-nudge` | `SessionStart` | Не-блокирующее однострочное напоминание запустить `$omxr-setup`, затем `$start-research`, если в AGENTS.md нет блоков `## Project context` или `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — навигационный хаб
- **[Getting Started](wiki/Getting-Started.md)** — установка + первая сессия
- **[Configuration](wiki/Configuration.md)** — блок Research stack, env vars, PII-паттерны
- **[Standalone Usage](wiki/Standalone-Usage.md)** — использование OMXR в одиночку, полный гайд
- **[With OMX](wiki/With-OMX.md)** — full stack: установка OMXR + OMX companion
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — справочники
- **[OMX Tool Reference](wiki/OMX-Tool-Reference.md)** — 47 инструментов OMX MCP, замапленных на стадии исследования
- **[Specializing](wiki/Specializing.md)** — создание field-специфичного пресета

## Specializing for your field

Core-агенты и команды — domain-neutral. Для доменного оттенка (например, методология neuroscience, конвенции wet-lab, идиомы ML-оценки) накладывайте пресет из `examples/<field>/`. Сейчас доступно:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generic neuro-fMRI специализация. Предоставляет neuro-окрашенное тело `analysis-implementer` (preprocessing / parcellation / connectivity / ISC / spin tests) + redacted MEMORY.md скелеты для всех 6 агентов.

Быстрый overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .omx/omxr/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .omx/omxr/agent-memory/$agent/MEMORY.md
done
```

Чтобы написать свой пресет: см. [`wiki/Specializing.md`](wiki/Specializing.md). PR с новыми пресетами (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) приветствуются.

## OMX companion (recommended)

OMXR относится к [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex) как к *companion*, а не зависимости. С установленным рядом OMX следующие компоненты естественно вписываются в исследовательские воркфлоу. Выбирайте релевантные вашему проекту — необязательно использовать всё.

| Component | Why for research |
|---|---|
| `@scientist` agent | Энфорсер статистической строгости (CI / p-values / effect sizes / маркеры `[LIMITATION]`). Companion для `@analysis-implementer`. |
| `@document-specialist` agent | Тяжёлое literature-исследование на бэке Context Hub OMX (кешированные fetches, структурированные заметки). Используйте вместе с `@literature-curator`, когда нужен deep dive масштаба survey; curator OMXR сам обслуживает per-claim citation resolution и ведение BibTeX/summary-table. |
| `@verifier` agent | Evidence-based проверки завершённости — отвергает заявления "should work" без свежего test output. |
| `@tracer` agent + `/oh-my-codex:trace` | Evidence-driven ранжирование конкурирующих гипотез + disconfirmation. Мапится на валидацию methods/results. |
| `@writer` agent | Технический документатор для лабораторных протоколов, methods appendix, гайдов воспроизводимости. |
| `@test-engineer` agent | TDD-дисциплина для покрытия edge case в скриптах анализа. |
| `@git-master` agent | Atomic-commit дисциплина — независимо ревертируемые шаги анализа. |
| `/oh-my-codex:autoresearch` skill | Bounded evaluator-driven итерационный цикл с per-iteration JSON + decision log. |
| `/oh-my-codex:deep-interview` skill | Сократическое прояснение размытых целей исследования до проверяемых гипотез. |
| OMX orchestration скиллы (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Мульти-итерационные / параллельные / консенсусные оркестраторы для analysis runs, literature scans, must-finish ревизий. См. [`wiki/With-OMX.md#recipes--pairing-omxr-with-omc`](wiki/With-OMX.md#recipes--pairing-omxr-with-omc) — 5 реальных рецептов. |
| MCP-инструменты `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Literature wiki / реестр гипотез / реестр experiment runs / stateful Python REPL. |

Установите OMX рядом через Codex marketplace или `npm i -g oh-my-codex`. Полная мапа: [`wiki/With-OMX.md`](wiki/With-OMX.md) + [`wiki/OMX-Tool-Reference.md`](wiki/OMX-Tool-Reference.md)

## Conventions (contributors)

- Имена файлов в **kebab-case** для агентов, скиллов, команд
- **YAML frontmatter** обязателен на каждом агенте / скилле / команде (`name`, `description`, опциональные `model` / `color` / `memory`)
- **Никакого PII** в `agents/`, `commands/`, `skills/`, `templates/`, `hooks/` или top-level документах — учреждения, научные руководители, реальные subject ID, email-ы, имена целевых журналов, абсолютные пути. Доменно-специфичный контент живёт только под `examples/<field>/`.
- **English-first** языковая директива на всех агентах (паттерн override-in-AGENTS.md)

Полный contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — см. [LICENSE](LICENSE).
