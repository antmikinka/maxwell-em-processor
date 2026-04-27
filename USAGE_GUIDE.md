# Maxwell Electromagnetic Theory - Setup and Usage Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [API Details](#api-details)

## Prerequisites

### System Requirements
- Python 3.9 or higher
- 8GB+ RAM recommended
- 10GB+ disk space for outputs
- Internet connection for API calls

### API Keys Required
1. **Mathpix API**
   - Sign up at https://mathpix.com/
   - Navigate to Console → API Keys
   - Create new application
   - Save App ID and App Key

2. **OpenRouter API**
   - Sign up at https://openrouter.ai/
   - Navigate to Keys section
   - Generate new API key
   - Save the key securely

## Installation

### Step 1: Clone or Download Project
```bash
cd /path/to/your/workspace
# If you have the files, navigate to the project directory
cd maxwell_em_processor
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Linux/Mac:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import numpy, scipy, sympy, matplotlib; print('Core packages OK')"
python -c "from mpxpy import MathpixClient; print('Mathpix OK')"
```

## Configuration

### Step 1: Create .env File
```bash
cp .env.example .env
```

### Step 2: Edit .env with Your Credentials
Open `.env` in your text editor and add your API keys:

```env
# Mathpix Credentials
MATHPIX_APP_ID=your_actual_mathpix_app_id
MATHPIX_APP_KEY=your_actual_mathpix_app_key

# OpenRouter Credentials  
OPENROUTER_API_KEY=your_actual_openrouter_api_key

# Optional: Adjust logging and processing settings
LOG_LEVEL=INFO  # DEBUG for verbose output
MAX_CONCURRENT_REQUESTS=5
```

### Step 3: Prepare Input Directory
```bash
mkdir -p input
# Place your Maxwell PDF files in the input directory
cp /path/to/maxwell_volume1.pdf input/
cp /path/to/maxwell_volume2.pdf input/
```

## Usage Examples

### Example 1: Process Complete Volume
```bash
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --stage full
```

### Example 2: Process Specific Pages Only
```bash
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --page-ranges "1-50,100-150" \
  --stage full
```

### Example 3: Run Individual Stages

**OCR Only:**
```bash
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --stage ocr
```

**TOC Analysis Only:**
```bash
python main_pipeline.py \
  --stage toc
```

**Content Organization (after OCR):**
```bash
python main_pipeline.py \
  --stage organize \
  --volume 1
```

**Code Generation (after organization):**
```bash
python main_pipeline.py \
  --stage codegen \
  --volume 1
```

### Example 4: Resume Interrupted Processing
```bash
python main_pipeline.py \
  --resume \
  --volume 1
```

### Example 5: Debug Mode with Verbose Logging
Edit `.env` and set:
```env
LOG_LEVEL=DEBUG
```

Then run:
```bash
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --stage full
```

## Advanced Features

### Custom Model Selection

Edit `.env` to use different AI models:

```env
# For better vision analysis (more expensive):
OPENROUTER_VISION_MODEL=anthropic/claude-3.5-sonnet

# For faster code generation (cheaper):
OPENROUTER_CODE_MODEL=anthropic/claude-3.5-sonnet
```

### Parallel Processing

Increase concurrent requests for faster processing:

```env
MAX_CONCURRENT_REQUESTS=10
```

**Note:** Higher values may hit API rate limits.

### Disable API Caching

For testing with fresh results:

```env
ENABLE_API_CACHING=false
```

### Generate Quantum Computing Code

Enable quantum package imports:

```env
ENABLE_QUANTUM_PACKAGES=true
```

This adds Cirq, PennyLane, and OpenFermion code generation.

## Troubleshooting

### Problem: "API Key Not Found" Error

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check contents (keys should not contain spaces)
cat .env

# Ensure no quotes around keys in .env
# Correct:   MATHPIX_APP_ID=abc123def456
# Incorrect: MATHPIX_APP_ID="abc123def456"
```

### Problem: Import Errors

**Solution:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Or install specific package
pip install mpxpy --upgrade
```

### Problem: Mathpix API Rate Limiting

**Solution:**
```env
# Reduce concurrent requests
MAX_CONCURRENT_REQUESTS=2

# Increase timeout
TIMEOUT_SECONDS=600
```

### Problem: Out of Memory

**Solution:**
```bash
# Process smaller page ranges
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --page-ranges "1-10"

# Then process next batch
python main_pipeline.py \
  --pdf input/maxwell_volume1.pdf \
  --volume 1 \
  --page-ranges "11-20"
```

### Problem: OpenRouter API Errors

**Solution:**
```bash
# Test API connection
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Check your API key has credits
# Visit: https://openrouter.ai/credits
```

## API Details

### Mathpix API Costs

Approximate costs per page:
- OCR: $0.01 - $0.02 per page
- Full processing with conversions: $0.02 - $0.04 per page

**Estimate for complete textbook (~400 pages):**
- Total cost: $8 - $16

### OpenRouter API Costs

Varies by model:
- Claude 3.5 Sonnet: ~$3 per million input tokens
- For organization + code generation: ~$0.10 - $0.30 per page

**Estimate for complete textbook:**
- Total cost: $40 - $120

### Total Estimated Cost

Processing one complete 400-page Maxwell volume:
- **Mathpix**: $8 - $16
- **OpenRouter**: $40 - $120
- **Total**: $48 - $136

**Cost-saving tips:**
1. Process only needed chapters
2. Use page ranges strategically
3. Enable caching to avoid re-processing
4. Use cheaper models for simpler tasks

## Monitoring Progress

### Real-time Log Monitoring

**Main progress:**
```bash
tail -f output/logs/main_pipeline.log
```

**API calls:**
```bash
tail -f output/logs/mathpix_api.log
tail -f output/logs/openrouter_api.log
```

**Errors only:**
```bash
tail -f output/logs/errors.log
```

**Statistics:**
```bash
tail -f output/logs/processing_stats.log
```

### Check Checkpoint Status

```bash
ls -lh output/checkpoints/
cat output/checkpoints/step_ocr.json
```

### View Generated Code

```bash
tree output/generated_code/
cat output/generated_code/volume_1/article_001/core_equations.py
```

## Output Structure Reference

```
output/
├── raw_ocr/
│   └── volume_1/
│       ├── page_001.json      # OCR data
│       ├── page_001.mmd       # Mathpix Markdown
│       └── images/            # Extracted figures
├── organized/
│   └── volume_1/
│       └── part-1-electrostatics/
│           └── chapter-01-description-of-phenomena/
│               └── article-001/
│                   ├── page_0001.json
│                   └── content.json
├── generated_code/
│   └── volume_1/
│       └── article-001/
│           ├── core_equations.py
│           ├── visualizations.py
│           └── tests/
│               └── test_equations.py
├── database/
│   ├── toc_structure.json
│   ├── volume_1_ocr_result.json
│   ├── volume_1_organization.json
│   └── volume_1_code_generation.json
├── logs/
│   ├── main_pipeline.log
│   ├── mathpix_api.log
│   ├── openrouter_api.log
│   ├── errors.log
│   └── processing_stats.log
├── cache/
│   ├── mathpix/
│   └── openrouter/
└── checkpoints/
    ├── step_ocr.json
    ├── step_toc_analysis.json
    ├── step_organization.json
    └── step_code_generation.json
```

## Testing Generated Code

```bash
# Navigate to generated code
cd output/generated_code/volume_1/article-001/

# Run the code
python core_equations.py

# Run tests
cd tests
pytest test_equations.py -v

# Or run all tests
cd output/generated_code
pytest -v
```

## Getting Help

### Check Logs
Most issues can be diagnosed from logs:
```bash
grep -i error output/logs/errors.log
grep -i "failed" output/logs/main_pipeline.log
```

### Validate Configuration
```bash
python config/config.py
```

### Test Individual Components
```bash
# Test Mathpix connection
python src/mathpix_processor.py

# Test TOC analyzer
python src/toc_analyzer.py

# Test content organizer
python src/content_organizer.py
```

---

**For issues or questions, check the main README.md or create a GitHub issue.**
