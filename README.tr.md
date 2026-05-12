[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | Türkçe | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Claude Code için çok-ajanlı orkestrasyon — araştırma sürümü. Sıfır öğrenme eğrisi.**

_Araştırma araçlarını öğrenmeyin. Sadece OMCR kullanın._

OMCR, [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)'un araştırma odaklı kardeşidir. OMC genel kod işlerini yürütme motorlarıyla (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`) orkestre ederken, OMCR *araştırma akışını* **6 alana özel motor** ile orkestre eder — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` ve otonom `/supervisor-drive`. Tek başlarına veya birlikte kullanın: OMCR motorları OMC'nin genel döngüleri içinde retry (`/ralph`), paralellik (`/team`, `/ultrawork`), çok stratejili keşif (`/ultraqa`) veya bütçe takipli sürüşler (`/autopilot`) için çalışır. Tam task → tool matrisi için [`wiki/Orchestration-Comparison.md`](wiki/Orchestration-Comparison.md), uygulamalı tarifler için [`wiki/With-OMC.md`](wiki/With-OMC.md).

6 araştırma ajanı + 6 orkestrasyon motoru + 4 setup/workflow komutu + 14 skill (1 primitive + 13 backing surface) + 4 hafif hook. Tam motor walkthrough: [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md)

> **Durum: v0.1.** Breaking change'ler muhtemel. Geri bildirim ve PR'lar memnuniyetle.

> **Tam dokümantasyon:** [`wiki/Home.md`](wiki/Home.md)

## Install

**Önerilen — Claude Code marketplace akışı** (satır başına bir slash komutu, teker teker girin):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Alternatif — manuel checkout** (plugin yöneticisi olmadan):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Sonra Claude Code'u açın ve yüklemek için `/plugin` çalıştırın. Yüklemeden sonra (hangi yoldan olursa):
- 6 ajan `@`-mention seçicisinde görünür
- 10 slash komutu seçicide görünür: `/omcr-setup`, `/start-research`, `/todofig`, `/sync` (setup/workflow) + `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` (orkestrasyon motorları)
- 14 skill çağrılabilir hale gelir (7 setup/workflow + 1 primitive `orchestrate` + 6 engine skill)
- 4 hook oturum başında kaydolur (PII koruma, MEMORY otomatik yükleme, atıf uyarısı, setup nudge)

**Dosya-bazlı cherry-pick** (plugin yöneticisi yok — sadece ajanları belirli bir projeye kopyala):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Bu yol komutları, skill'leri ve hook'ları atlar. Tam özellik için plugin kurulumunu kullanın.

## Quick start

Kurduktan sonra bir araştırma projesi açın ve sırayla çalıştırın:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** kurulum tarzıdır — araştırmanız hakkında soru yok. Sadece altyapı serer: `CLAUDE.md`'de boş `## Project context` / `## Research stack` / `## Language preference` blokları, 6 ajan için `.claude/agent-memory/<agent>/MEMORY.md` (kanonik template), literature-curator için boş `paper/references.bib` + `./references.csv`, ve `.claude/settings.json`'da küratörlü izin allowlist (read-only git, dosya araması, LaTeX build, citation API, figure crop — Python analizi opt-in; git write ve dosya silme elle kalır).

**`/start-research`** mülakattır. Bu placeholder'ları doldurmanızda size eşlik eder:
- **Project context** (çalışma başlığı, alan, hedef venue, merkezi hipotez, araştırma konusu, datasetler, anlatı omurgası)
- **Research stack** (deck/outline yolları, figure sayısı, BibTeX + summary-table yolları, opsiyonel CrossRef email)
- **Preset overlay** (opsiyonel — `examples/neuro-fmri/` vb. — sadece hâlâ kanonik template ile byte-identical olan `MEMORY.md` dosyalarını değiştirir)
- **Manuscript scaffold** (`manuscript-scaffold` skill'ine delege: LaTeX skeleton + dergi template lookup + opsiyonel Overleaf clone)

`/start-research`'i `/omcr-setup`'tan önce çalıştırırsanız, önce `/omcr-setup`'u çalıştırmayı önerir. Atlanan bilimsel alanlar `[TBD: <kısa not>]` olarak kaydedilir — asla uydurulmaz — ki `@supervisor` follow-up etmesi gerektiğini bilsin.

İkisini de atlarsanız, SessionStart `setup-nudge` hook'u initialize edene kadar her oturumda tek satırlık hatırlatma yazdırır. `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` ile susturulur.

İkisinden sonra gerçek bir konuşma başlatın:

```
@supervisor where are we?
```

Tam walkthrough: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI seviyesinde bilimsel vizyon koruyucusu + proje orkestratörü. Merkezi hipotezi sahiplenir; alt ajanlara delege eder. |
| `@analysis-implementer` | Pipeline, istatistiksel analiz, ML/simülasyon modellerini uygular. Varsayılan olarak alan-nötr. |
| `@paper-writer` | Manuscript bölümlerini high-impact dergi düzeyinde nesirle yazar. |
| `@figure-descriptor` | Şekilleri implementasyona hazır brief'ler olarak tasarlar — görüntü üretmez. |
| `@reviewer` | Hedef venue seviyesinde gönderim öncesi adversarial review. |
| `@literature-curator` | Projenin BibTeX'i ve literature summary table'ını lockstep tutar. `[CITE: ...]` placeholder'larını çözer, atıfları `verify-citation` skill'iyle doğrular, asla uydurmaz. |

### 4 slash commands (projenizin CLAUDE.md'si üzerinden parametrelenir)

| Command | What it does |
|---|---|
| `/omcr-setup` | Kurulum tarzı: `CLAUDE.md`'ye boş işaretleyici blokları, `.claude/agent-memory/` dizinleri, boş `references.bib`/`references.csv`, ve `.claude/settings.json`'da küratörlü izin allowlist'i yerleştirir. **Araştırmanız hakkında soru sormaz.** Proje başına bir kez çalıştırın. |
| `/start-research [minimal\|neuro-fmri]` | Mülakat tarzı: `CLAUDE.md` placeholder'larını doldurur (çalışma başlığı, hipotez, hedef venue, datasetler, anlatı omurgası), isteğe bağlı olarak ajan belleğine bir preset uygular, LaTeX manuscript dizinini scaffold eder (`manuscript-scaffold` skill'i aracılığıyla, dergi template'i + opsiyonel Overleaf clone ile). Eğer `/omcr-setup` çalıştırılmamışsa önce onu çalıştırmayı önerir. |
| `/todofig [Fig N]` | Yakalanan bir figure deck'i bir outline ile karşılaştırır → P0/P1/P2 öncelikli TODO. |
| `/sync` | Mevcut durumu (deck) hedefle (outline) uzlaştırır, ajan belleklerini tazeler, isteğe bağlı olarak crop'lanmış figure'ları hedef belgeye gömer. Bir snapshot, TODO değil. |

### 14 skills

4 setup/workflow slash komutu thin dispatcher'lardır — her biri `$ARGUMENTS`'i eşleşen bir skill'e forward eder. `cropfig`, `verify-citation`, `manuscript-scaffold` bağımsız olarak da çağrılabilir. **Ek olarak** 1 primitive (`orchestrate` — dahili, 4 fazdan compose olur) + 6 orkestrasyon komutunu destekleyen engine skill; tam walkthrough [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Aşağıdaki tablo 7 setup/workflow skill'ini kapsar.

| Skill | What it does |
|---|---|
| `omcr-setup` | `/omcr-setup` arkasında. Kurulum tarzı: `CLAUDE.md` işaretleyici blokları, agent-memory dizinleri, bibliografi dosyaları, küratörlü izin allowlist'i scaffold eder. |
| `start-research` | `/start-research` arkasında. Mülakat tarzı ilk proje init: scaffold edilmiş `CLAUDE.md` placeholder'larını doldurur, isteğe bağlı preset overlay uygular, manuscript scaffold'u `manuscript-scaffold`'a delege eder. |
| `sync` | `/sync` arkasında. Mevcut durumu (yakalanmış figure deck) outline ile uzlaştırır; ajan belleklerini olgusal drift'lerle tazeler; sadece snapshot (TODO yok). |
| `todofig` | `/todofig` arkasında. Yakalanmış figure deck ile outline'ı karşılaştırır; gap'ler için P0/P1/P2 öncelikli TODO üretir. |
| `cropfig` | `.key`/`.pptx` deck'ten manuscript + outline artifact'larına üç adımlı pipeline: slide-başına vektör PDF (cropped, manuscript-grade) + outline-grade PNG. Doğrudan veya başka komutlar tarafından çağrılır; slash yok. |
| `verify-citation` | CrossRef/OpenAlex aracılığıyla varlık + metadata kontrolü. `@literature-curator`'ın eklediği her girdiyi gate'ler, doğrulama sonucunu projenin summary table'ına yazar. |
| `manuscript-scaffold` | Paketlenmiş LaTeX skeleton'u kullanıcının manuscript dizinine kopyalar, isteğe bağlı olarak paketlenmiş registry'den dergiye özel `\documentclass` uygular, isteğe bağlı olarak bir Overleaf projesini clone'lar (token tracked dosyalara persist edilmez), default branch'e commit atar, push öncesi sorar. `/start-research` faz 6 tarafından çağrılır; bağımsız olarak da çağrılabilir. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | PII (varsayılan: email / SSN / subject ID; yapılandırılabilir) içeren write'ları engeller. |
| `memory-load` | `SessionStart` | `.claude/agent-memory/*/MEMORY.md`'yi oturum bağlamına otomatik inject eder. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Manuscript markdown'da atıfsız paragraflar olduğunda heuristic, bloklamayan uyarı. |
| `setup-nudge` | `SessionStart` | CLAUDE.md'de `## Project context` veya `## Research stack` blokları yoksa, `/omcr-setup` ardından `/start-research` çalıştırmak için bloklamayan tek satırlık dürtü. |

## Documentation

- **[Wiki home](wiki/Home.md)** — navigasyon merkezi
- **[Getting Started](wiki/Getting-Started.md)** — kurulum + ilk oturum
- **[Configuration](wiki/Configuration.md)** — Research stack bloğu, env değişkenler, PII pattern'leri
- **[Standalone Usage](wiki/Standalone-Usage.md)** — OMCR'ı tek başına kullanma, tam walkthrough
- **[With OMC](wiki/With-OMC.md)** — full stack: OMCR + OMC companion kurulumu
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — referanslar
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 OMC MCP aracının araştırma aşamalarına mapping'i
- **[Specializing](wiki/Specializing.md)** — alan-özel preset yazma

## Specializing for your field

Core ajanlar ve komutlar alan-nötrdür. Domain rengi için (örn. nöroscience metodolojisi, wet-lab kuralları, ML değerlendirme idiomları), `examples/<field>/`'den bir preset overlay yapın. Şu anda mevcut:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generic neuro-fMRI uzmanlaşması. Neuro lezzetli `analysis-implementer` gövdesi (preprocessing / parcellation / connectivity / ISC / spin tests) + 6 ajan için redacted MEMORY.md iskeletleri sağlar.

Hızlı overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

Kendi preset'inizi yazmak için: [`wiki/Specializing.md`](wiki/Specializing.md). Yeni preset ekleyen PR'lar (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) memnuniyetle.

## OMC companion (recommended)

OMCR, [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode)'u bağımlılık olarak değil *companion* olarak görür. OMC yan yana kuruluyken aşağıdaki bileşenler araştırma akışlarına doğal olarak uyar. Projenize uygun olanları seçin — hepsini kullanmak zorunda değilsiniz.

| Component | Why for research |
|---|---|
| `@scientist` agent | İstatistiksel sıkılığı dayatan (CI / p-değerleri / etki boyutu / `[LIMITATION]` işaretleyicileri). `@analysis-implementer`'ın companion'ı. |
| `@document-specialist` agent | OMC'nin Context Hub'ı (cache'lenmiş fetch'ler, yapılandırılmış notlar) destekli daha ağır literature araştırması. Survey ölçeğinde deep dive gerektiğinde `@literature-curator` ile birlikte kullanın; OMCR'ın curator'ı per-claim citation çözümü ve BibTeX/summary-table yönetimini kendi başına halleder. |
| `@verifier` agent | Kanıt temelli tamamlama kontrolü — taze test çıktısı olmadan "should work" iddialarını reddeder. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Kanıt-driven rakip hipotez sıralaması + disconfirmation. Methods/results doğrulamasına map olur. |
| `@writer` agent | Lab protokolleri, methods appendix'leri, yeniden üretilebilirlik kılavuzları için teknik dokümantasyon yazarı. |
| `@test-engineer` agent | Analiz scriptlerinde edge case coverage için TDD disiplini. |
| `@git-master` agent | Atomic-commit disiplini — bağımsız revert edilebilir analiz adımları. |
| `/oh-my-claudecode:autoresearch` skill | Per-iteration JSON + decision log eşliğinde bounded evaluator-driven iterasyon döngüsü. |
| `/oh-my-claudecode:deep-interview` skill | Belirsiz araştırma hedeflerinin test edilebilir hipotezlere Sokratik netleşmesi. |
| OMC orkestrasyon skill'leri (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Analiz koşumları, literatür taramaları, mutlaka bitirilmesi gereken revizyonlar için multi-iteration / paralel / consensus orkestratörler. 5 uygulamalı tarif için [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc). |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP araçları | Literature wiki / hipotez register / deney koşum registry / stateful Python REPL. |

OMC'yi Claude Code marketplace üzerinden yan yana kurun ya da `npm i -g oh-my-claude-sisyphus`. Tam mapping: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md)

## Conventions (contributors)

- Ajanlar, skill'ler, komutlar için **kebab-case** dosya adları
- Her ajan / skill / komutta **YAML frontmatter** zorunlu (`name`, `description`, opsiyonel `model` / `color` / `memory`)
- `agents/`, `commands/`, `skills/`, `templates/`, `hooks/` veya üst düzey docs'ta **PII yok** — kurumlar, danışmanlar, gerçek subject ID'leri, email'ler, hedef dergi adları, mutlak yollar. Alan-özel içerik yalnızca `examples/<field>/` altında.
- Tüm ajanlarda **English-first** dil direktifi (CLAUDE.md'de override etme deseni)

Tam contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — [LICENSE](LICENSE) görün.
