# Maxwell EM Theory Processor - System Architecture

## 📐 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐    ┌──────────────────┐   ┌──────────────────┐  │
│  │  Maxwell Vol 1   │    │  Maxwell Vol 2   │   │  TOC README      │  │
│  │     (PDF)        │    │     (PDF)        │   │     Files        │  │
│  └────────┬─────────┘    └────────┬─────────┘   └────────┬─────────┘  │
│           │                       │                       │             │
└───────────┼───────────────────────┼───────────────────────┼─────────────┘
            │                       │                       │
            └───────────┬───────────┘                       │
                        │                                   │
                        ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 1: OCR PROCESSING                            │
│                    (mathpix_processor.py)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │           Mathpix API Client                           │            │
│  │  • PDF → Text extraction                               │            │
│  │  • LaTeX equation recognition                          │            │
│  │  • Figure/diagram extraction                           │            │
│  │  • Markdown conversion                                 │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
│                       ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐            │
│  │          Caching & Logging System                      │            │
│  │  • Save all API responses                              │            │
│  │  • Log all requests/responses                          │            │
│  │  • No data loss guarantee                              │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
└───────────────────────┼─────────────────────────────────────────────────┘
                        │
                        ▼
            ┌──────────────────────┐
            │  Output: OCR Data    │
            │  • Page JSON files   │
            │  • Mathpix Markdown  │
            │  • Extracted figures │
            │  • Equations (LaTeX) │
            └──────────┬───────────┘
                       │
                       ├──────────────────────┐
                       │                      │
                       ▼                      ▼
┌─────────────────────────────────┐  ┌──────────────────────────────────┐
│   STAGE 2: TOC ANALYSIS         │  │   Parallel: Database Creation    │
│   (toc_analyzer.py)             │  │   (data_models.py)               │
├─────────────────────────────────┤  └──────────────────────────────────┘
│                                 │
│  ┌───────────────────────────┐ │
│  │  README File Parser       │ │
│  │  • Extract chapters       │ │
│  │  • Parse article numbers  │ │
│  │  • Map page ranges        │ │
│  └──────────┬────────────────┘ │
│             │                   │
│             ▼                   │
│  ┌───────────────────────────┐ │
│  │  Hierarchical Structure   │ │
│  │  Volume → Part → Chapter  │ │
│  │          → Article        │ │
│  └──────────┬────────────────┘ │
└─────────────┼───────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │  Output: TOC JSON    │
    │  • toc_structure.json│
    │  • Page mappings     │
    │  • Article index     │
    └──────────┬───────────┘
               │
               ├─────────────────┐
               │                 │
               ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STAGE 3: CONTENT ORGANIZATION                             │
│               (content_organizer.py)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         OpenRouter AI Classification                   │            │
│  │  • Analyze page content                                │            │
│  │  • Detect section headers                              │            │
│  │  • Identify article numbers                            │            │
│  │  • Determine chapter/part                              │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
│                       ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         Folder Structure Creation                      │            │
│  │  • Create TOC-based hierarchy                          │            │
│  │  • Organize pages by section                           │            │
│  │  • Link equations to articles                          │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
└───────────────────────┼─────────────────────────────────────────────────┘
                        │
                        ▼
            ┌──────────────────────┐
            │  Output: Organized   │
            │  • Folder hierarchy  │
            │  • Page metadata     │
            │  • Classification    │
            └──────────┬───────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STAGE 4: CODE GENERATION                                  │
│               (code_converter.py)                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         OpenRouter AI Code Generation                  │            │
│  │  • Analyze mathematical content                        │            │
│  │  • Generate NumPy/SciPy implementations                │            │
│  │  • Create SymPy symbolic math                          │            │
│  │  • Generate Matplotlib visualizations                  │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
│                       ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         Python Module Creation                         │            │
│  │  • core_equations.py                                   │            │
│  │  • visualizations.py                                   │            │
│  │  • tests/test_*.py                                     │            │
│  │  • Complete with docstrings & type hints               │            │
│  └────────────────────┬───────────────────────────────────┘            │
│                       │                                                 │
└───────────────────────┼─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FINAL OUTPUTS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Raw OCR    │  │  Organized   │  │  Generated   │  │  Database  │ │
│  │    Data      │  │   Content    │  │    Code      │  │   Files    │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤ │
│  │ • JSON files │  │ • Folders by │  │ • .py modules│  │ • TOC JSON │ │
│  │ • Markdown   │  │   TOC struct │  │ • Tests      │  │ • Metadata │ │
│  │ • Images     │  │ • Metadata   │  │ • Docstrings │  │ • Stats    │ │
│  │ • Equations  │  │ • Links      │  │ • Type hints │  │ • Mappings │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
PDF Input
   │
   ├─→ Mathpix API ─→ [OCR Data] ─→ Cache ─┐
   │                                        │
   │                                        ├─→ [Raw OCR JSON]
   │                                        │
   ▼                                        ▼
TOC README ─→ Parser ─→ [TOC Structure] ─→ Database
                                            │
                                            ▼
[OCR Data] + [TOC Structure] ─→ OpenRouter AI ─→ [Classification]
                                            │
                                            ├─→ [Organized Folders]
                                            │
                                            ▼
[Organized Content] ─→ OpenRouter AI ─→ [Generated Code]
                                            │
                                            ├─→ [Python Modules]
                                            ├─→ [Visualizations]
                                            └─→ [Unit Tests]
```

## 🔌 External API Integration

```
┌──────────────────────────────────────────────────┐
│             External APIs                        │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────┐  ┌──────────────────┐  │
│  │   Mathpix API       │  │  OpenRouter API  │  │
│  ├─────────────────────┤  ├──────────────────┤  │
│  │ • PDF OCR           │  │ • Claude 3.5     │  │
│  │ • Equation extract  │  │ • GPT-4 Vision   │  │
│  │ • Markdown convert  │  │ • Code gen       │  │
│  └──────────┬──────────┘  └────────┬─────────┘  │
│             │                      │             │
└─────────────┼──────────────────────┼─────────────┘
              │                      │
              ▼                      ▼
    ┌──────────────────────────────────────┐
    │      Local Caching System            │
    │  • API Response Cache                │
    │  • Request Deduplication             │
    │  • Offline Processing Support        │
    └──────────────────────────────────────┘
```

## 🗂️ Module Dependencies

```
main_pipeline.py
    │
    ├─→ config/config.py
    │       └─→ python-dotenv
    │
    ├─→ src/logger_config.py
    │       └─→ loguru
    │
    ├─→ src/data_models.py
    │       └─→ pydantic
    │
    ├─→ src/mathpix_processor.py
    │       ├─→ mpxpy
    │       ├─→ src/data_models.py
    │       └─→ src/logger_config.py
    │
    ├─→ src/toc_analyzer.py
    │       ├─→ src/data_models.py
    │       └─→ src/logger_config.py
    │
    ├─→ src/content_organizer.py
    │       ├─→ requests (OpenRouter)
    │       ├─→ src/data_models.py
    │       ├─→ src/toc_analyzer.py
    │       └─→ src/logger_config.py
    │
    └─→ src/code_converter.py
            ├─→ requests (OpenRouter)
            ├─→ src/data_models.py
            └─→ src/logger_config.py
```

## 🔐 Security & Privacy

```
┌──────────────────────────────────────────┐
│      Environment Variables (.env)        │
├──────────────────────────────────────────┤
│  • API Keys (encrypted at rest)          │
│  • Configuration settings                │
│  • Feature flags                         │
└──────────────┬───────────────────────────┘
               │
               ├─→ Never committed to git
               ├─→ .gitignore protection
               └─→ Local file only
```

## 📊 Checkpoint & Resume System

```
Processing Start
    │
    ├─→ Stage 1: OCR ──────────┬─→ [Checkpoint 1 saved]
    │                          │
    ├─→ Stage 2: TOC ──────────┼─→ [Checkpoint 2 saved]
    │                          │
    ├─→ Stage 3: Organize ─────┼─→ [Checkpoint 3 saved]
    │                          │
    └─→ Stage 4: Code Gen ─────┴─→ [Checkpoint 4 saved]

    If interrupted at any point:
    Resume ─→ Load last checkpoint ─→ Continue from next stage
```

## 🎛️ Configuration Hierarchy

```
Default Settings (hardcoded)
         │
         ▼
Environment Variables (.env)
         │
         ▼
Command Line Arguments (--flags)
         │
         ▼
Runtime Configuration
```

## 📈 Scalability Architecture

```
Single PDF (Sequential)
    │
    ├─→ Page-by-page processing
    ├─→ Memory-efficient streaming
    └─→ Checkpoint after each page

Multiple PDFs (Parallel - Future)
    │
    ├─→ Multi-process support
    ├─→ Queue-based distribution
    └─→ Distributed caching
```

---

This architecture ensures:
- ✅ **Modularity**: Each component is independent
- ✅ **Reliability**: Comprehensive caching and checkpoints
- ✅ **Scalability**: Handles large volumes efficiently
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Extensibility**: Easy to add new features

---

This document is original project documentation licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Where it refers to Maxwell's 1873 *Treatise*, that text is public domain.
See [LICENSE](LICENSE).
