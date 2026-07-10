[English](README.md) | 한국어 | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Claude Code를 위한 멀티 에이전트 오케스트레이션 — 연구 전용. 학습 곡선 제로.**

_연구 도구를 따로 배우지 마세요. 그냥 OMCR을 쓰세요._

OMCR은 Claude Code를 위한 연구 워크스페이스입니다: 6명의 에이전트 — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — 와 함께 가설, 분석, 글쓰기, 그림, 인용, 리뷰를 진행합니다. 직접 손대고 싶지 않을 때는 6개의 오케스트레이션 엔진이 흔한 루프를 자동화해줍니다. 위에 범용 오케스트레이션(재시도, 병렬 실행, 예산 추적)이 더 필요하면 [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)와 조합하세요.

6명의 연구팀 에이전트 + 6개의 오케스트레이션 엔진 + 7개의 셋업/워크플로/유틸리티 커맨드 + 18개의 스킬 + 4개의 경량 훅.

> **상태: v0.1.** Breaking change가 자주 있을 수 있습니다. 피드백과 PR 환영합니다.

> **전체 문서:** [`wiki/Home.md`](wiki/Home.md)

> **Claude Code 대신 Codex CLI를 쓰시나요?** Codex 포팅은 [oh-my-codex-research](https://github.com/youngeun1209/oh-my-codex-research) (OMXR)에 있습니다 — 동일한 6 에이전트 연구팀을 OpenAI Codex CLI로 옮긴 버전입니다.

## Quick start

**Step 1: 설치**

**OMCR을 처음 설치한다면** — 마켓플레이스 플로우 (권장). Claude Code 슬래시 커맨드이니까 **한 번에 하나씩** 입력하세요:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

그다음:

```
/plugin install oh-my-claudecode-research
```

**수동 checkout을 선호한다면** (플러그인 매니저 없이):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**OMCR이 이미 설치돼 있고 업데이트하려면** — 아래 두 슬래시 커맨드를 한 번에 하나씩 실행하세요:

```
/plugin marketplace update omcr
```

그다음:

```
/plugin update oh-my-claudecode-research
```

첫 번째는 마켓플레이스 메타데이터만 새로고침하고, 두 번째가 실제로 새 플러그인 파일을 받아옵니다. OMCR은 `main` 브랜치를 따라가니까 새 commit마다 새 버전으로 취급됩니다. 사용자 프로젝트 상태(CLAUDE.md, 에이전트 메모리, 세팅)는 그대로 유지됩니다 — Step 2를 다시 실행할 필요 없음.

**Step 2: 셋업**

**프로젝트당 한 번만 실행하면 됩니다.** 연구 프로젝트의 Claude Code 세션 안에서 슬래시 커맨드를 **한 번에 하나씩** 실행하세요:

```
/omcr-setup
```

그다음:

```
/start-research
```

`/omcr-setup`은 인프라를 깔아둡니다 — `CLAUDE.md`의 비어 있는 `## Project context` / `## Research stack` / `## Language preference` 블록, 6명의 에이전트 모두에 대한 `.claude/agent-memory/<agent>/MEMORY.md`, literature-curator를 위한 빈 `paper/references.bib` + `./references.csv`, 그리고 큐레이션된 `.claude/settings.json` 권한 allowlist. **연구 내용에 대한 질문은 없습니다.**

`/start-research`는 인터뷰입니다. placeholder들을 채우는 과정을 안내합니다:
- **Project context** (working title, 분야, target venue, 중심 가설, 연구 주제, 데이터셋, narrative spine)
- **Research stack** (덱/outline 경로, figure 개수, BibTeX + summary-table 경로, 선택적 CrossRef 이메일)
- **Preset overlay** (선택 — `examples/neuro-fmri/` 등 — canonical 템플릿과 byte-identical인 에이전트 `MEMORY.md`만 교체)
- **Manuscript scaffold** (`manuscript-scaffold` 스킬에 위임: LaTeX skeleton + 저널 템플릿 lookup + 선택적 Overleaf clone)

`/omcr-setup` 전에 `/start-research`를 돌리면, 먼저 `/omcr-setup`을 돌릴지 물어봅니다. 건너뛴 과학 분야 필드는 `[TBD: <짧은 메모>]`로 저장됩니다 — 절대 지어내지 않음 — 그래서 `@supervisor`가 나중에 follow-up할 수 있게 합니다. 둘 다 건너뛰면, SessionStart `setup-nudge` 훅이 매 세션마다 한 줄짜리 reminder를 출력합니다 (`CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`로 끌 수 있음).

**Step 3: 작업 시작**

```
@supervisor where are we?
```

전체 워크스루: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI 레벨의 과학적 비전 keeper이자 프로젝트 오케스트레이터. 중심 가설을 owns하고, 서브에이전트에게 위임. |
| `@analysis-implementer` | 파이프라인, 통계 분석, ML/시뮬레이션 모델을 구현. 기본은 분야 중립. |
| `@paper-writer` | high-impact 저널 수준의 prose 품질로 manuscript 섹션을 작성. |
| `@figure-descriptor` | 구현 가능한 brief 형태로 figure를 설계 — 이미지 생성은 하지 않음. |
| `@reviewer` | 타깃 venue 수준의 적대적 사전 리뷰. |
| `@literature-curator` | 프로젝트의 BibTeX과 literature summary table을 lockstep으로 owns. `[CITE: ...]` placeholder를 해결하고, `verify-citation` 스킬로 인용을 검증하며, 절대로 fabricate하지 않음. |

### 7 slash commands (프로젝트의 CLAUDE.md로 파라미터화)

| Command | What it does |
|---|---|
| `/omcr-setup` | 설치형: 비어 있는 `CLAUDE.md` 마커 블록, `.claude/agent-memory/` 디렉터리, 비어 있는 `references.bib`/`references.csv`, 그리고 큐레이션된 `.claude/settings.json` 권한 allowlist를 깔아둠. **연구 내용에 대한 질문 없음.** 프로젝트당 한 번만 실행. |
| `/start-research [minimal\|neuro-fmri]` | 인터뷰형: `CLAUDE.md` placeholder를 채움(working title, 가설, target venue, 데이터셋, narrative spine), 선택적으로 에이전트 메모리에 프리셋 적용, LaTeX manuscript 디렉터리를 scaffold(`manuscript-scaffold` 스킬을 통해, 저널 템플릿 + 선택적 Overleaf clone 포함). `/omcr-setup`이 안 돌았으면 먼저 돌릴지 물어봄. |
| `/todofig [Fig N]` | 캡쳐된 figure 덱과 outline을 비교 → P0/P1/P2 우선순위 TODO. |
| `/sync` | 현재 상태(덱)와 목표(outline)를 reconcile, 에이전트 메모리 갱신, 선택적으로 cropped figure를 타깃 문서에 embed. 상태 스냅샷이지 TODO가 아님. |
| `/session-start [light\|full]` | 읽기 전용 orientation — 프로젝트 corpus(CLAUDE.md, outline, MEMORY, wiki 랜딩 페이지)를 읽고 요약 + 있는 그대로의 상태 스냅샷을 리포트. 부작용 없음; light/full 모드. |
| `/save-session-log [slug]` | 현재 세션의 날짜별 기록(요청, 작업 내용, 건드린 파일, 결정 사항, 다음 단계)을 session-logs 디렉터리에 충실하게 기록한 뒤, 확정된 지식을 wiki에 정밀하게 distill. |
| `/update-version [@new files]` | outline이나 figure 덱이 버전업(v4→v5)되면, 새 파일명을 모든 live 참조에 전파; 오래된 archive는 삭제 여부를 물어봄(confirm-gated). 기존 값은 `## Research stack`에서 읽어옴. |

### 18 skills

7개의 셋업/워크플로/유틸리티 슬래시 커맨드는 thin dispatcher — 각자 `$ARGUMENTS`를 매칭되는 스킬로 forward합니다. `cropfig`, `verify-citation`, `manuscript-scaffold`, `paper-ingest`는 standalone으로도 호출 가능. **추가로** 1개 primitive(`orchestrate` — 내부용, 4개 phase로 composes) + 6개의 오케스트레이션 커맨드를 backing하는 엔진 스킬; 전체 워크스루는 [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). 아래 표는 11개의 셋업/워크플로/유틸리티 스킬을 다룹니다.

| Skill | What it does |
|---|---|
| `omcr-setup` | `/omcr-setup`을 backing. 설치형: `CLAUDE.md` 마커 블록, agent-memory 디렉터리, bibliography 파일, 큐레이션된 권한 allowlist를 scaffold. |
| `start-research` | `/start-research`를 backing. 인터뷰형 첫 프로젝트 init: scaffold된 `CLAUDE.md` placeholder를 채우고, 선택적으로 프리셋 오버레이를 적용, manuscript scaffold는 `manuscript-scaffold`에 위임. |
| `sync` | `/sync`를 backing. 현재 상태(캡쳐된 figure 덱)와 outline을 reconcile; 사실적 drift로 에이전트 메모리 갱신; 상태 스냅샷만(TODO 없음). |
| `todofig` | `/todofig`를 backing. 캡쳐된 figure 덱과 outline을 비교; gap에 대한 P0/P1/P2 우선순위 TODO 생성. |
| `cropfig` | `.key`/`.pptx` 덱에서 manuscript + outline artifact까지의 3단계 파이프라인: 슬라이드별 벡터 PDF(cropped, manuscript-grade) + outline 등급 PNG. 직접 호출하거나 다른 커맨드가 호출; 슬래시 없음. |
| `verify-citation` | CrossRef/OpenAlex로 존재 + 메타데이터 확인. `@literature-curator`가 추가하는 모든 항목을 gate하고, 검증 결과를 프로젝트 summary table에 기록. |
| `manuscript-scaffold` | 번들된 LaTeX skeleton을 사용자의 manuscript 디렉터리로 복사하고, 선택적으로 번들된 registry에서 저널별 `\documentclass`를 적용, 선택적으로 Overleaf 프로젝트를 clone(토큰은 추적 파일에 persist하지 않음), 기본 브랜치에 commit, push 전에 확인. `/start-research` phase 6에서 호출됨; standalone으로도 호출 가능. |
| `paper-ingest` | 읽은 논문(PDF / DOI / URL)을 2개 폴더짜리 **reading library**로 ingest — 프로젝트 중립적인 요약 + cropped main figure + `index.csv` row, 이어서 relevance-gated된 project-usage 노트. `verify-citation` + `cropfig`를 재사용. manuscript BibTeX과는 별개. Standalone. [Reading-Library](wiki/Reading-Library.md) 참조. |
| `session-start` | `/session-start`를 backing. 읽기 전용 프로젝트 orientation(corpus 읽기 + 상태 리포트; light/full 모드). |
| `save-session-log` | `/save-session-log`를 backing. 날짜별 세션 기록 + 확정된 지식의 정밀한 wiki-distill. |
| `update-version` | `/update-version`를 backing. outline/덱 버전업을 모든 live 포인터에 전파; 과거 기록은 그대로 고정. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | PII(기본값: 이메일 / SSN / subject ID; 설정 가능)를 포함하는 write를 차단. |
| `memory-load` | `SessionStart` | `.claude/agent-memory/*/MEMORY.md`를 세션 컨텍스트에 자동 주입. |
| `citation-warn` | `PostToolUse:Write\|Edit` | manuscript 마크다운에 인용 없는 문단이 있으면 휴리스틱하게 경고(차단하지 않음). |
| `setup-nudge` | `SessionStart` | CLAUDE.md에 `## Project context` 또는 `## Research stack` 블록이 빠져 있으면 `/omcr-setup` → `/start-research`를 실행하라는 한 줄 nudge(차단하지 않음). |

## Documentation

- **[Wiki home](wiki/Home.md)** — 네비게이션 허브
- **[Getting Started](wiki/Getting-Started.md)** — 설치 + 첫 세션
- **[Configuration](wiki/Configuration.md)** — Research stack 블록, 환경 변수, PII 패턴
- **[Standalone Usage](wiki/Standalone-Usage.md)** — OMCR 단독 사용, 전체 워크스루
- **[With OMC](wiki/With-OMC.md)** — 풀스택: OMCR + OMC companion 설치
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — 레퍼런스
- **[Reading Library](wiki/Reading-Library.md)** — `paper-ingest`: 읽은 논문을 파일링(manuscript BibTeX과는 별개)
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47개의 OMC MCP 도구를 연구 단계별로 매핑
- **[Specializing](wiki/Specializing.md)** — 분야별 프리셋 만들기

## Specializing for your field

코어 에이전트와 커맨드는 분야 중립입니다. 도메인별 색깔(예: 신경과학 방법론, wet-lab 컨벤션, ML 평가 idiom)을 입히려면 `examples/<field>/`에서 프리셋을 오버레이하세요. 현재 제공되는 프리셋:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — 범용 neuro-fMRI 특화. neuro 색이 들어간 `analysis-implementer` 본문 (preprocessing / parcellation / connectivity / ISC / spin tests) + 6명의 에이전트 모두에 대한 redacted MEMORY.md 스켈레톤 제공.

빠른 오버레이:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

자기 프리셋을 직접 만들려면: [`wiki/Specializing.md`](wiki/Specializing.md)를 보세요. 새 프리셋 추가하는 PR(`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) 환영합니다.

## OMC companion (recommended)

OMCR은 [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode)를 *의존성*이 아니라 *companion*으로 봅니다. OMC를 같이 설치하면 아래 컴포넌트들이 연구 워크플로에 자연스럽게 들어맞습니다. 프로젝트에 필요한 것만 골라 쓰세요 — 다 쓸 필요 없습니다.

| Component | Why for research |
|---|---|
| `@scientist` agent | 통계적 엄밀성 강제(신뢰구간 / p-value / 효과 크기 / `[LIMITATION]` 마커). `@analysis-implementer`의 companion. |
| `@document-specialist` agent | OMC의 Context Hub(캐시된 fetch, 구조화된 메모)를 backing으로 한 무거운 literature 리서치. survey 규모의 deep dive가 필요할 때 `@literature-curator`와 함께 쓰세요; OMCR의 curator는 per-claim 인용 해결과 BibTeX/summary-table 관리를 자체적으로 처리합니다. |
| `@verifier` agent | 근거 기반 완료 확인 — 새 테스트 출력 없이 "should work" 주장은 reject. |
| `@tracer` agent + `/oh-my-claudecode:trace` | 근거 기반 경쟁 가설 랭킹 + disconfirmation. methods/results 검증에 매핑. |
| `@writer` agent | lab 프로토콜, methods appendix, 재현성 가이드용 기술 문서 작성자. |
| `@test-engineer` agent | 분석 스크립트 엣지 케이스 커버리지에 대한 TDD 규율. |
| `@git-master` agent | atomic-commit 규율 — 독립적으로 revert 가능한 분석 단계. |
| `/oh-my-claudecode:autoresearch` skill | iteration별 JSON + decision log를 동반한 bounded evaluator-driven 반복 루프. |
| `/oh-my-claudecode:deep-interview` skill | 모호한 연구 목표를 검증 가능한 가설로 Socratic 명료화. |
| OMC 오케스트레이션 스킬 (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | 분석 run, literature 스캔, 반드시 끝내야 하는 revision을 위한 multi-iteration / 병렬 / 합의 오케스트레이터. 5개의 실전 레시피는 [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc)를 보세요. |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP 도구 | Literature wiki / 가설 레지스터 / 실험 run 레지스트리 / stateful Python REPL. |

OMC는 Claude Code marketplace로 함께 설치하거나, `npm i -g oh-my-claude-sisyphus`로 설치하세요. 전체 매핑: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- 에이전트, 스킬, 커맨드 파일명은 **kebab-case**
- 모든 에이전트 / 스킬 / 커맨드에 **YAML frontmatter** 필수 (`name`, `description`, 선택적 `model` / `color` / `memory`)
- `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, 또는 top-level 문서에 **PII 금지** — 기관명, 지도교수명, 실제 subject ID, 이메일, 타깃 저널명, 절대경로. 도메인 특화 콘텐츠는 `examples/<field>/` 아래에만.
- 모든 에이전트에 **English-first** 언어 지시문 (CLAUDE.md에서 override하는 패턴)

전체 contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — [LICENSE](LICENSE) 참조.
