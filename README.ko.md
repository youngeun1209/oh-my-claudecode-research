# oh-my-codex-research (OMXR)

[OpenAI Codex CLI](https://github.com/openai/codex)와 [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex)를 위한 연구용 에디션입니다.

OMXR은 `oh-my-codex`의 research companion입니다. 가설 정리, 분석, 원고 작성, 그림, 인용, 리뷰 대응, 연구 상태 루프를 위한 여섯 개의 연구 에이전트 템플릿과 Codex 스킬을 제공합니다.

## 포함된 것

- 연구 에이전트 6개: `supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`
- 연구 프로젝트 초기 설정: `$omxr-setup`
- 첫 프로젝트 인터뷰: `$start-research`
- 그림/원고 워크플로: `$todofig`, `$sync`, `$figure-bake`, `$outline-expand`
- 문헌/리뷰 워크플로: `$literature-sweep`, `$verify-citation`, `$respond-reviewer`, `$iterate-revision`
- `.omx/state/omxr/` 아래의 durable project state
- `.omx/omxr/agent-memory/` 아래의 agent memory

## 권장 설치

먼저 기본 Codex/OMX 런타임을 설치합니다:

```bash
npm install -g @openai/codex oh-my-codex
omx setup
omx doctor
codex login status
omx exec --skip-git-repo-check -C . "Reply with exactly OMX-EXEC-OK"
```

이후 이 저장소의 Codex plugin manifest를 Codex plugin discovery에 노출합니다:

```text
.codex-plugin/plugin.json
```

plugin manifest는 스킬 발견을 담당합니다. runtime wiring, hook, base config, 일반 `AGENTS.md` 동작은 `omx setup`이 담당하고, 연구 프로젝트 scaffold는 `$omxr-setup`이 담당합니다.

## 연구 프로젝트 시작

연구 프로젝트 안에서:

```text
$omxr-setup
$start-research
```

`$omxr-setup`은 다음을 생성하거나 갱신합니다:

- `AGENTS.md` research blocks
- `.omx/state/omxr/{paper,reviews,citations,figures,rebuttals}.json`
- `.omx/state/omxr/_run-log.jsonl`
- `.omx/omxr/agent-memory/<agent>/MEMORY.md`
- 선택적 `.codex/agents/omxr/<agent>.md`
- `paper/references.bib`
- `references.csv`

`$start-research`는 working title, field, target venue, central hypothesis, datasets, narrative spine, manuscript paths, preset overlay 같은 프로젝트별 내용을 채웁니다.

## 상태와 메모리

OMXR 상태는 프로젝트 로컬 파일이며 기본적으로 gitignore 대상입니다:

```text
.omx/state/omxr/
.omx/omxr/agent-memory/
```

추적되는 소스 템플릿은 다음에 둡니다:

```text
agents/
templates/
develop/example-state/
```

## 안전 장치

Codex/OMX hook 지원은 런타임 버전에 따라 다릅니다. OMXR은 각 기능을 native hook, runtime fallback, explicit check 중 하나로 분류합니다:

- memory load
- setup nudge
- PII scrub
- citation warning

native write interception이 없다면, 원고를 많이 쓰는 워크플로는 finalize 전에 explicit check를 호출해야 합니다.

## 검증

릴리스 전 stale reference guard를 실행합니다:

```bash
bash tools/check-stale-references.sh
```

출력 없이 exit code `0`이면 onboarding/runtime surface에 허용되지 않은 legacy branding이 남아 있지 않다는 뜻입니다.

## 라이선스

MIT — [LICENSE](LICENSE)를 보세요.
