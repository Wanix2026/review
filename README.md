# Review

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-6e47ff)](https://claude.ai/code)
[![3 courses validated](https://img.shields.io/badge/validated-3%20courses-success)](#provenance)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![scripts](https://img.shields.io/badge/scripts-6%20Python%20files-306998)](scripts/)

Turns syllabi and lecture slides into exhaustive, source-attributed review notes — every claim traceable, every value verbatim, nothing fabricated. Designed for medical students, validated across surgery, preventive medicine, and anesthesiology.

## Demo

```
$ /review ~/Desktop/HMC/大三下/外科

Phase 0 · 扫描 + 分类
  大纲 ✅  2023级-《外科学总论》教学大纲.pdf
  日历 ✅  嵌入大纲各章的学时分配表
  PPT   8 files covering 9 theory chapters
  分类置信度: 9/9 auto-approved (≥85%)

Phase 1 · 提取 [██████████] 9/9 ✅
  PDF: 01绪论 02休克 03感染... → 175K chars
  PPTX: 水电解质 创伤 营养... → 81K chars

Phase 2 · 交叉验证
  Ch1-Ch9: ✅ confirmed
  Ch10 综合实训: — practice-only, excluded
  0 fatal gaps · 0 warnings

Phase 3 · 生成
  → 外科学总论-复习笔记.md  (exhaustive extraction, 83 h3 sections)
  → 外科学总论-复习笔记.html (sidebar TOC with search, print-ready)
  → 外科学总论-记忆卡.anki.csv
```

**Output preview** (Surgery, Chapter 6 — Surgical Infection):

> ### 破伤风  
> | 项目 | 内容 |
> |------|------|
> | 病原 | **破伤风梭菌** (G⁺ anaerobic bacillus), produces **tetanospasmin** |
> | 潜伏期 | Typically **6–10 days** (shorter = more severe) |
> | 典型表现 | **Risus sardonicus** → **Trismus** → **Opisthotonos** → Respiratory failure |
> | 预防 | Debridement + active immunization (toxoid) + passive: **TAT 1500 IU** or **TIG 250–500 IU** |
> | 治疗 | Metronidazole + TAT/TIG + Diazepam + Tracheostomy if needed |
>
> **可能的考点**  
> PPT末页思考题 → 破伤风的临床表现和防治（掌握级）  
> 大纲双重点 → 脓毒症概念及qSOFA三项快速筛查

## Provenance

This skill was designed and iterated through real clinical medicine exam preparation. Three courses validated:

- Surgery (考查课, 9 chapters, 8 slide decks) — student reported full exam coverage
- Preventive Medicine (考试课, 6 chapters, 13 slide decks + independent calendar) — matched original notes
- Anesthesiology (考查课, 10 chapters, 5 slide decks + review guide) — first-pass generation

## Design Philosophy

- **Syllabus as single source of truth** — every output claim must trace back to a syllabus line
- **Three-source cross-validation** — syllabus, teaching calendar, and lecture slides compared chapter by chapter; discrepancies explicitly annotated rather than silently resolved
- **No content generation** — organize, extract, and classify only; never fabricate knowledge points
- **Explicit gap annotation** — missing materials are clearly marked and visually distinct from confirmed content
- **Source attribution** — every chapter traces back to its originating files; numerical values are transcribed verbatim

## Installation

```bash
git clone https://github.com/Wanix2026/review.git ~/.claude/skills/review
pip3 install python-pptx python-docx openpyxl pdfminer.six
```

Restart Claude Code. The skill loads automatically.

## Usage

### Generate review notes

Organize your course folder:

```
外科学/
├── 大纲.pdf          ← syllabus (required)
├── 课件/             ← lecture slides
│   ├── 01绪论.pdf
│   ├── 02休克.pdf
│   └── ...
└── 复习重点.docx      ← exam guide (optional)
```

In Claude Code:

```
/review ~/Desktop/外科学
```

The skill scans, classifies, extracts, cross-validates, and generates. Confirm once at the start, then wait. Output:

```
外科学/
├── 外科学-复习笔记.md       ← Markdown source
├── 外科学-复习笔记.html     ← sidebar TOC + search + print
├── 外科学-记忆卡.anki.csv   ← Anki import
└── 外科学-思维导图.md       ← Mermaid chapter map
```

### Extract question banks

**From PDF/Word files**: drop the file into the course folder. The skill auto-detects, cleans (strips explanations, student answers, separators), and exports `.docx` for import into 考试宝 or other flashcard apps.

**From web platforms (人卫/学习通)**: open the exam page in your browser, press F12 to open the Console, paste this extraction script:

```javascript
// Dump all visible text from the exam page
console.log(document.body.innerText);
```

Copy the Console output, paste it into Claude Code with: "Clean this question bank — keep only question type, stem, options, and correct answer. Remove explanations, student answers, and separators. Export as .docx."

### Dual mode

| Condition | Behavior |
|-----------|----------|
| Question types provided | Structured sections per question type (A1/A2/B1/名词解释/简答) |
| No types given (default) | Pure knowledge organization — no type labels |

## Pipeline

```
Phase 0 — File Discovery & Classification
  Directory scan, automatic file-type classification
  Content-based validation (12 Chinese filename aliases)
  Guard check: syllabus and teaching calendar must exist
  Four-layer chapter matching (number → content sample → keyword → calendar bridge)
  Environment dependency pre-check

Phase 1 — Full Extraction (incremental, cached)
  SHA-256 file fingerprinting, incremental mode
  Format diagnosis: PDF (text/scanned/encrypted), DOCX, DOC, PPTX, XLSX
  Post-extraction integrity check with garbled text detection
  Structured cache at .course-cache/ with JSON Schema constraints
  Resume-from-breakpoint support

Phase 2 — Three-Source Cross-Validation
  16-state decision table (syllabus × calendar × slides)
  Four-tier gap classification with actionable responses
  Conflict resolution: calendar priority, explicit evidence preservation
  Maximum 2 feedback rounds before forced output

Phase 3 — Review Note Generation
  Fixed three-section chapter template (requirements → content → likely exam topics)
  Content depth enforcement: verbatim numerical transcription, step-by-step preservation
  Mandatory post-generation completeness audit with coverage report
  Source attribution on every chapter
  HTML output with sidebar TOC, scroll-spy, mobile responsive, print stylesheet
```

## Output Files

```
course-directory/
├── .course-cache/                   # Structured extraction cache
├── [Course]-复习笔记.md             # Markdown source
├── [Course]-复习笔记.html           # HTML with TOC and section navigation
├── [Course]-复习笔记.pdf            # Print-optimized PDF (optional)
├── [Course]-思维导图.md             # Mermaid chapter mindmap
├── [Course]-记忆卡.anki.csv         # Anki flashcard import
└── [Course]-题库导出.docx           # Question bank export (optional)
```

## Skill Structure

```
.claude/skills/review/
├── SKILL.md                         # Full workflow specification
├── install.sh                       # One-command environment setup
├── README.md
├── scripts/
│   ├── extract.py                   # Unified extraction (6 formats)
│   ├── verify.py                    # Post-extraction integrity check
│   ├── to_html.py                   # Markdown to HTML with sidebar TOC
│   ├── anki.py                      # Anki CSV flashcard export
│   └── mindmap.py                   # Mermaid mindmap generator
└── references/
    ├── template.html                # HTML output template
    ├── schema.md                    # JSON Schema for cache files
    └── checklist.md                 # Quality assurance checklist
```

## Accuracy Guarantees

The skill enforces strict accuracy constraints:

- All knowledge points must have verifiable source file origins
- Numerical values transcribed verbatim — no rounding, no format changes, no unit dropping
- Procedural steps listed individually — merging or summarizing is forbidden
- Comparison tables preserved in table form — never flattened to prose
- Syllabus sub-items tracked for full coverage — any item below 90% coverage triggers re-extraction
- Post-generation audit runs automatically, with results appended to output

## Capabilities

| Capability | Description |
|------------|-------------|
| Format support | PDF (text layer, scanned, encrypted), PPTX, DOCX, DOC, XLSX |
| Intelligent classification | Filename + content dual validation, 12 Chinese alias patterns |
| Three-source validation | 16-state decision table with explicit conflict annotation |
| Incremental updates | SHA-256 fingerprinting with fast update mode |
| Resume from breakpoint | Extraction state persisted; restart from interruption point |
| Multi-project tracking | Global project registry remembering per-course configuration |
| Anki export | Auto-extract comparison tables, terminology, and numerical facts to CSV |
| Mindmap generation | Mermaid chapter structure visualization |
| Question bank processing | Web platform extraction, cleaning, and .docx export |

## Dependencies

| Tool | Purpose |
|------|---------|
| pdf2txt (pdfminer.six) | PDF text extraction |
| python-pptx | PPTX slide text extraction |
| python-docx | Word document processing |
| openpyxl | Excel spreadsheet processing |

## License

MIT
