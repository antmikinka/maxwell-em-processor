# Licensing Guide and Decision Record

This document explains the licensing structure of this repository: what
rights are held, which options were considered, what was overclaimed in
an earlier draft, and what the files now grant.

The grant is in [LICENSE](LICENSE). If this document and LICENSE ever
disagree, LICENSE controls. Third-party attribution is in [NOTICE](NOTICE).
Official full texts are in [LICENSES/MIT.txt](LICENSES/MIT.txt) and
[LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt). Courtesy citation is
in [CITATION.cff](CITATION.cff).

This file is original project documentation and is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## 1. The Situation

This project is a Maxwell Electromagnetic Theory Processor — a Python
pipeline that OCRs James Clerk Maxwell's *A Treatise on Electricity and
Magnetism* (1873) using the Mathpix API, then organizes the extracted
content into a hierarchy of Volumes, Parts, Chapters, and Articles.

Licensing it is not a one-line decision. The tree contains materials
with different owners and different appropriate license frameworks. A
license can only grant rights the licensor actually holds.

This is **split licensing** (different files, different grants). It is
not dual licensing. Dual licensing usually means the *same* work is
offered under two licenses at once.

---

## 2. The Five Types of Material

| # | Type | What it is | Where it lives | Who holds rights | Appropriate treatment |
|---|------|-----------|----------------|------------------|-----------------------|
| 1 | **Original code** | Python pipeline, processors, config, scripts | `src/`, `config/`, `main_pipeline.py`, `archive/legacy-scripts/` | Anthony Mikinka | Software license (MIT) |
| 2 | **Original documentation and analysis** | Authored prose: guides, architecture, this record, archive analyses | `README.md`, `ARCHITECTURE.md`, `USAGE_GUIDE.md`, `LICENSING.md`, `archive/ARCHIVE_MANIFEST.md`, `archive/documentation/` | Anthony Mikinka | Content license (CC BY 4.0) |
| 3 | **Vendored SDK** | Fork of Mathpix's Python SDK | `mpxpy/` | Mathpix, Inc. (original); Anthony Mikinka (modifications) | Inbound MIT — cannot be relicensed |
| 4 | **Public-domain source and mechanical extracts** | Maxwell's 1873 text; OCR/typesetting of that text; factual TOC and article indexes | Referenced in input/output; `input/v3 - Vol * - README.md`; `maxwell_article_index.json` when present | Nobody (public domain). No copyright is claimed. | No copyright license |
| 5 | **Other inbound files** | Non-Maxwell source documents that may exist locally | `input/` PDFs other than the 1873 Treatise (gitignored) | Original publishers / authors | Not this project's to grant |

No single license honestly covers all five.

---

## 3. The Constraints

### Software licenses vs content licenses

Software licenses (MIT, Apache 2.0, BSD) are designed for executable
code. They are what developers, package managers, and institutions
expect for `src/`.

Content licenses (the Creative Commons family) are designed for
documents, papers, and other expressive works. They are the usual
choice for scholarly prose.

Using a content license on Python code is actively harmful: it is
ambiguous about source vs compiled form, and FSF, OSI, Debian, and
Creative Commons themselves advise against CC licenses on software.

### The inbound Mathpix constraint

`mpxpy/` is a vendored fork of Mathpix's Python SDK, originally
licensed under MIT by Mathpix, Inc.

- You cannot relicense Mathpix's code to CC BY 4.0 or anything else.
- Their copyright and permission notices must be preserved.
- All-CC-BY on the whole tree is therefore impossible.

That constraint eliminates a single CC BY grant for the repository.
It does **not** force a second license on original documentation.
All-MIT on *original* work, plus a NOTICE for Mathpix, remains
legally possible. Choosing CC BY for original docs is a values
choice (attribution on scholarly writing), not a legal necessity.

### The Maxwell constraint

Maxwell's original 1873 text is public domain. No one can copyright
it. A CC BY 4.0 grant in this project does **not** claim Maxwell's
words.

Mechanical OCR, typesetting, and factual transcription of Maxwell's
own article titles, numbers, and page numbers do not create a new
copyright in those words or facts. Claiming CC BY on that material
would be an overclaim.

Original commentary, architecture writing, usage guides, and other
authored analysis *can* honestly be CC BY 4.0.

---

## 4. The Options We Considered

### Option A: All MIT

Apply MIT to all original work. Preserve Mathpix MIT. Declare Maxwell
public domain.

| Pros | Cons |
|------|------|
| One license on original work, easy to explain | Documentation and analysis can be reused without a license-level attribution duty |
| Universally understood by developers | Treats scholarly writing the same as a utility function |
| Compatible with `mpxpy/` | |

**Verdict:** Legally clean. A respectable second choice. Weaker than
needed on original prose.

### Option B: All CC BY 4.0

Apply CC BY 4.0 to everything.

| Pros | Cons |
|------|------|
| Strong attribution on everything | **Impossible** for `mpxpy/` |
| Feels culturally right for a scholarly modernization | CC licenses are not software licenses |
| | PyPI, package managers, and many institutional policies do not handle CC on code |
| | FSF, OSI, and Debian advise against CC for software |
| | Would still need a carve-out for `mpxpy/` |

**Verdict:** Not viable.

### Option C: Split — MIT for code + CC BY 4.0 for original docs (CHOSEN)

Split by material type. Original code gets MIT. Original
documentation and analysis get CC BY 4.0. Vendored SDK keeps inbound
MIT. Maxwell and mechanical extracts stay public domain / no claim.

| Pros | Cons |
|------|------|
| Right license for each material type | More than one license name to mention |
| Attribution on authored scholarly writing | GitHub will not detect a single license badge cleanly |
| Code stays frictionless for developers | |
| Compatible with `mpxpy/` | |
| Same pattern as Jupyter (OSI code + CC BY docs) and open editions | |

**Verdict:** The correct professional choice, **if and only if** the
CC BY bucket is limited to original authored writing.

### What was overclaimed, and what changed

An earlier draft of LICENSE and the file map applied CC BY 4.0 to
"any extracted/processed Maxwell content," including structured JSON,
LaTeX, organized output, `maxwell_article_index.json`, and the input
volume README files.

That contradicted the Maxwell constraint in section 3. Those files
are Maxwell's words and facts, or mechanical reproductions of them.

On 2026-08-18 the grant was narrowed so that LICENSE, this record,
and the README say the same thing:

- CC BY 4.0 covers original authored documentation and analysis only.
- Maxwell's text, mechanical OCR, and factual indexes are public
  domain / no copyright claimed.
- Other inbound files are not licensed by this project.

---

## 5. License Map (File-by-File)

### MIT — original code (Anthony Mikinka)

| Path | Description |
|------|-------------|
| `main_pipeline.py` | Main 3-stage pipeline orchestrator |
| `src/circuit_breaker.py` | Circuit breaker for API resilience |
| `src/content_organizer.py` | Content classification and organization |
| `src/data_models.py` | Pydantic data models |
| `src/health_monitor.py` | Pipeline health monitoring |
| `src/logger_config.py` | Logging configuration |
| `src/mathpix_processor.py` | Mathpix OCR processing engine |
| `src/retry_handler.py` | Retry logic with backoff |
| `src/simple_mode_organizer.py` | Simplified processing mode |
| `src/toc_analyzer.py` | Table of contents parser |
| `src/utils.py` | Utility functions |
| `config/__init__.py` | Config package init |
| `config/config.py` | Settings via pydantic-settings |
| `config/config.txt` | Configuration template |
| `archive/legacy-scripts/**` | Archived one-off and diagnostic scripts |
| `archive/legacy-scripts/README.md` | License notice for the archived scripts tree |

### CC BY 4.0 — original documentation and analysis (Anthony Mikinka)

| Path | Description |
|------|-------------|
| `README.md` | Project overview and setup guide |
| `ARCHITECTURE.md` | System architecture with diagrams |
| `USAGE_GUIDE.md` | Detailed usage instructions |
| `LICENSING.md` | This document |
| `archive/ARCHIVE_MANIFEST.md` | Archive inventory |
| `archive/documentation/README.md` | License notice for the archived docs tree |
| `archive/documentation/CONVO-FUNCTIONALITY-PLANS.md` | Functionality analysis |
| `archive/documentation/DATA_SCIENCE_ANALYSIS.md` | Data science assessment |
| `archive/documentation/Enhanced_Maxwell_TOC_Solution_Report.md` | TOC solution report |
| `archive/documentation/IMPLEMENTATION_PLAN.md` | Implementation roadmap |
| `archive/documentation/MAXWELL_COMPLETE_TREATISE_SUMMARY.txt` | Treatise summary (original writing; quoted Maxwell remains PD) |
| `archive/documentation/MAXWELL_TOC_ACCESS_SCHEMA.md` | TOC schema doc |
| `archive/documentation/MAXWELL_TOC_EXTRACTOR_GUIDE.md` | Extractor guide |
| `archive/documentation/PROJECT_SUMMARY.md` | Project summary |
| `archive/documentation/indexes-json.md` | Index documentation |

Quoted Maxwell in any of those files remains public domain. Only the
original surrounding writing is CC BY 4.0.

### MIT — vendored, inbound (Mathpix + modifications)

| Path | Description |
|------|-------------|
| `mpxpy/**` | Vendored fork of [Mathpix Python SDK](https://github.com/Mathpix/mathpix-python) |

See `mpxpy/LICENSE.txt` and [NOTICE](NOTICE):

```
Copyright (c) 2023 Mathpix, Inc. (original mpxpy SDK)
Copyright (c) 2025 Anthony Mikinka (modifications and vendored fork)
```

### Public domain / no copyright claimed

| Material | Note |
|----------|------|
| Maxwell's original 1873 text | Published 1873; author died 1879. Public domain worldwide. |
| `input/15773-A Treatise On Electricity And Magnetism Vol-i.pdf` | Public-domain scan of Volume I. Published in this repo. |
| `input/15774-A Treatise On Electricity And Magnetism Vol-ii.pdf` | Public-domain scan of Volume II. Published in this repo. |
| `MAXWELL_VOLUME_1_MASTER_OUTPUT/` | Volume I edition: `volume_1_ocr.md`, chapter JSON, reports, and `RAW_OUTPUTS/`. No copyright claimed. |
| `MAXWELL_VOLUME_2_MASTER_OUTPUT/` | Volume II edition, including `RAW_OUTPUTS/`. No copyright claimed. |
| `Maxwell_TOC_Fixed/` | Intermediate failed TOC split of Maxwell JSON. Published for inspection. No copyright claimed. |
| Mechanical OCR / typesetting of that text | Markdown, LaTeX, HTML, JSON, zip, and similar reproductions of Maxwell. Local-only trees such as `output/` and `Maxwell_TOC/` are the same class when they reproduce Maxwell; they are not published. |
| `maxwell_article_index.json` | Factual `{art, title, page}` transcription of Maxwell. |
| `input/v3 - Vol 1 - README.md` | Transcription of Maxwell's volume 1 table of contents. |
| `input/v3 - Vol 2 - README.md` | Transcription of Maxwell's volume 2 table of contents. |

Citing this project as the edition you used is welcome as scholarly
courtesy. It is not a copyright condition on Maxwell.

### Other inbound files — not licensed by this project

| Material | Note |
|----------|------|
| `input/*.pdf` of the 1873 Treatise | Public domain scans. The two Treatise PDFs are published in this repo. |
| Any other `input/` document (for example a modern textbook chapter) | Keeps its original copyright. Must not be committed, published, or described as MIT, CC BY, or public domain project content. |

### License text files (not a separate grant)

| Path | Description |
|------|-------------|
| `LICENSE` | Controlling grant and file-class map |
| `LICENSES/MIT.txt` | Official MIT License text |
| `LICENSES/CC-BY-4.0.txt` | Official CC BY 4.0 legal code |
| `CITATION.cff` | Courtesy citation for the software and edition |
| `NOTICE` | Inbound third-party attribution |

These files do not add rights. They publish the texts and the map.

### Not in the repository (gitignored)

| Material | Reason |
|----------|--------|
| `.env` (API credentials) | Secrets — never committed |
| `output/` | Local pipeline cache, logs, and non-Maxwell trial OCR (including the modern textbook chapter) |
| `Maxwell_TOC/`, `Enhanced_Maxwell_TOC/` | Earlier local TOC attempts / logs |
| `MAXWELL_VOLUME_*_MASTER_OUTPUT/volume_*_direct_result.json` | Duplicate root-level API blobs (`RAW_OUTPUTS/` is published) |
| `chroma_data/` | Runtime vector store |
| `*.log` files | Operational logs |
| `venv/` | Virtual environment |
| `config/total-usage-data.csv` | Operational telemetry |
| Other `input/*.pdf` | Third-party or local-only sources — not published |

---

## 6. Why This Split

1. **The material types are genuinely different.** A circuit breaker
   module and an architecture document serve different audiences and
   belong under different licenses.

2. **Attribution belongs on original scholarly writing.** CC BY 4.0
   is the honest license for `ARCHITECTURE.md`, `USAGE_GUIDE.md`,
   this record, and the archive analyses.

3. **Attribution does not belong on Maxwell.** The purpose of the
   project is to make a public-domain scientific treatise more usable.
   Enclosing OCR of that treatise under CC BY would do the opposite.

4. **Friction matters for the code.** Developers expect MIT. Package
   managers expect an OSI license on `src/`.

5. **Inbound MIT must be preserved.** Mathpix's code stays MIT, with
   notices, in `mpxpy/LICENSE.txt` and `NOTICE`.

6. **All-MIT was available and was rejected for the docs layer only.**
   The Mathpix constraint does not force CC BY. We chose CC BY for
   original prose because that writing deserves a real attribution
   license.

---

## 7. What You Can Do

### With the original code (MIT)

- Use it, modify it, distribute it, sell it
- Include it in proprietary projects
- Keep the copyright notice in any copies

### With original documentation and analysis (CC BY 4.0)

- Share it, adapt it, build on it, including commercially
- Credit Anthony Mikinka, link to the license, and note changes

### With the vendored mpxpy (MIT — Mathpix inbound)

- Same MIT rights as above
- Keep Mathpix's copyright notice and Anthony's modification notice

### With Maxwell's original text and mechanical extracts

- Public domain. No copyright license applies.
- Citation of this project is courtesy, not a condition.

### With other inbound files

- This project grants no rights in them.
- Do not copy, publish, or relicense a modern third-party PDF from
  `input/` as if it were part of this repository.

---

## 8. Mixed files

If a future published edition mixes Maxwell's words with original
commentary, encoding notes, or analysis in one file:

- Maxwell's strings remain public domain
- Only the original commentary is CC BY 4.0
- The file should say so

Do not put a single CC BY banner on a blob that is mostly Maxwell.

---

## 9. References

| Item | Location |
|------|----------|
| Grant | [LICENSE](LICENSE) |
| Official MIT text | [LICENSES/MIT.txt](LICENSES/MIT.txt) |
| Official CC BY 4.0 legal code | [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt) |
| Courtesy citation | [CITATION.cff](CITATION.cff) |
| Third-party notices | [NOTICE](NOTICE) |
| MIT License | https://opensource.org/licenses/MIT |
| CC BY 4.0 | https://creativecommons.org/licenses/by/4.0/ |
| CC BY 4.0 legal code | https://creativecommons.org/licenses/by/4.0/legalcode |
| Mathpix Python SDK | https://github.com/Mathpix/mathpix-python |
| Creative Commons on software | https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software |
| FSF on CC licenses | https://www.gnu.org/licenses/license-list.html#ccby |

---

*First written: 2026-07-28*
*Grant narrowed (no CC BY on Maxwell extracts): 2026-08-18*
*Full legal texts and CITATION.cff added: 2026-08-18*
*Author: Anthony Mikinka*
