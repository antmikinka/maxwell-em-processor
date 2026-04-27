# Archive Manifest

**Created:** 2026-04-26
**Purpose:** Consolidation of legacy exploration artifacts from project root into organized archive directories. This cleanup removes iteration history and exploratory documentation that accumulated during the TOC extraction pipeline development phase, leaving a clean baseline for ongoing production work.

---

## archive/documentation/ (9 files)

Historical planning, analysis, and reference documents produced during the TOC extraction and pipeline design exploration phase. These are retained for historical reference but are no longer part of the active project documentation set.

| File | Description | Reason Archived |
|------|-------------|-----------------|
| `PROJECT_SUMMARY.md` | Original project overview and scope document | Superseded by ARCHITECTURE.md and USAGE_GUIDE.md |
| `CONVO-FUNCTIONALITY-PLANS.md` | Conversation-derived feature planning notes | Exploratory planning; completed |
| `DATA_SCIENCE_ANALYSIS.md` | Data analysis of processed volume structure | Exploratory analysis; completed |
| `IMPLEMENTATION_PLAN.md` | Detailed implementation roadmap (102KB) | Implementation phase complete |
| `Enhanced_Maxwell_TOC_Solution_Report.md` | Report on enhanced TOC extraction approach | Single-use solution report |
| `MAXWELL_TOC_ACCESS_SCHEMA.md` | Schema documentation for TOC access patterns | Referenced during development; superseded by code |
| `MAXWELL_TOC_EXTRACTOR_GUIDE.md` | User guide for TOC extractor scripts | Extractors archived; guide obsolete |
| `indexes-json.md` | JSON index format reference | Referenced during development; superseded by code |
| `MAXWELL_COMPLETE_TREATISE_SUMMARY.txt` | Plain-text treatise summary | Legacy artifact from initial processing |

## archive/legacy-scripts/extractors/ (9 files)

Multiple iterations of TOC extraction scripts produced during the iterative development cycle. These represent sequential refinements and debugging attempts. The current production pipeline in `src/` and `main_pipeline.py` supersedes all of these.

| File | Notes |
|------|-------|
| `enhanced_maxwell_toc_extractor.py` | Initial enhanced extractor |
| `enhanced_maxwell_toc_extractor_final.py` | Final enhanced variant |
| `enhanced_maxwell_toc_extractor_working.py` | Working variant during development |
| `final_enhanced_extractor.py` | Standalone final extractor build |
| `working_enhanced_extractor.py` | Working iteration |
| `working_enhanced_maxwell_extractor.py` | Working Maxwell-specific variant |
| `maxwell_toc_extractor.py` | Original Maxwell TOC extractor |
| `maxwell_toc_extractor_fixed.py` | Fixed version of original extractor |
| `maxwell_toc_extractor_numbered.py` | Numbered output variant |

## archive/legacy-scripts/mathpix/ (2 files)

Direct Mathpix API integration scripts. Replaced by the structured `src/mathpix_processor.py` module within the production pipeline.

| File | Notes |
|------|-------|
| `mathpix_api_caller.py` | Basic Mathpix API caller |
| `mathpix_enhanced.py` | Enhanced Mathpix integration with retries |

## archive/legacy-scripts/diagnostics/ (5 files)

Ad-hoc diagnostic and sanity-check scripts used during Volume 1 and Volume 2 processing validation.

| File | Notes |
|------|-------|
| `check_p204.py` | Page 204 validation check |
| `check_p478.py` | Page 478 validation check |
| `check_v2_p4_chapters.py` | Volume 2 Part 4 chapter validator |
| `check_v2_range.py` | Volume 2 range validator |
| `test_mathpix_api.py` | Mathpix API connectivity test |

## archive/legacy-scripts/splitters/ (4 files)

Volume splitting scripts used to divide processed outputs into Part-level chunks. These were one-off execution scripts used during initial volume processing.

| File | Notes |
|------|-------|
| `split_part_1_final.py` | Volume 1 Part 1 splitter |
| `split_part_2_final.py` | Volume 1 Part 2 splitter |
| `split_volume_2_part_3.py` | Volume 2 Part 3 splitter |
| `split_volume_2_part_4.py` | Volume 2 Part 4 splitter |

---

## Summary Statistics

| Category | File Count |
|----------|-----------|
| Documentation | 9 |
| Extractor Scripts | 9 |
| Mathpix Scripts | 2 |
| Diagnostic Scripts | 5 |
| Splitter Scripts | 4 |
| **Total** | **29** |

## Rationale

These artifacts accumulated during the exploratory TOC extraction phase (Volumes 1 and 2 processing). Keeping them in the project root created noise that obscured the active production codebase (`src/`, `config/`, `main_pipeline.py`). Archiving them preserves historical context while establishing a clean, navigable project structure for the GAIA pipeline implementation phase.
