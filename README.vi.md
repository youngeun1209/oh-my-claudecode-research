[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | Tiếng Việt | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Điều phối đa tác nhân cho Claude Code — phiên bản dành cho nghiên cứu. Không cần học.**

_Đừng học công cụ nghiên cứu. Cứ dùng OMCR._

OMCR là một không gian làm việc nghiên cứu cho Claude Code: sáu agent — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — bạn cùng làm việc trên giả thuyết, phân tích, viết, figure, citation, review. Sáu engine điều phối tự động hóa các vòng lặp phổ biến khi bạn muốn hands-off. Kết hợp với [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) khi cần điều phối tổng quát ở tầng trên (retry, parallel, budget tracking).

Đội nghiên cứu 6 agent + 6 engine điều phối + 4 lệnh setup/workflow + 14 skill + 4 hook nhẹ.

> **Trạng thái: v0.1.** Có thể có thay đổi phá vỡ tương thích. Hoan nghênh feedback và PR.

> **Tài liệu đầy đủ:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: Cài đặt**

**Nếu bạn cài OMCR lần đầu** — luồng marketplace (khuyến nghị). Đây là lệnh slash của Claude Code, gõ **từng cái một**:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

Sau đó:

```
/plugin install oh-my-claudecode-research
```

**Nếu bạn muốn checkout thủ công** (không plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**Nếu OMCR đã cài và bạn muốn update** — chạy hai lệnh slash sau, từng cái một:

```
/plugin marketplace update omcr
```

Sau đó:

```
/plugin update oh-my-claudecode-research
```

Lệnh đầu chỉ refresh metadata của marketplace; lệnh thứ hai mới thực sự kéo file plugin mới về. OMCR theo nhánh `main`, nên mỗi commit mới được coi như một phiên bản mới. Trạng thái dự án của bạn (CLAUDE.md, agent memory, settings) không bị động vào — không cần chạy lại Step 2.

**Step 2: Khởi tạo**

**Chỉ cần làm một lần cho mỗi dự án.** Trong một phiên Claude Code ở dự án nghiên cứu của bạn, chạy lệnh slash **từng cái một**:

```
/omcr-setup
```

Sau đó:

```
/start-research
```

`/omcr-setup` lát hạ tầng — các block trống `## Project context` / `## Research stack` / `## Language preference` trong `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` cho cả 6 agent, `paper/references.bib` + `./references.csv` trống cho literature-curator, và một allowlist quyền được tuyển chọn trong `.claude/settings.json`. **Không hỏi về nghiên cứu của bạn.**

`/start-research` là phỏng vấn. Nó dẫn bạn điền các placeholder đó:
- **Project context** (working title, lĩnh vực, venue mục tiêu, giả thuyết trung tâm, chủ đề nghiên cứu, dataset, mạch truyện)
- **Research stack** (đường dẫn deck/outline, số figure, đường dẫn BibTeX + summary-table, email CrossRef tùy chọn)
- **Preset overlay** (tùy chọn — `examples/neuro-fmri/` v.v. — chỉ thay file `MEMORY.md` của agent còn byte-identical với template canonical)
- **Manuscript scaffold** (ủy quyền cho skill `manuscript-scaffold`: LaTeX skeleton + lookup template tạp chí + clone Overleaf tùy chọn)

Nếu bạn chạy `/start-research` trước `/omcr-setup`, nó đề nghị chạy `/omcr-setup` trước. Các field khoa học bị bỏ qua được lưu thành `[TBD: <ghi chú ngắn>]` — không bao giờ bịa — để `@supervisor` biết cần follow up. Nếu bỏ qua cả hai, hook `setup-nudge` ở SessionStart in một dòng nhắc mỗi phiên cho tới khi bạn init (tắt bằng `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Bắt đầu**

```
@supervisor where are we?
```

Hướng dẫn đầy đủ: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | Người giữ tầm nhìn khoa học cấp PI + người điều phối dự án. Sở hữu giả thuyết trung tâm; ủy quyền cho subagent. |
| `@analysis-implementer` | Triển khai pipeline, phân tích thống kê, mô hình ML/mô phỏng. Mặc định trung tính theo ngành. |
| `@paper-writer` | Soạn các phần manuscript với chất lượng văn xuôi tạp chí high-impact. |
| `@figure-descriptor` | Thiết kế figure dưới dạng brief sẵn sàng triển khai — không tạo ảnh. |
| `@reviewer` | Review đối kháng trước khi submit ở mức của venue mục tiêu. |
| `@literature-curator` | Sở hữu đồng bộ BibTeX và bảng tóm tắt literature của dự án. Giải quyết placeholder `[CITE: ...]`, xác minh trích dẫn qua skill `verify-citation`, không bao giờ bịa. |

### 4 slash commands (tham số hóa qua CLAUDE.md của dự án)

| Command | What it does |
|---|---|
| `/omcr-setup` | Kiểu cài đặt: scaffold các block marker rỗng trong `CLAUDE.md`, thư mục `.claude/agent-memory/`, `references.bib`/`references.csv` rỗng, và một allowlist quyền được tuyển chọn trong `.claude/settings.json`. **Không hỏi gì về nghiên cứu của bạn.** Chạy một lần mỗi dự án. |
| `/start-research [minimal\|neuro-fmri]` | Kiểu phỏng vấn: điền các placeholder trong `CLAUDE.md` (working title, giả thuyết, venue mục tiêu, dataset, mạch truyện), tùy chọn áp preset vào agent memory, scaffold thư mục LaTeX manuscript (qua skill `manuscript-scaffold`, kèm template tạp chí + clone Overleaf tùy chọn). Đề nghị chạy `/omcr-setup` trước nếu chưa chạy. |
| `/todofig [Fig N]` | So sánh deck figure đã chụp với outline → TODO ưu tiên P0/P1/P2. |
| `/sync` | Đồng bộ trạng thái hiện tại (deck) với mục tiêu (outline), refresh agent memory, tùy chọn nhúng figure đã crop vào tài liệu mục tiêu. Snapshot trạng thái, không phải TODO. |

### 14 skills

4 lệnh slash setup/workflow là thin dispatcher — mỗi cái forward `$ARGUMENTS` đến skill cùng tên. `cropfig`, `verify-citation`, `manuscript-scaffold` cũng có thể gọi độc lập. **Cộng thêm** 1 primitive (`orchestrate` — nội bộ, ghép từ 4 phase) + 6 engine skill backing 6 lệnh điều phối; hướng dẫn đầy đủ ở [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Bảng dưới phủ 7 skill setup/workflow.

| Skill | What it does |
|---|---|
| `omcr-setup` | Backing `/omcr-setup`. Kiểu cài đặt: scaffold block marker trong `CLAUDE.md`, thư mục agent-memory, file bibliography, allowlist quyền được tuyển chọn. |
| `start-research` | Backing `/start-research`. Init dự án đầu kiểu phỏng vấn: điền các placeholder đã scaffold trong `CLAUDE.md`, tùy chọn áp preset overlay, ủy quyền manuscript scaffold cho `manuscript-scaffold`. |
| `sync` | Backing `/sync`. Đồng bộ trạng thái hiện tại (deck figure đã chụp) với outline; refresh agent memory bằng drift thực tế; chỉ snapshot trạng thái (không TODO). |
| `todofig` | Backing `/todofig`. So sánh deck figure đã chụp với outline; tạo TODO ưu tiên P0/P1/P2 cho các gap. |
| `cropfig` | Pipeline ba bước từ deck `.key`/`.pptx` đến artifact manuscript + outline: PDF vector từng slide (đã crop, chất lượng manuscript) + PNG chất lượng outline. Gọi trực tiếp hoặc bởi lệnh khác; không có slash. |
| `verify-citation` | Kiểm tra tồn tại + metadata qua CrossRef/OpenAlex. Gate mọi entry mà `@literature-curator` thêm vào, ghi phán quyết xác minh vào summary table của dự án. |
| `manuscript-scaffold` | Sao chép LaTeX skeleton đi kèm vào thư mục manuscript của người dùng, tùy chọn áp `\documentclass` đặc thù tạp chí từ registry đi kèm, tùy chọn clone dự án Overleaf (token không persist vào file được track), commit trên nhánh mặc định, hỏi trước khi push. Được `/start-research` phase 6 gọi; cũng có thể gọi độc lập. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Chặn write chứa PII (mặc định: email / SSN / subject ID; có thể cấu hình). |
| `memory-load` | `SessionStart` | Tự inject `.claude/agent-memory/*/MEMORY.md` vào context phiên. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Cảnh báo heuristic không chặn khi markdown manuscript có đoạn không trích dẫn. |
| `setup-nudge` | `SessionStart` | Nudge một dòng không chặn để chạy `/omcr-setup` rồi `/start-research` nếu CLAUDE.md thiếu block `## Project context` hoặc `## Research stack`. |

## Documentation

- **[Wiki home](wiki/Home.md)** — trung tâm điều hướng
- **[Getting Started](wiki/Getting-Started.md)** — cài + phiên đầu tiên
- **[Configuration](wiki/Configuration.md)** — block Research stack, env vars, pattern PII
- **[Standalone Usage](wiki/Standalone-Usage.md)** — dùng OMCR một mình, hướng dẫn đầy đủ
- **[With OMC](wiki/With-OMC.md)** — full stack: cài OMCR + OMC companion
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — tham chiếu
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 công cụ OMC MCP được map vào các giai đoạn nghiên cứu
- **[Specializing](wiki/Specializing.md)** — viết preset đặc thù ngành

## Specializing for your field

Agent và lệnh trong core là trung tính theo ngành. Để thêm màu domain (ví dụ phương pháp neuroscience, quy ước wet-lab, idiom đánh giá ML), overlay một preset từ `examples/<field>/`. Hiện đang cung cấp:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — chuyên hóa neuro-fMRI generic. Cung cấp thân `analysis-implementer` đậm chất neuro (preprocessing / parcellation / connectivity / ISC / spin tests) + bộ khung MEMORY.md đã redact cho cả 6 agent.

Overlay nhanh:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Để tự viết preset của bạn: xem [`wiki/Specializing.md`](wiki/Specializing.md). Hoan nghênh PR thêm preset mới (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …).

## OMC companion (recommended)

OMCR coi [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) là *companion*, không phải dependency. Khi cài OMC song song, các component sau ăn khớp tự nhiên vào quy trình nghiên cứu. Chọn cái phù hợp dự án bạn — không cần dùng hết.

| Component | Why for research |
|---|---|
| `@scientist` agent | Người ép tuân thủ nghiêm ngặt thống kê (CI / p-value / effect size / marker `[LIMITATION]`). Companion của `@analysis-implementer`. |
| `@document-specialist` agent | Nghiên cứu literature nặng đô được hậu thuẫn bởi Context Hub của OMC (fetch cache, ghi chú có cấu trúc). Dùng cùng `@literature-curator` khi cần deep dive cỡ survey; curator của OMCR tự xử lý resolution citation per-claim và quản lý BibTeX/summary-table. |
| `@verifier` agent | Kiểm tra hoàn thành dựa trên bằng chứng — từ chối tuyên bố "should work" không có output test mới. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Xếp hạng giả thuyết cạnh tranh dựa trên bằng chứng + disconfirmation. Map vào xác thực methods/results. |
| `@writer` agent | Người viết tài liệu kỹ thuật cho protocol lab, appendix methods, hướng dẫn tái lập. |
| `@test-engineer` agent | Kỷ luật TDD cho coverage edge case script phân tích. |
| `@git-master` agent | Kỷ luật atomic-commit — các bước phân tích có thể revert độc lập. |
| `/oh-my-claudecode:autoresearch` skill | Vòng lặp lặp bounded evaluator-driven với JSON + decision log mỗi iteration. |
| `/oh-my-claudecode:deep-interview` skill | Làm rõ kiểu Socratic mục tiêu nghiên cứu mơ hồ thành giả thuyết kiểm tra được. |
| Skill điều phối OMC (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Bộ điều phối multi-iteration / parallel / consensus cho lần chạy phân tích, quét literature, revision phải hoàn thành. Xem [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) cho 5 công thức thực tế. |
| Công cụ MCP `wiki_*` / `notepad_*` / `state_*` / `python_repl` | Wiki literature / register giả thuyết / registry lần chạy thí nghiệm / REPL Python có state. |

Cài OMC song song qua Claude Code marketplace, hoặc `npm i -g oh-my-claude-sisyphus`. Mapping đầy đủ: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Tên file **kebab-case** cho agent, skill, lệnh
- **YAML frontmatter** bắt buộc trên mọi agent / skill / lệnh (`name`, `description`, tùy chọn `model` / `color` / `memory`)
- **Không PII** trong `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, hoặc tài liệu top-level — tên tổ chức, tên cố vấn, ID subject thật, email, tên tạp chí mục tiêu, đường dẫn tuyệt đối. Nội dung đặc thù domain chỉ nằm dưới `examples/<field>/`.
- Directive ngôn ngữ **English-first** trên mọi agent (pattern override-in-CLAUDE.md)

Contract đầy đủ: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — xem [LICENSE](LICENSE).
