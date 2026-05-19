[English](README.md) | [한국어](README.ko.md) | 中文 | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-codex-research

**面向 Codex 的多代理编排 —— 科研专用版。零学习曲线。**

_别再去学科研工具了。直接用 OMXR。_

OMXR 是面向 Codex 的科研工作空间:6 名 agent —— `@supervisor`、`@analysis-implementer`、`@paper-writer`、`@figure-descriptor`、`@reviewer`、`@literature-curator` —— 与你一起完成假设、分析、写作、figure、引用、review。需要 hands-off 时,6 个编排引擎自动化常见循环。如果在上层还需要通用编排(重试、并行、预算追踪),就与 [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) 组合使用。

6 名研究团队 agent + 6 个编排引擎 + 4 个 setup/workflow 命令 + 14 个技能 + 4 个轻量级 hook。

> **状态:v0.1。** 可能出现 breaking change。欢迎反馈与 PR。

> **完整文档:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: 安装**

**如果你是第一次安装 OMXR** —— marketplace 流程(推荐)。这些是 Codex 的斜杠命令,**一次输入一个**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-codex-research
```

然后:

```
/plugin install oh-my-codex-research
```

**如果你想用手动 checkout**(不用插件管理器):

```bash
git clone https://github.com/youngeun1209/oh-my-codex-research \
  ~/.codex/plugins/oh-my-codex-research
```

**如果 OMXR 已经安装,想更新** —— 按顺序一次一条运行下面两条:

```
/plugin marketplace update omxr
```

然后:

```
/plugin update oh-my-codex-research
```

第一条只刷新 marketplace 元数据,第二条才真正拉取新的插件文件。OMXR 跟随 `main` 分支,所以每个新 commit 都被视作新版本。项目状态(AGENTS.md、agent 内存、设置)不会被改动 —— 不需要重新跑 Step 2。

**Step 2: 设置**

**每个项目只需要做一次。** 在你的研究项目的 Codex 会话中,**一次输入一个**斜杠命令:

```
$omxr-setup
```

然后:

```
$start-research
```

`$omxr-setup` 铺基础设施 —— `AGENTS.md` 中的空 `## Project context` / `## Research stack` / `## Language preference` 块、6 个 agent 的 `.omx/omxr/agent-memory/<agent>/MEMORY.md`、literature-curator 用的空 `paper/references.bib` + `./references.csv`,以及精选的 hook/check readiness。**不询问你的研究。**

`$start-research` 是访谈。它引导你填充上述占位符:
- **Project context**(工作标题、领域、目标 venue、中心假设、研究主题、数据集、叙述主线)
- **Research stack**(deck/outline 路径、figure 数量、BibTeX + summary-table 路径、可选 CrossRef 邮箱)
- **Preset overlay**(可选 —— `examples/neuro-fmri/` 等 —— 仅替换仍与 canonical 模板字节相同的 agent `MEMORY.md`)
- **Manuscript scaffold**(委派给 `manuscript-scaffold` 技能:LaTeX skeleton + journal 模板查询 + 可选 Overleaf clone)

如果在 `$omxr-setup` 之前运行 `$start-research`,它会询问是否先运行 `$omxr-setup`。被跳过的科学字段以 `[TBD: <简短备注>]` 保存 —— 从不捏造 —— 这样 `@supervisor` 知道需要后续跟进。两者都跳过时,SessionStart 的 `setup-nudge` hook 每个会话都会打印一行提醒(可通过 `CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1` 关闭)。

**Step 3: 开始工作**

```
@supervisor where are we?
```

完整教程: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI 级别的科学愿景守护者兼项目编排者。拥有中心假设,委派给子代理。 |
| `@analysis-implementer` | 实现数据管道、统计分析、ML/模拟模型。默认领域中立。 |
| `@paper-writer` | 以高影响力期刊水准撰写 manuscript 章节。 |
| `@figure-descriptor` | 以可实现的 brief 形式设计图表 —— 不生成图像。 |
| `@reviewer` | 按目标 venue 水准做提交前的对抗性审稿。 |
| `@literature-curator` | 同步维护项目的 BibTeX 与 literature summary table。解析 `[CITE: ...]` 占位符,通过 `verify-citation` 技能验证引用,绝不捏造。 |

### 4 workflow commands (通过项目 AGENTS.md 参数化)

| Command | What it does |
|---|---|
| `$omxr-setup` | 安装式:铺设空的 `AGENTS.md` 标记块、`.omx/omxr/agent-memory/` 目录、空的 `references.bib`/`references.csv`,以及精心挑选的 hook/check readiness。**不询问你的研究内容。** 每个项目运行一次即可。 |
| `$start-research [minimal\|neuro-fmri]` | 访谈式:填充 `AGENTS.md` 占位符(工作标题、假设、目标 venue、数据集、叙述主线),可选地为代理记忆应用预设,scaffold LaTeX manuscript 目录(通过 `manuscript-scaffold` 技能,可选 journal template + Overleaf clone)。如未运行 `$omxr-setup`,会询问是否先运行。 |
| `$todofig [Fig N]` | 对比已捕获的 figure deck 与 outline → 优先级 P0/P1/P2 的 TODO。 |
| `$sync` | 调和当前状态(deck)与目标(outline),刷新代理记忆,可选地将 cropped figure 嵌入目标文档。是状态快照而非 TODO。 |

### 14 skills

4 个 setup/workflow 斜杠命令是 thin dispatcher —— 各自把 `$ARGUMENTS` 转发给同名技能。`cropfig`、`verify-citation`、`manuscript-scaffold` 也可独立调用。**额外加上** 1 个 primitive(`orchestrate` —— 内部使用,由 4 个 phase 组合而成) + 6 个支撑 6 个编排命令的引擎技能;完整教程见 [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)。下表覆盖 7 个 setup/workflow 技能。

| Skill | What it does |
|---|---|
| `omxr-setup` | 支撑 `$omxr-setup`。安装式:scaffold `AGENTS.md` 标记块、agent-memory 目录、bibliography 文件、精选权限 hook/check readiness。 |
| `start-research` | 支撑 `$start-research`。访谈式首项目初始化:填充 scaffold 后的 `AGENTS.md` 占位符,可选应用预设覆盖,manuscript scaffold 委派给 `manuscript-scaffold`。 |
| `sync` | 支撑 `$sync`。调和当前状态(捕获的 figure deck)与 outline;以事实性 drift 刷新代理记忆;仅状态快照(不生成 TODO)。 |
| `todofig` | 支撑 `$todofig`。对比已捕获的 figure deck 与 outline;生成 gap 的 P0/P1/P2 优先级 TODO。 |
| `cropfig` | 从 `.key`/`.pptx` deck 到 manuscript + outline artifact 的三步管道:逐 slide 矢量 PDF(cropped、manuscript-grade) + outline-grade PNG。直接调用或由其他命令调用;无斜杠。 |
| `verify-citation` | 通过 CrossRef/OpenAlex 做存在性 + 元数据检查。把守 `@literature-curator` 添加的每一条,把验证结论写入项目 summary table。 |
| `manuscript-scaffold` | 把内置的 LaTeX skeleton 复制到用户 manuscript 目录,可选地从内置 registry 应用 journal 专属 `\documentclass`,可选地 clone Overleaf 项目(token 不会 persist 到 tracked 文件),在默认分支 commit,push 前会询问。被 `$start-research` 的 phase 6 调用;也可独立调用。 |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | 阻止包含 PII(默认:邮箱 / SSN / subject ID;可配置)的写入。 |
| `memory-load` | `SessionStart` | 自动将 `.omx/omxr/agent-memory/*/MEMORY.md` 注入会话上下文。 |
| `citation-warn` | `PostToolUse:Write\|Edit` | manuscript markdown 中存在无引用段落时给出启发式警告(不阻断)。 |
| `setup-nudge` | `SessionStart` | 若 AGENTS.md 缺少 `## Project context` 或 `## Research stack` 块,给出运行 `$omxr-setup` 然后 `$start-research` 的一行提示(不阻断)。 |

## Documentation

- **[Wiki home](wiki/Home.md)** — 导航中心
- **[Getting Started](wiki/Getting-Started.md)** — 安装 + 首次会话
- **[Configuration](wiki/Configuration.md)** — Research stack 块、环境变量、PII 模式
- **[Standalone Usage](wiki/Standalone-Usage.md)** — 单独使用 OMXR 的完整教程
- **[With OMX](wiki/With-OMX.md)** — 全栈:OMXR + OMX companion 安装
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — 参考
- **[OMX Tool Reference](wiki/OMX-Tool-Reference.md)** — 将 47 个 OMX MCP 工具映射到研究阶段
- **[Specializing](wiki/Specializing.md)** — 编写领域专属预设

## Specializing for your field

核心代理与命令是领域中立的。如需添加领域风味(例如神经科学方法学、wet-lab 习惯、ML 评估惯用法),从 `examples/<field>/` 覆盖一个预设。当前提供:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** —— 通用 neuro-fMRI 特化。提供带 neuro 风味的 `analysis-implementer` 主体(preprocessing / parcellation / connectivity / ISC / spin tests) + 6 个代理全部的 redacted MEMORY.md 骨架。

快速覆盖:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .omx/omxr/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .omx/omxr/agent-memory/$agent/MEMORY.md
done
```

编写自己的预设:见 [`wiki/Specializing.md`](wiki/Specializing.md)。欢迎提 PR 添加新预设(`examples/wet-lab/`、`examples/ml-research/`、`examples/astronomy/`、…)。

## OMX companion (recommended)

OMXR 把 [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex) 视作 *companion*,而非依赖。同时安装 OMX 后,以下组件天然契合研究工作流。挑选与你项目相关的 —— 不必全用。

| Component | Why for research |
|---|---|
| `@scientist` agent | 统计严谨性执行者(置信区间 / p 值 / 效应量 / `[LIMITATION]` 标记)。`@analysis-implementer` 的 companion。 |
| `@document-specialist` agent | 由 OMX 的 Context Hub(缓存 fetch、结构化笔记)支撑的更重量级 literature 研究。当需要 survey 规模深挖时与 `@literature-curator` 配合;OMXR 的 curator 自身处理 per-claim 引用解析与 BibTeX/summary-table 管理。 |
| `@verifier` agent | 基于证据的完成检查 —— 拒绝没有新测试输出的 "should work" 声明。 |
| `@tracer` agent + `/oh-my-codex:trace` | 证据驱动的竞争假设排名 + disconfirmation。映射到 methods/results 验证。 |
| `@writer` agent | 用于实验室协议、methods appendix、可重复性指南的技术文档作者。 |
| `@test-engineer` agent | 针对分析脚本边界覆盖的 TDD 纪律。 |
| `@git-master` agent | atomic-commit 纪律 —— 可独立 revert 的分析步骤。 |
| `/oh-my-codex:autoresearch` skill | bounded evaluator-driven 迭代循环,带 per-iteration JSON + decision log。 |
| `/oh-my-codex:deep-interview` skill | 苏格拉底式将模糊研究目标澄清为可检验假设。 |
| OMX 编排技能 (`ralph`、`team`、`autopilot`、`ralplan`、`ultraqa`、`autoresearch`、…) | 面向分析 run、文献扫描、必须完成的 revision 的多迭代 / 并行 / 共识编排器。5 个实战配方见 [`wiki/With-OMX.md#recipes--pairing-omxr-with-omc`](wiki/With-OMX.md#recipes--pairing-omxr-with-omc)。 |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP 工具 | Literature wiki / 假设 register / 实验 run 注册表 / stateful Python REPL。 |

通过 Codex marketplace 同时安装 OMX,或 `npm i -g oh-my-codex`。完整映射: [`wiki/With-OMX.md`](wiki/With-OMX.md) + [`wiki/OMX-Tool-Reference.md`](wiki/OMX-Tool-Reference.md)

## Conventions (contributors)

- 代理、技能、命令的文件名采用 **kebab-case**
- 每个代理 / 技能 / 命令必须有 **YAML frontmatter**(`name`、`description`,可选 `model` / `color` / `memory`)
- 在 `agents/`、`commands/`、`skills/`、`templates/`、`hooks/`,以及顶层文档中 **禁止 PII** —— 机构名、导师名、真实 subject ID、邮箱、目标期刊名、绝对路径。领域专属内容仅放在 `examples/<field>/` 下。
- 所有代理默认 **English-first** 语言指令(通过 AGENTS.md 覆盖的模式)

完整 contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT —— 见 [LICENSE](LICENSE)。
