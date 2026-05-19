[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | Türkçe | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-codex-research

**Codex için çok-ajanlı orkestrasyon — araştırma sürümü. Sıfır öğrenme eğrisi.**

_Araştırma araçlarını öğrenmeyin. Sadece OMXR kullanın._

OMXR, Codex için bir araştırma çalışma alanıdır: altı ajan — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — ile birlikte hipotez, analiz, yazım, figure, atıflar, review üzerinde çalışırsınız. Hands-off istediğinizde altı orkestrasyon motoru yaygın döngüleri otomatikleştirir. Üstte genel orkestrasyon (retry, paralellik, bütçe takibi) lazımsa [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) ile birleştirin.

6 araştırma ajanı + 6 orkestrasyon motoru + 4 setup/workflow komutu + 14 skill + 4 hafif hook.

> **Durum: v0.1.** Breaking change'ler muhtemel. Geri bildirim ve PR'lar memnuniyetle.

> **Tam dokümantasyon:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 1: Kurulum**

**OMXR'ı ilk kez kuruyorsanız** — marketplace akışı (önerilir). Bunlar Codex slash komutlarıdır, **teker teker** girin:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-codex-research
```

Sonra:

```
/plugin install oh-my-codex-research
```

**Manuel checkout istiyorsanız** (plugin yöneticisi olmadan):

```bash
git clone https://github.com/youngeun1209/oh-my-codex-research \
  ~/.codex/plugins/oh-my-codex-research
```

**OMXR zaten kuruluysa ve güncellemek istiyorsanız** — aşağıdaki iki slash komutunu teker teker çalıştırın:

```
/plugin marketplace update omxr
```

Sonra:

```
/plugin update oh-my-codex-research
```

İlki sadece marketplace metadata'sını yeniler; ikincisi gerçekten yeni plugin dosyalarını çeker. OMXR `main` dalını takip ettiği için her yeni commit yeni sürüm olarak işlenir. Projenizin durumu (AGENTS.md, ajan belleği, ayarlar) değişmez — Step 2'yi yeniden çalıştırmaya gerek yok.

**Step 2: Yapılandırma**

**Proje başına yalnızca bir kez yapılır.** Araştırma projenizdeki bir Codex oturumu içinde slash komutlarını **teker teker** çalıştırın:

```
$omxr-setup
```

Sonra:

```
$start-research
```

`$omxr-setup` altyapıyı serer — `AGENTS.md`'de boş `## Project context` / `## Research stack` / `## Language preference` blokları, 6 ajanın hepsi için `.omx/omxr/agent-memory/<agent>/MEMORY.md`, literature-curator için boş `paper/references.bib` + `./references.csv`, ve hook/check readiness. **Araştırmanız hakkında soru yok.**

`$start-research` mülakattır. Bu placeholder'ları doldurmanızda size eşlik eder:
- **Project context** (çalışma başlığı, alan, hedef venue, merkezi hipotez, araştırma konusu, datasetler, anlatı omurgası)
- **Research stack** (deck/outline yolları, figure sayısı, BibTeX + summary-table yolları, opsiyonel CrossRef email)
- **Preset overlay** (opsiyonel — `examples/neuro-fmri/` vb. — sadece hâlâ kanonik template ile byte-identical olan `MEMORY.md` dosyalarını değiştirir)
- **Manuscript scaffold** (`manuscript-scaffold` skill'ine delege: LaTeX skeleton + dergi template lookup + opsiyonel Overleaf clone)

`$start-research`'i `$omxr-setup`'tan önce çalıştırırsanız, önce `$omxr-setup`'u çalıştırmayı önerir. Atlanan bilimsel alanlar `[TBD: <kısa not>]` olarak kaydedilir — asla uydurulmaz — ki `@supervisor` follow-up etmesi gerektiğini bilsin. İkisini de atlarsanız, SessionStart `setup-nudge` hook'u initialize edene kadar her oturumda tek satırlık hatırlatma yazdırır (`CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1` ile susturulur).

**Step 3: Başla**

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

### 4 workflow commands (projenizin AGENTS.md'si üzerinden parametrelenir)

| Command | What it does |
|---|---|
| `$omxr-setup` | Kurulum tarzı: `AGENTS.md`'ye boş işaretleyici blokları, `.omx/omxr/agent-memory/` dizinleri, boş `references.bib`/`references.csv`, ve hook/check readiness'i yerleştirir. **Araştırmanız hakkında soru sormaz.** Proje başına bir kez çalıştırın. |
| `$start-research [minimal\|neuro-fmri]` | Mülakat tarzı: `AGENTS.md` placeholder'larını doldurur (çalışma başlığı, hipotez, hedef venue, datasetler, anlatı omurgası), isteğe bağlı olarak ajan belleğine bir preset uygular, LaTeX manuscript dizinini scaffold eder (`manuscript-scaffold` skill'i aracılığıyla, dergi template'i + opsiyonel Overleaf clone ile). Eğer `$omxr-setup` çalıştırılmamışsa önce onu çalıştırmayı önerir. |
| `$todofig [Fig N]` | Yakalanan bir figure deck'i bir outline ile karşılaştırır → P0/P1/P2 öncelikli TODO. |
| `$sync` | Mevcut durumu (deck) hedefle (outline) uzlaştırır, ajan belleklerini tazeler, isteğe bağlı olarak crop'lanmış figure'ları hedef belgeye gömer. Bir snapshot, TODO değil. |

### 14 skills

4 setup/workflow slash komutu thin dispatcher'lardır — her biri `$ARGUMENTS`'i eşleşen bir skill'e forward eder. `cropfig`, `verify-citation`, `manuscript-scaffold` bağımsız olarak da çağrılabilir. **Ek olarak** 1 primitive (`orchestrate` — dahili, 4 fazdan compose olur) + 6 orkestrasyon komutunu destekleyen engine skill; tam walkthrough [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). Aşağıdaki tablo 7 setup/workflow skill'ini kapsar.

| Skill | What it does |
|---|---|
| `omxr-setup` | `$omxr-setup` arkasında. Kurulum tarzı: `AGENTS.md` işaretleyici blokları, agent-memory dizinleri, bibliografi dosyaları, küratörlü izin hook/check readiness'i scaffold eder. |
| `start-research` | `$start-research` arkasında. Mülakat tarzı ilk proje init: scaffold edilmiş `AGENTS.md` placeholder'larını doldurur, isteğe bağlı preset overlay uygular, manuscript scaffold'u `manuscript-scaffold`'a delege eder. |
| `sync` | `$sync` arkasında. Mevcut durumu (yakalanmış figure deck) outline ile uzlaştırır; ajan belleklerini olgusal drift'lerle tazeler; sadece snapshot (TODO yok). |
| `todofig` | `$todofig` arkasında. Yakalanmış figure deck ile outline'ı karşılaştırır; gap'ler için P0/P1/P2 öncelikli TODO üretir. |
| `cropfig` | `.key`/`.pptx` deck'ten manuscript + outline artifact'larına üç adımlı pipeline: slide-başına vektör PDF (cropped, manuscript-grade) + outline-grade PNG. Doğrudan veya başka komutlar tarafından çağrılır; slash yok. |
| `verify-citation` | CrossRef/OpenAlex aracılığıyla varlık + metadata kontrolü. `@literature-curator`'ın eklediği her girdiyi gate'ler, doğrulama sonucunu projenin summary table'ına yazar. |
| `manuscript-scaffold` | Paketlenmiş LaTeX skeleton'u kullanıcının manuscript dizinine kopyalar, isteğe bağlı olarak paketlenmiş registry'den dergiye özel `\documentclass` uygular, isteğe bağlı olarak bir Overleaf projesini clone'lar (token tracked dosyalara persist edilmez), default branch'e commit atar, push öncesi sorar. `$start-research` faz 6 tarafından çağrılır; bağımsız olarak da çağrılabilir. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | PII (varsayılan: email / SSN / subject ID; yapılandırılabilir) içeren write'ları engeller. |
| `memory-load` | `SessionStart` | `.omx/omxr/agent-memory/*/MEMORY.md`'yi oturum bağlamına otomatik inject eder. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Manuscript markdown'da atıfsız paragraflar olduğunda heuristic, bloklamayan uyarı. |
| `setup-nudge` | `SessionStart` | AGENTS.md'de `## Project context` veya `## Research stack` blokları yoksa, `$omxr-setup` ardından `$start-research` çalıştırmak için bloklamayan tek satırlık dürtü. |

## Documentation

- **[Wiki home](wiki/Home.md)** — navigasyon merkezi
- **[Getting Started](wiki/Getting-Started.md)** — kurulum + ilk oturum
- **[Configuration](wiki/Configuration.md)** — Research stack bloğu, env değişkenler, PII pattern'leri
- **[Standalone Usage](wiki/Standalone-Usage.md)** — OMXR'ı tek başına kullanma, tam walkthrough
- **[With OMX](wiki/With-OMX.md)** — full stack: OMXR + OMX companion kurulumu
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — referanslar
- **[OMX Tool Reference](wiki/OMX-Tool-Reference.md)** — 47 OMX MCP aracının araştırma aşamalarına mapping'i
- **[Specializing](wiki/Specializing.md)** — alan-özel preset yazma

## Specializing for your field

Core ajanlar ve komutlar alan-nötrdür. Domain rengi için (örn. nöroscience metodolojisi, wet-lab kuralları, ML değerlendirme idiomları), `examples/<field>/`'den bir preset overlay yapın. Şu anda mevcut:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generic neuro-fMRI uzmanlaşması. Neuro lezzetli `analysis-implementer` gövdesi (preprocessing / parcellation / connectivity / ISC / spin tests) + 6 ajan için redacted MEMORY.md iskeletleri sağlar.

Hızlı overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .omx/omxr/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .omx/omxr/agent-memory/$agent/MEMORY.md
done
```

Kendi preset'inizi yazmak için: [`wiki/Specializing.md`](wiki/Specializing.md). Yeni preset ekleyen PR'lar (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) memnuniyetle.

## OMX companion (recommended)

OMXR, [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex)'u bağımlılık olarak değil *companion* olarak görür. OMX yan yana kuruluyken aşağıdaki bileşenler araştırma akışlarına doğal olarak uyar. Projenize uygun olanları seçin — hepsini kullanmak zorunda değilsiniz.

| Component | Why for research |
|---|---|
| `@scientist` agent | İstatistiksel sıkılığı dayatan (CI / p-değerleri / etki boyutu / `[LIMITATION]` işaretleyicileri). `@analysis-implementer`'ın companion'ı. |
| `@document-specialist` agent | OMX'nin Context Hub'ı (cache'lenmiş fetch'ler, yapılandırılmış notlar) destekli daha ağır literature araştırması. Survey ölçeğinde deep dive gerektiğinde `@literature-curator` ile birlikte kullanın; OMXR'ın curator'ı per-claim citation çözümü ve BibTeX/summary-table yönetimini kendi başına halleder. |
| `@verifier` agent | Kanıt temelli tamamlama kontrolü — taze test çıktısı olmadan "should work" iddialarını reddeder. |
| `@tracer` agent + `/oh-my-codex:trace` | Kanıt-driven rakip hipotez sıralaması + disconfirmation. Methods/results doğrulamasına map olur. |
| `@writer` agent | Lab protokolleri, methods appendix'leri, yeniden üretilebilirlik kılavuzları için teknik dokümantasyon yazarı. |
| `@test-engineer` agent | Analiz scriptlerinde edge case coverage için TDD disiplini. |
| `@git-master` agent | Atomic-commit disiplini — bağımsız revert edilebilir analiz adımları. |
| `/oh-my-codex:autoresearch` skill | Per-iteration JSON + decision log eşliğinde bounded evaluator-driven iterasyon döngüsü. |
| `/oh-my-codex:deep-interview` skill | Belirsiz araştırma hedeflerinin test edilebilir hipotezlere Sokratik netleşmesi. |
| OMX orkestrasyon skill'leri (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Analiz koşumları, literatür taramaları, mutlaka bitirilmesi gereken revizyonlar için multi-iteration / paralel / consensus orkestratörler. 5 uygulamalı tarif için [`wiki/With-OMX.md#recipes--pairing-omxr-with-omc`](wiki/With-OMX.md#recipes--pairing-omxr-with-omc). |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP araçları | Literature wiki / hipotez register / deney koşum registry / stateful Python REPL. |

OMX'yi Codex marketplace üzerinden yan yana kurun ya da `npm i -g oh-my-codex`. Tam mapping: [`wiki/With-OMX.md`](wiki/With-OMX.md) + [`wiki/OMX-Tool-Reference.md`](wiki/OMX-Tool-Reference.md)

## Conventions (contributors)

- Ajanlar, skill'ler, komutlar için **kebab-case** dosya adları
- Her ajan / skill / komutta **YAML frontmatter** zorunlu (`name`, `description`, opsiyonel `model` / `color` / `memory`)
- `agents/`, `commands/`, `skills/`, `templates/`, `hooks/` veya üst düzey docs'ta **PII yok** — kurumlar, danışmanlar, gerçek subject ID'leri, email'ler, hedef dergi adları, mutlak yollar. Alan-özel içerik yalnızca `examples/<field>/` altında.
- Tüm ajanlarda **English-first** dil direktifi (AGENTS.md'de override etme deseni)

Tam contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — [LICENSE](LICENSE) görün.
