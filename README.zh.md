[English](README.md) | [한국어](README.ko.md) | 中文 | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**面向 Claude Code 的多代理编排 —— 科研专用版。零学习曲线。**

_别再去学科研工具了。直接用 OMCR。_

OMCR 是 [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) 的科研定制版。OMC 用执行引擎(`ralph`、`team`、`autopilot`、`ultraqa`、`ultrawork`)编排通用代码工作,而 OMCR 用 **6 个领域专用引擎** —— `/iterate-revision`、`/literature-sweep`、`/respond-reviewer`、`/figure-bake`、`/outline-expand`,以及自主模式的 `/supervisor-drive` —— 来编排*科研工作流*。两者可单独使用,也可组合:OMCR 引擎可在 OMC 的通用循环中运行,用于重试(`/ralph`)、并行(`/team`、`/ultrawork`)、多策略探索(`/ultraqa`)或预算追踪式自主驱动(`/autopilot`)。完整的 task → tool 矩阵见 [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md),实战配方见 [`wiki/With-OMC.md`](wiki/With-OMC.md)。

6 名研究团队代理 + 6 个编排引擎 + 4 个 setup/workflow 命令 + 14 个技能(1 个 primitive + 13 个 backing surface) + 4 个轻量级 hook。引擎完整教程: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **状态:v0.1。** 可能出现 breaking change。欢迎反馈与 PR。

> **完整文档:** [`wiki/Home.md`](wiki/Home.md)

## Install

**推荐 —— Claude Code marketplace 流程**(每行一个斜杠命令,逐条输入):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**替代 —— 手动 checkout**(不用插件管理器):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

之后打开 Claude Code,运行 `/plugin` 加载。加载后(任一路径):
- 6 个代理出现在 `@`-mention 选择器中
- 10 个斜杠命令出现在选择器中:`/omcr-setup`、`/start-research`、`/todofig`、`/sync`(setup/workflow) + `/iterate-revision`、`/literature-sweep`、`/respond-reviewer`、`/figure-bake`、`/outline-expand`、`/supervisor-drive`(编排引擎)
- 14 个技能可被调用(7 个 setup/workflow + 1 个 primitive `orchestrate` + 6 个引擎技能)
- 4 个 hook 在会话启动时注册(PII 守护、MEMORY 自动加载、引用警告、setup nudge)

**按文件 cherry-pick**(无插件管理器 —— 仅复制 agents 到特定项目):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

这种方式跳过命令、技能和 hook。需要完整功能请用插件安装。

## Quick start

安装后,打开一个研究项目,按顺序运行:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** 是安装式 —— 不询问你的研究。只铺基础设施:`CLAUDE.md` 中的空 `## Project context` / `## Research stack` / `## Language preference` 块、6 个代理的 `.claude/agent-memory/<agent>/MEMORY.md`(canonical 模板)、literature-curator 用的空 `paper/references.bib` + `./references.csv`,以及精选的 `.claude/settings.json` 权限 allowlist(只读 git、文件搜索、LaTeX build、引用 API、figure crop —— Python 分析为 opt-in;git write 和文件删除保持手动)。

**`/start-research`** 是访谈。它引导你填充上述占位符:
- **Project context**(工作标题、领域、目标 venue、中心假设、研究主题、数据集、叙述主线)
- **Research stack**(deck/outline 路径、figure 数量、BibTeX + summary-table 路径、可选 CrossRef 邮箱)
- **Preset overlay**(可选 —— `examples/neuro-fmri/` 等 —— 仅替换仍与 canonical 模板字节相同的代理 `MEMORY.md`)
- **Manuscript scaffold**(委派给 `manuscript-scaffold` 技能:LaTeX skeleton + journal 模板查询 + 可选 Overleaf clone)

如果在 `/omcr-setup` 之前运行 `/start-research`,它会询问是否先运行 `/omcr-setup`。被跳过的科学字段以 `[TBD: <简短备注>]` 保存 —— 从不捏造 —— 这样 `@supervisor` 知道需要后续跟进。

两者都跳过时,SessionStart 的 `setup-nudge` hook 每个会话都会打印一行提醒。可通过 `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` 关闭。

两者都完成后,开始真正的对话:

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

### 4 slash commands (通过项目 CLAUDE.md 参数化)

| Command | What it does |
|---|---|
| `/omcr-setup` | 安装式:铺设空的 `CLAUDE.md` 标记块、`.claude/agent-memory/` 目录、空的 `references.bib`/`references.csv`,以及精心挑选的 `.claude/settings.json` 权限 allowlist。**不询问你的研究内容。** 每个项目运行一次即可。 |
| `/start-research [minimal\|neuro-fmri]` | 访谈式:填充 `CLAUDE.md` 占位符(工作标题、假设、目标 venue、数据集、叙述主线),可选地为代理记忆应用预设,scaffold LaTeX manuscript 目录(通过 `manuscript-scaffold` 技能,可选 journal template + Overleaf clone)。如未运行 `/omcr-setup`,会询问是否先运行。 |
| `/todofig [Fig N]` | 对比已捕获的 figure deck 与 outline → 优先级 P0/P1/P2 的 TODO。 |
| `/sync` | 调和当前状态(deck)与目标(outline),刷新代理记忆,可选地将 cropped figure 嵌入目标文档。是状态快照而非 TODO。 |

### 14 skills

4 个 setup/workflow 斜杠命令是 thin dispatcher —— 各自把 `$ARGUMENTS` 转发给同名技能。`cropfig`、`verify-citation`、`manuscript-scaffold` 也可独立调用。**额外加上** 1 个 primitive(`orchestrate` —— 内部使用,由 4 个 phase 组合而成) + 6 个支撑 6 个编排命令的引擎技能;完整教程见 [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)。下表覆盖 7 个 setup/workflow 技能。

| Skill | What it does |
|---|---|
| `omcr-setup` | 支撑 `/omcr-setup`。安装式:scaffold `CLAUDE.md` 标记块、agent-memory 目录、bibliography 文件、精选权限 allowlist。 |
| `start-research` | 支撑 `/start-research`。访谈式首项目初始化:填充 scaffold 后的 `CLAUDE.md` 占位符,可选应用预设覆盖,manuscript scaffold 委派给 `manuscript-scaffold`。 |
| `sync` | 支撑 `/sync`。调和当前状态(捕获的 figure deck)与 outline;以事实性 drift 刷新代理记忆;仅状态快照(不生成 TODO)。 |
| `todofig` | 支撑 `/todofig`。对比已捕获的 figure deck 与 outline;生成 gap 的 P0/P1/P2 优先级 TODO。 |
| `cropfig` | 从 `.key`/`.pptx` deck 到 manuscript + outline artifact 的三步管道:逐 slide 矢量 PDF(cropped、manuscript-grade) + outline-grade PNG。直接调用或由其他命令调用;无斜杠。 |
| `verify-citation` | 通过 CrossRef/OpenAlex 做存在性 + 元数据检查。把守 `@literature-curator` 添加的每一条,把验证结论写入项目 summary table。 |
| `manuscript-scaffold` | 把内置的 LaTeX skeleton 复制到用户 manuscript 目录,可选地从内置 registry 应用 journal 专属 `\documentclass`,可选地 clone Overleaf 项目(token 不会 persist 到 tracked 文件),在默认分支 commit,push 前会询问。被 `/start-research` 的 phase 6 调用;也可独立调用。 |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | 阻止包含 PII(默认:邮箱 / SSN / subject ID;可配置)的写入。 |
| `memory-load` | `SessionStart` | 自动将 `.claude/agent-memory/*/MEMORY.md` 注入会话上下文。 |
| `citation-warn` | `PostToolUse:Write\|Edit` | manuscript markdown 中存在无引用段落时给出启发式警告(不阻断)。 |
| `setup-nudge` | `SessionStart` | 若 CLAUDE.md 缺少 `## Project context` 或 `## Research stack` 块,给出运行 `/omcr-setup` 然后 `/start-research` 的一行提示(不阻断)。 |

## Documentation

- **[Wiki home](wiki/Home.md)** — 导航中心
- **[Getting Started](wiki/Getting-Started.md)** — 安装 + 首次会话
- **[Configuration](wiki/Configuration.md)** — Research stack 块、环境变量、PII 模式
- **[Standalone Usage](wiki/Standalone-Usage.md)** — 单独使用 OMCR 的完整教程
- **[With OMC](wiki/With-OMC.md)** — 全栈:OMCR + OMC companion 安装
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — 参考
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 将 47 个 OMC MCP 工具映射到研究阶段
- **[Specializing](wiki/Specializing.md)** — 编写领域专属预设

## Specializing for your field

核心代理与命令是领域中立的。如需添加领域风味(例如神经科学方法学、wet-lab 习惯、ML 评估惯用法),从 `examples/<field>/` 覆盖一个预设。当前提供:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** —— 通用 neuro-fMRI 特化。提供带 neuro 风味的 `analysis-implementer` 主体(preprocessing / parcellation / connectivity / ISC / spin tests) + 6 个代理全部的 redacted MEMORY.md 骨架。

快速覆盖:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

编写自己的预设:见 [`wiki/Specializing.md`](wiki/Specializing.md)。欢迎提 PR 添加新预设(`examples/wet-lab/`、`examples/ml-research/`、`examples/astronomy/`、…)。

## OMC companion (recommended)

OMCR 把 [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) 视作 *companion*,而非依赖。同时安装 OMC 后,以下组件天然契合研究工作流。挑选与你项目相关的 —— 不必全用。

| Component | Why for research |
|---|---|
| `@scientist` agent | 统计严谨性执行者(置信区间 / p 值 / 效应量 / `[LIMITATION]` 标记)。`@analysis-implementer` 的 companion。 |
| `@document-specialist` agent | 由 OMC 的 Context Hub(缓存 fetch、结构化笔记)支撑的更重量级 literature 研究。当需要 survey 规模深挖时与 `@literature-curator` 配合;OMCR 的 curator 自身处理 per-claim 引用解析与 BibTeX/summary-table 管理。 |
| `@verifier` agent | 基于证据的完成检查 —— 拒绝没有新测试输出的 "should work" 声明。 |
| `@tracer` agent + `/oh-my-claudecode:trace` | 证据驱动的竞争假设排名 + disconfirmation。映射到 methods/results 验证。 |
| `@writer` agent | 用于实验室协议、methods appendix、可重复性指南的技术文档作者。 |
| `@test-engineer` agent | 针对分析脚本边界覆盖的 TDD 纪律。 |
| `@git-master` agent | atomic-commit 纪律 —— 可独立 revert 的分析步骤。 |
| `/oh-my-claudecode:autoresearch` skill | bounded evaluator-driven 迭代循环,带 per-iteration JSON + decision log。 |
| `/oh-my-claudecode:deep-interview` skill | 苏格拉底式将模糊研究目标澄清为可检验假设。 |
| OMC 编排技能 (`ralph`、`team`、`autopilot`、`ralplan`、`ultraqa`、`autoresearch`、…) | 面向分析 run、文献扫描、必须完成的 revision 的多迭代 / 并行 / 共识编排器。5 个实战配方见 [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc)。 |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP 工具 | Literature wiki / 假设 register / 实验 run 注册表 / stateful Python REPL。 |

通过 Claude Code marketplace 同时安装 OMC,或 `npm i -g oh-my-claude-sisyphus`。完整映射: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- 代理、技能、命令的文件名采用 **kebab-case**
- 每个代理 / 技能 / 命令必须有 **YAML frontmatter**(`name`、`description`,可选 `model` / `color` / `memory`)
- 在 `agents/`、`commands/`、`skills/`、`templates/`、`hooks/`,以及顶层文档中 **禁止 PII** —— 机构名、导师名、真实 subject ID、邮箱、目标期刊名、绝对路径。领域专属内容仅放在 `examples/<field>/` 下。
- 所有代理默认 **English-first** 语言指令(通过 CLAUDE.md 覆盖的模式)

完整 contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT —— 见 [LICENSE](LICENSE)。
