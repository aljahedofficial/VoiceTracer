# VoiceTracer Requirements & Scope

**Project**: VoiceTracer  
**Thesis**: "The Monolingualism of the Machine: Stylistic Homogenization in L2 Academic Writing"  
**Date**: February 2026  
**Status**: Phase 1 - Planning

---

## 1. Project Objective

Develop a Streamlit web application that measures and documents voice loss when L2 writers use AI editing tools. The app enables learners and educators to:
- Compare original vs. AI-edited text
- Quantify stylistic changes via research-backed metrics
- Visualize homogenization patterns
- Export publication-ready reports and research data

---

## 2. Core Research Questions Addressed

1. How does AI editing affect L2 learner writing characteristics?
2. Can we quantify stylistic differences between human and AI-edited text?
3. What linguistic markers indicate AI involvement?
4. How can L2 learners preserve voice while improving grammar?

---

## 3. Success Criteria

### Functional Requirements
- [x] Accept text input (paste, file upload: TXT, DOCX, PDF)
- [x] Calculate 4 core metrics + AI-ism detection
- [x] Display side-by-side comparison with change indicators
- [x] Generate interactive visualizations (radar, bar, diff)
- [x] Export to 8+ formats (PDF, DOCX, XLSX, PPTX, PNG, ZIP, CSV, JSON)
- [x] Auto-save every 30 seconds
- [x] Session recovery on reload
- [x] Responsive design (desktop, tablet, mobile)

### Quality Requirements
- Metric accuracy parity with manual calculation ±2%
- WCAG 2.1 AA accessibility compliance
- Export file integrity checks
- Performance: page load < 3s, metric calc < 2s

### Research Requirements
- Metrics align with thesis methodology
- Benchmark data for comparison
- Research-grade CSV/JSON exports
- Metadata & citation support

---

## 4. Metrics Specification

### Core Metrics (Required)

#### 1. Burstiness Index
- **Formula**: `SD(sentence_lengths) / mean(sentence_lengths)`
- **Range**: 0–3 (normalized)
- **Interpretation**: 
  - Low (< 0.8): Machine-like uniformity
  - High (> 1.5): Human-like variation
- **Why**: AI smooths sentence length variation

#### 2. Lexical Diversity (MTLD or TTR)
- **Formula**: Mean Type-Token Ratio or MTLD
- **Range**: 0–1
- **Interpretation**:
  - < 0.4: Low diversity (formulaic)
  - > 0.6: High diversity (varied vocab)
- **Why**: AI repeats common academic phrases

#### 3. Syntactic Complexity
- **Components**:
  - Average sentence length (words/sent)
  - Subordination ratio (subordinate clauses / total clauses)
  - Modifier density (modifiers / total tokens)
- **Interpretation**:
  - Complex: diverse structure
  - Simple: repetitive patterns
- **Why**: AI simplifies for clarity

#### 4. AI-ism Frequency
- **Categories**:
  - Opening hedges: "It is important to note that..."
  - Closing phrases: "In conclusion...", "To summarize..."
  - Formulaic connectors: "delve into", "in light of", "moreover"
  - Transition patterns: "Furthermore, it is evident..."
- **Scoring**: Likelihood 0–100 per category
- **Why**: Detects AI-generated phrases

### Supplementary Metrics (Optional)
- Passive voice ratio
- Readability (Flesch-Kincaid, CEFR)
- Rare word ratio
- Collocation patterns

---

## 5. UI/UX Workflow

### 4-Step Dashboard

**Step 1: Input Panel**
- Text areas (original + edited side-by-side)
- Upload: TXT, DOCX, PDF
- Sample loader (demo texts)
- Word count & quick stats

**Step 2: Metrics Dashboard**
- Quick summary (metric cards with gauges)
- Detailed explanations ("What it is", "Why it matters", "Why it changed")
- Benchmark comparison
- Interactive expandable sections

**Step 3: Visual Analysis**
- 6-axis radar chart (original vs. edited)
- Bar chart comparison
- Side-by-side text diff with syncing
- Time-series (for multiple analyses)

**Step 4: Report Generation**
- Format selection: PDF, DOCX, XLSX, PPTX, PNG, ZIP, CSV, JSON
- Customization (branding, sections, metrics to include)
- Download management
- Email/share options (future)

### Navigation & Layout
- **Sidebar**: Logo, file management, nav tabs, session history, help
- **Main content**: 4-step panels with progress indicator
- **Responsive**:
  - Desktop (>1024px): Full layout
  - Tablet (768–1024px): Collapsible sidebar
  - Mobile (<768px): Hamburger menu, single column

---

## 6. Export Formats & Specs

| Format | Size | Purpose | Features |
|--------|------|---------|----------|
| **PDF** | 2–3 MB | Academic report | 17 pages, charts, branding, print-ready |
| **DOCX** | 1–1.5 MB | Editable report | Track changes, comments, hyperlinks |
| **XLSX** | 512 KB–1 MB | Data analysis | 5 sheets, formulas, charts, color-coded |
| **PPTX** | 2–3 MB | Presentation | 9 slides, speaker notes, editable |
| **PNG** | 600×400 to 2400×1600 | Figures for papers | Individual charts, transparent bg |
| **ZIP** | Bundles | Publication | Charts (PNG/SVG/PDF), README, docs |
| **CSV** | 50–200 KB | Statistical analysis | SPSS/R compatible, normalized data |
| **JSON** | 50–100 KB | Advanced analysis | Structured metadata, benchmarks |

---

## 7. Data Model

### Core Entities

```
DocumentPair
├── id: UUID
├── original_text: str
├── edited_text: str
├── original_metadata: {word_count, char_count, created_at}
├── edited_metadata: {word_count, char_count, edited_at}
└── created_at: datetime

Metrics
├── metric_id: UUID
├── doc_pair_id: UUID (FK)
├── original_metrics: {burstiness, lex_div, syn_complex, ai_ism}
├── edited_metrics: {burstiness, lex_div, syn_complex, ai_ism}
├── deltas: {changes as %, interpretation}
├── calculated_at: datetime
└── method_version: str (for reproducibility)

AIismInventory
├── doc_pair_id: UUID (FK)
├── phrase: str
├── category: enum (opening, closing, connector, transition)
├── occurrence_count: int
├── likelihood: 0–100
└── context_snippets: [str]

Benchmark
├── benchmark_id: UUID
├── name: str (e.g., "Native Speaker Average")
├── metric_baselines: {burstiness, lex_div, syn_complex, ai_ism}
├── description: str
└── source: str (e.g., "Agarwal et al. 2024")

Session
├── session_id: UUID
├── user_id: str (anonymized)
├── document_pairs: [UUID]
├── auto_save_interval: int (seconds, default 30)
├── last_activity: datetime
└── recovery_data: {state_snapshot}
```

---

## 8. Technology Stack

- **Framework**: Streamlit (rapid prototyping, no frontend scaffolding)
- **Analysis**: spaCy (NLP), NLTK (tokenization), pandas (data manipulation)
- **Visualization**: Plotly (interactive charts), matplotlib (static exports)
- **Export**: python-docx, openpyxl, reportlab (PDF), python-pptx
- **Storage**: SQLite (session/benchmark data, deployable with app)
- **Deployment**: Streamlit Cloud (free, no auth needed for prototype)

---

## 9. Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| 1. Planning & Scope | 0.5 day | Requirements, data model, success metrics |
| 2. Architecture & Model | 0.5 day | Data schema, metric formulas, benchmarks |
| 3. Core Engine | 1–2 days | Text parsing, metric calculation, normalization |
| 4. UI Workflow | 2 days | 4-step dashboard, sidebar, responsiveness |
| 5. Visualizations | 1 day | Charts, diffs, interactive components |
| 6. Exports | 2 days | All 8 formats, metadata, integrity checks |
| 7. Persistence | 0.5–1 day | Auto-save, session recovery |
| 8. QA & Validation | 1 day | Metric parity, exports, a11y, performance |
| 9. Deploy & Docs | 0.5 day | Streamlit Cloud, user guide, thesis notes |
| **TOTAL** | **~8–10 days** | Thesis-ready prototype |

---

## 10. Out of Scope (for v1)

- User authentication (will use anonymized sessions)
- Multi-user collaboration
- Custom metric configuration
- API endpoints
- Mobile app
- Institutional integration

---

## 11. Assumptions & Dependencies

- **spaCy English model** pre-downloaded (en_core_web_sm)
- **Internet connectivity** for Streamlit Cloud deployment
- **File upload**: Supports TXT, DOCX, PDF via python-docx and PyPDF2
- **Benchmarks**: From Agarwal et al. 2024 and thesis data

---

## 12. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Metric accuracy issues | Validate against manual analysis on 10 sample texts |
| Export file corruption | Test all formats before deployment |
| Performance (large texts) | Implement text truncation at 5000 words |
| Accessibility gaps | Run WAVE/Axe scan before launch |
| Session loss | Implement SQLite with recovery snapshots |

---

**Approval**: Requirements finalized & ready for Phase 2  
**Next**: Architecture & data model design
