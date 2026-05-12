[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | 日本語 | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Claude Code 向けマルチエージェントオーケストレーション ── リサーチ専用版。学習コストゼロ。**

_リサーチ用ツールを学ぶ必要はありません。OMCR をそのまま使ってください。_

OMCR は [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) のリサーチ特化版です。OMC が汎用コードワークを実行エンジン(`ralph`、`team`、`autopilot`、`ultraqa`、`ultrawork`)でオーケストレーションするのに対し、OMCR は *リサーチワークフロー* を **6 つのドメイン特化エンジン** ── `/iterate-revision`、`/literature-sweep`、`/respond-reviewer`、`/figure-bake`、`/outline-expand`、そして自律モードの `/supervisor-drive` ── でオーケストレーションします。どちらも単独で使えますし、組み合わせも可能です:OMCR エンジンは OMC の汎用ループ内で動作し、リトライ(`/ralph`)、並列実行(`/team`、`/ultrawork`)、多戦略探索(`/ultraqa`)、予算追跡型の自律ドライブ(`/autopilot`)に組み込めます。task → tool マトリクスは [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md)、実践レシピは [`wiki/With-OMC.md`](wiki/With-OMC.md) を参照してください。

6 名のリサーチチームエージェント + 6 つのオーケストレーションエンジン + 4 つの setup/workflow コマンド + 14 のスキル(1 つの primitive + 13 の backing surface) + 4 つの軽量フック。エンジンのフルウォークスルー: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **ステータス: v0.1。** Breaking change が入る可能性があります。フィードバックや PR を歓迎します。

> **完全なドキュメント:** [`wiki/Home.md`](wiki/Home.md)

## Install

**推奨 ── Claude Code marketplace 経由**(1 行ずつ、スラッシュコマンドを 1 つずつ入力):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**代替 ── 手動 checkout**(プラグインマネージャなし):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

その後 Claude Code を開いて `/plugin` を実行してロード。ロード後(いずれの経路でも):
- 6 つのエージェントが `@`-mention ピッカーに表示
- 10 個のスラッシュコマンドがピッカーに表示: `/omcr-setup`、`/start-research`、`/todofig`、`/sync`(setup/workflow) + `/iterate-revision`、`/literature-sweep`、`/respond-reviewer`、`/figure-bake`、`/outline-expand`、`/supervisor-drive`(オーケストレーションエンジン)
- 14 のスキルが呼び出し可能になる(7 つの setup/workflow + 1 つの primitive `orchestrate` + 6 つの engine skill)
- 4 つの hook がセッション開始時に登録(PII ガード、MEMORY 自動ロード、引用警告、setup nudge)

**ファイル単位の cherry-pick**(プラグインマネージャなし ── 特定プロジェクトに agents だけコピー):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

この方式ではコマンド、スキル、フックがスキップされます。完全な機能セットが必要ならプラグインインストールを推奨。

## Quick start

インストール後、リサーチプロジェクトを開いて順に実行:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** はインストール型 ── リサーチ内容についての質問はありません。インフラだけを敷きます: `CLAUDE.md` 内の空の `## Project context` / `## Research stack` / `## Language preference` ブロック、6 つのエージェントの `.claude/agent-memory/<agent>/MEMORY.md`(canonical テンプレート)、literature-curator 用の空の `paper/references.bib` + `./references.csv`、そしてキュレーションされた `.claude/settings.json` パーミッション allowlist(read-only git、ファイル検索、LaTeX build、引用 API、figure crop ── Python 分析は opt-in、git write とファイル削除は手動のまま)。

**`/start-research`** はインタビューです。プレースホルダの埋め方をガイドします:
- **Project context**(作業タイトル、分野、ターゲット venue、中心仮説、リサーチトピック、データセット、ナラティブ)
- **Research stack**(deck/outline パス、figure 数、BibTeX + summary-table パス、任意の CrossRef メール)
- **Preset overlay**(任意 ── `examples/neuro-fmri/` など ── canonical テンプレートとバイト一致のエージェント `MEMORY.md` のみ置き換え)
- **Manuscript scaffold**(`manuscript-scaffold` スキルに委譲: LaTeX skeleton + ジャーナルテンプレート lookup + 任意の Overleaf clone)

`/omcr-setup` の前に `/start-research` を実行すると、先に `/omcr-setup` を実行するか確認します。スキップした科学フィールドは `[TBD: <短いメモ>]` として保存され ── 決して捏造しません ── `@supervisor` が後でフォローアップできるようにします。

両方をスキップした場合、SessionStart の `setup-nudge` フックが毎セッション 1 行リマインダーを出します。`CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` で抑制可能。

両方が終わったら、本物の会話を始めましょう:

```
@supervisor where are we?
```

フルウォークスルー: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI レベルの科学的ビジョン保持者 + プロジェクトオーケストレーター。中心仮説を保持し、サブエージェントに委譲。 |
| `@analysis-implementer` | パイプライン、統計分析、ML/シミュレーションモデルを実装。デフォルトは分野ニュートラル。 |
| `@paper-writer` | high-impact ジャーナル級の文章品質で manuscript セクションを起草。 |
| `@figure-descriptor` | 実装可能な brief 形式で図を設計 ── 画像生成はしない。 |
| `@reviewer` | ターゲット venue 水準での投稿前敵対的レビュー。 |
| `@literature-curator` | プロジェクトの BibTeX と literature summary table を同期保持。`[CITE: ...]` プレースホルダを解決し、`verify-citation` スキルで引用を検証、捏造は一切しない。 |

### 4 slash commands (プロジェクトの CLAUDE.md でパラメータ化)

| Command | What it does |
|---|---|
| `/omcr-setup` | インストール型: 空の `CLAUDE.md` マーカーブロック、`.claude/agent-memory/` ディレクトリ、空の `references.bib`/`references.csv`、そしてキュレーションされた `.claude/settings.json` パーミッション allowlist を敷きます。**リサーチ内容については質問しません。** プロジェクトごとに 1 回実行。 |
| `/start-research [minimal\|neuro-fmri]` | インタビュー型: `CLAUDE.md` プレースホルダ(作業タイトル、仮説、ターゲット venue、データセット、ナラティブ)を埋め、オプションでエージェントメモリにプリセットを適用、LaTeX manuscript ディレクトリを scaffold(`manuscript-scaffold` スキル経由、ジャーナルテンプレート + 任意の Overleaf clone)。`/omcr-setup` 未実行なら先に実行するか確認。 |
| `/todofig [Fig N]` | 取得済み figure deck と outline を比較 → P0/P1/P2 優先度の TODO。 |
| `/sync` | 現在の状態(deck)と目標(outline)を調停、エージェントメモリを更新、任意で crop 済み figure をターゲット文書に埋め込み。状態スナップショット(TODO ではない)。 |

### 14 skills

4 つの setup/workflow スラッシュコマンドは thin dispatcher ── 各自 `$ARGUMENTS` を同名スキルに転送します。`cropfig`、`verify-citation`、`manuscript-scaffold` は単独でも呼び出し可能。**さらに** 1 つの primitive(`orchestrate` ── 内部用、4 つの phase で構成) + 6 つのオーケストレーションコマンドを支える engine skill。フルウォークスルーは [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)。下表は 7 つの setup/workflow スキルをカバーします。

| Skill | What it does |
|---|---|
| `omcr-setup` | `/omcr-setup` を支える。インストール型: `CLAUDE.md` マーカーブロック、agent-memory ディレクトリ、bibliography ファイル、キュレーション済みパーミッション allowlist を scaffold。 |
| `start-research` | `/start-research` を支える。インタビュー型の初回プロジェクト初期化: scaffold 済み `CLAUDE.md` プレースホルダを埋め、オプションでプリセットを適用、manuscript scaffold は `manuscript-scaffold` に委譲。 |
| `sync` | `/sync` を支える。現状(取得済み figure deck)と outline を調停、事実的な drift でエージェントメモリを更新、状態スナップショットのみ(TODO は出さない)。 |
| `todofig` | `/todofig` を支える。取得済み figure deck と outline を比較し、gap に対する P0/P1/P2 優先度 TODO を生成。 |
| `cropfig` | `.key`/`.pptx` deck から manuscript + outline アーティファクトまでの 3 段階パイプライン: スライド単位のベクター PDF(crop 済み、manuscript-grade) + outline-grade PNG。直接呼び出すか他コマンドが呼び出す。スラッシュなし。 |
| `verify-citation` | CrossRef/OpenAlex による存在 + メタデータチェック。`@literature-curator` が追加するすべてのエントリを gate し、検証結果をプロジェクトの summary table に書き込む。 |
| `manuscript-scaffold` | バンドル済み LaTeX skeleton をユーザの manuscript ディレクトリにコピー、オプションでバンドル済み registry からジャーナル固有の `\documentclass` を適用、オプションで Overleaf プロジェクトを clone(token は tracked ファイルに永続化しない)、デフォルトブランチに commit、push 前に確認。`/start-research` の phase 6 から呼び出される。単独呼び出しも可。 |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | PII(デフォルト: メール / SSN / subject ID。設定可能)を含む書き込みをブロック。 |
| `memory-load` | `SessionStart` | `.claude/agent-memory/*/MEMORY.md` をセッションコンテキストに自動注入。 |
| `citation-warn` | `PostToolUse:Write\|Edit` | manuscript markdown に引用なしの段落があればヒューリスティックに警告(ブロックしない)。 |
| `setup-nudge` | `SessionStart` | CLAUDE.md に `## Project context` または `## Research stack` ブロックがない場合、`/omcr-setup` → `/start-research` を実行するよう一行で nudge(ブロックしない)。 |

## Documentation

- **[Wiki home](wiki/Home.md)** — ナビゲーションハブ
- **[Getting Started](wiki/Getting-Started.md)** — インストール + 初回セッション
- **[Configuration](wiki/Configuration.md)** — Research stack ブロック、環境変数、PII パターン
- **[Standalone Usage](wiki/Standalone-Usage.md)** — OMCR 単独使用、フルウォークスルー
- **[With OMC](wiki/With-OMC.md)** — フルスタック: OMCR + OMC companion インストール
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — リファレンス
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 個の OMC MCP ツールをリサーチ段階にマップ
- **[Specializing](wiki/Specializing.md)** — 分野特化プリセットを書く

## Specializing for your field

コアのエージェントとコマンドは分野ニュートラルです。ドメイン色(例: 神経科学方法論、wet-lab 慣習、ML 評価のイディオム)を加えるには、`examples/<field>/` のプリセットをオーバーレイします。現在提供されているもの:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — 汎用 neuro-fMRI 特化。neuro 風味の `analysis-implementer` 本文(preprocessing / parcellation / connectivity / ISC / spin tests) + 6 つのエージェント全部に対する redacted MEMORY.md スケルトンを提供。

クイックオーバーレイ:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

自分のプリセットを書くには: [`wiki/Specializing.md`](wiki/Specializing.md) を参照。新規プリセットを追加する PR(`examples/wet-lab/`、`examples/ml-research/`、`examples/astronomy/`、…)を歓迎します。

## OMC companion (recommended)

OMCR は [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) を依存ではなく *companion* として扱います。OMC を併設すると、以下のコンポーネントがリサーチワークフローに自然にフィットします。プロジェクトに関係するものだけ選んでください ── 全部使う必要はありません。

| Component | Why for research |
|---|---|
| `@scientist` agent | 統計的厳密性の徹底(信頼区間 / p 値 / 効果量 / `[LIMITATION]` マーカー)。`@analysis-implementer` の companion。 |
| `@document-specialist` agent | OMC の Context Hub(キャッシュ済み fetch、構造化メモ)を背景にした重量級 literature リサーチ。survey 規模の deep dive が必要なときに `@literature-curator` と併用。OMCR の curator は per-claim 引用解決と BibTeX/summary-table 管理を自前で行う。 |
| `@verifier` agent | エビデンスベースの完了確認 ── 新規テスト出力なしの "should work" を拒否。 |
| `@tracer` agent + `/oh-my-claudecode:trace` | エビデンス駆動の競合仮説ランキング + disconfirmation。methods/results 検証にマップ。 |
| `@writer` agent | ラボプロトコル、methods appendix、再現性ガイド向けの技術文書ライター。 |
| `@test-engineer` agent | 分析スクリプトのエッジケースカバレッジに対する TDD 規律。 |
| `@git-master` agent | atomic-commit 規律 ── 独立に revert 可能な分析ステップ。 |
| `/oh-my-claudecode:autoresearch` skill | per-iteration JSON + decision log を備えた bounded evaluator-driven 反復ループ。 |
| `/oh-my-claudecode:deep-interview` skill | 曖昧なリサーチ目標を検証可能な仮説へソクラテス的に明確化。 |
| OMC オーケストレーションスキル (`ralph`、`team`、`autopilot`、`ralplan`、`ultraqa`、`autoresearch`、…) | 分析 run、文献スキャン、必達 revision のためのマルチイテレーション / 並列 / コンセンサスオーケストレータ。5 つの実践レシピは [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) を参照。 |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP ツール | Literature wiki / 仮説 register / 実験 run レジストリ / stateful Python REPL。 |

OMC は Claude Code marketplace 経由、または `npm i -g oh-my-claude-sisyphus` で併設できます。完全なマッピング: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- エージェント、スキル、コマンドのファイル名は **kebab-case**
- すべてのエージェント / スキル / コマンドに **YAML frontmatter** 必須(`name`、`description`、任意の `model` / `color` / `memory`)
- `agents/`、`commands/`、`skills/`、`templates/`、`hooks/`、およびトップレベル文書での **PII 禁止** ── 機関名、指導教員名、実 subject ID、メール、ターゲットジャーナル名、絶対パス。ドメイン特化コンテンツは `examples/<field>/` 配下のみ。
- すべてのエージェントで **English-first** な言語ディレクティブ(CLAUDE.md でオーバーライドするパターン)

完全な contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT ── [LICENSE](LICENSE) を参照。
