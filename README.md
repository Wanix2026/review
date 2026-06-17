# Review

A Claude Code skill for systematically organizing medical course review materials. Extracts knowledge from syllabi, teaching calendars, lecture slides, exam guides, and question banks, producing structured review notes backed by source attribution and cross-validated against three independent sources.

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

## Usage

Invoke within Claude Code:

```
/review /path/to/course-directory
```

Or describe naturally: "Help me organize review materials for this course" — the skill loads automatically.

### Dual Mode

| Condition | Behavior |
|-----------|----------|
| User provides question types and exam format | Type-driven output with structured sections for each question type |
| No question types provided (default) | Pure knowledge organization — no question type labels, no dedicated terminology sections |

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
