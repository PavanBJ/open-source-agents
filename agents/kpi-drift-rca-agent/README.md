# KPI Drift RCA Agent

> An autonomous Root Cause Analysis copilot for analytics engineers and BI teams — diagnoses metric drift without hallucinated math by pairing deterministic Pandas variance decomposition with Gemini diagnostic reasoning.

---

## Overview

### Problem Statement & Intended Users
- **Problem**: When a critical business KPI (conversions, revenue, DAU) unexpectedly drops, analytics teams spend hours manually slicing dimensional cubes to isolate which cohort drove the change. LLMs alone cannot reliably compute multi-dimensional variance decomposition without arithmetic hallucinations.
- **Intended Users**: Analytics engineers, BI analysts, data scientists, and on-call operations teams who need fast, trustworthy metric triage.

### Key Features
- **Deterministic-First Architecture**: 100% of the math is computed by Pandas — exact cohort deltas, percentage contributions, and optional conversion-rate decomposition. The LLM never touches arithmetic.
- **Dual-Metric Decomposition**: Decomposes both absolute volume drift (e.g., conversion count drop) and conversion rate drift (e.g., CR% = conversions / sessions) when a secondary metric is available.
- **Gemini Diagnostic Reasoning**: Feeds verified numerical facts into Gemini to generate executive summaries, plausible technical/business hypotheses, and ready-to-run triage SQL queries.
- **CLI-Driven with Out-of-the-Box Defaults**: Runs instantly on bundled mock data with zero flags (`python main.py`), or fully customizable via `argparse` for production datasets.
- **Markdown Report Export**: Automatically writes a structured RCA report combining the math breakdown and LLM diagnosis to a markdown file.

---

## Technical Stack

- **Language & Runtime**: Python 3.10+
- **Core Libraries**: Pandas (deterministic decomposition), argparse (CLI)
- **Model Provider**: Google Gemini via `google-genai` SDK
- **Models**: `gemini-3.5-flash-lite` (primary), `gemini-2.5-flash` / `gemini-flash-latest` (fallbacks)
- **Environment**: `python-dotenv` for secrets management

---

## Architecture & Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                        KPI Drift RCA Agent                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐      ┌──────────────────────────────────────┐  │
│  │  baseline.csv    │─────>│  STEP 1: Pandas Deterministic       │  │
│  │  current.csv     │      │  Harness (Zero Hallucinations)      │  │
│  └─────────────────┘      │                                      │  │
│                            │  • Cohort-level Δ = Current - Base   │  │
│                            │  • % contribution to total variance  │  │
│                            │  • Rate decomposition (CR% drift)    │  │
│                            └──────────────┬───────────────────────┘  │
│                                           │                          │
│                                           ▼                          │
│                            ┌──────────────────────────────────────┐  │
│                            │  STEP 2: Gemini Reasoning Engine     │  │
│                            │                                      │  │
│                            │  • Executive impact summary          │  │
│                            │  • Primary anomaly cohort analysis   │  │
│                            │  • Technical/business hypotheses     │  │
│                            │  • Targeted triage SQL queries       │  │
│                            └──────────────┬───────────────────────┘  │
│                                           │                          │
│                                           ▼                          │
│                            ┌──────────────────────────────────────┐  │
│                            │  OUTPUT: Console + Markdown Report   │  │
│                            │  (report.md)                         │  │
│                            └──────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**Step-by-step flow:**
1. **CSV Ingestion & Validation** — Loads baseline and current period CSVs; validates that all required metric and dimension columns exist.
2. **Deterministic Decomposition** — Pandas groups by dimensions, computes exact deltas, percentage contributions, and optional rate drift.
3. **Structured Prompt Envelope** — The verified math facts are serialized into a structured prompt (no raw data sent, only aggregated cohort statistics).
4. **Gemini Diagnostic Reasoning** — Gemini interprets the top drag cohorts and generates an executive RCA report with hypotheses and SQL triage queries.
5. **Report Export** — The full diagnosis (math + LLM output) is printed to stdout and exported to a markdown file.

---

## Directory Structure

```text
agents/kpi-drift-rca-agent/
├── data/
│   ├── baseline.csv        # Baseline period cohort data (mock)
│   └── current.csv         # Current period cohort data (mock)
├── .env.example            # Template — GEMINI_API_KEY placeholder only
├── .gitignore              # Ignores .env, report.md, __pycache__/, .venv/
├── main.py                 # Agent entry point (harness + reasoning + CLI)
├── README.md               # This documentation
└── requirements.txt        # Python dependencies (3 packages)
```

---

## Prerequisites

Before running this project, ensure you have:
- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
- **pip** package manager (bundled with Python)
- A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey)

---

## Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd agents/kpi-drift-rca-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv

   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key:**

   Copy the example file and add your key:
   ```bash
   cp .env.example .env
   # Then edit .env and replace the placeholder with your actual key
   ```

   Or set it directly in your terminal:
   ```bash
   # Windows (PowerShell):
   $env:GEMINI_API_KEY="your_gemini_api_key_here"

   # Linux / macOS:
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

---

## Configuration & Environment Variables

| Variable Name | Required | Default | Description |
|:---|:---|:---|:---|
| `GEMINI_API_KEY` | Yes | *None* | API key for Google Gemini (obtain from [AI Studio](https://aistudio.google.com/apikey)) |

---

## How to Run

**Quickstart** — runs on the bundled mock data with zero flags:
```bash
python main.py
```

**Custom run** — override any parameter:
```bash
python main.py \
  --baseline data/baseline.csv \
  --current data/current.csv \
  --metric conversions \
  --secondary-metric sessions \
  --dimensions country,device,channel \
  --output-report rca_oct_2026.md
```

### CLI Arguments

| Flag | Default | Description |
|:---|:---|:---|
| `--baseline` | `data/baseline.csv` | Path to baseline-period CSV |
| `--current` | `data/current.csv` | Path to current-period CSV |
| `--metric` | `conversions` | Primary metric column to decompose |
| `--secondary-metric` | `sessions` | Denominator for rate decomposition (set `''` to disable) |
| `--dimensions` | `country,device,channel` | Comma-separated dimension columns |
| `--output-report` | `report.md` | Output path for the markdown RCA report |

---

## Example Input & Output

### Example Input
The bundled mock data (`data/baseline.csv` and `data/current.csv`) contains weekly e-commerce conversion snapshots segmented by `country`, `device`, and `channel`.

### Example Output

```text
=================================================================
STEP 1: Computing Deterministic Cohort Decomposition...
=================================================================
  Target Metric : conversions
  Variance      : 2,200.0 -> 1,750.0 (-20.45%)
  Top Culprit   : US / Mobile / Paid (Delta: -420.0)
  Worst Rate Δ  : US / Mobile / Paid (6.0% -> 1.8367%, Δ -4.1633 pp)

=================================================================
STEP 2: Calling Gemini for Root Cause Diagnosis...
=================================================================

## 1. Executive Summary

Conversions dropped by **20.45%** (-450 conversions) week-over-week, falling
from 2,200 to 1,750 total events. The decline is overwhelmingly concentrated
in US Mobile Paid traffic, where conversions collapsed from 600 to 180 despite
stable session volume — indicating a severe conversion rate regression, not a
traffic acquisition problem.

## 2. Primary Anomaly Cohort

| Dimension | Value |
|:---|:---|
| Country | US |
| Device | Mobile |
| Channel | Paid |
| Baseline → Current | 600 → 180 conversions |
| Delta | -420 |
| % of Total Variance | **93.33%** |
| CR% Baseline → Current | 6.00% → 1.84% (Δ -4.16 pp) |

## 3. Plausible Technical & Business Hypotheses

1. **Mobile Checkout Regression** — A recent frontend deployment introduced a
   JavaScript error or layout break on mobile viewports affecting the US checkout
   flow, causing cart abandonment spikes.
2. **Payment Gateway Failure** — A mobile-preferred US payment method (Apple Pay,
   Google Pay) experienced elevated transaction rejection rates or latency during
   the current period window.
3. **Tracking Tag Drop** — An analytics SDK or tag manager update suppressed the
   client-side conversion event from firing on mobile browsers, creating a false
   drop in recorded conversions.

## 4. Targeted Triage Queries

```sql
-- Checkout funnel step-level analysis for the anomaly cohort
SELECT event_name, COUNT(DISTINCT session_id) AS sessions
FROM analytics.events
WHERE country = 'US' AND device = 'Mobile' AND channel = 'Paid'
  AND event_date BETWEEN '2026-10-10' AND '2026-10-17'
GROUP BY 1 ORDER BY sessions DESC;
```

```sql
-- Payment gateway error rates for mobile US transactions
SELECT payment_method, error_code, COUNT(*) AS failures
FROM payments.gateway_logs
WHERE country = 'US' AND device_type = 'Mobile' AND status = 'FAILED'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY 1, 2 ORDER BY failures DESC;
```

=================================================================
Report exported to: report.md
=================================================================
```

> **Note**: The Gemini diagnostic section above is a representative example. Actual LLM output will vary between runs based on the model's reasoning.

---

## How to Test

Verify the project works in a clean environment:

```bash
# 1. Create a fresh virtual environment and install deps
python -m venv .venv-test
source .venv-test/bin/activate   # or .\.venv-test\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt

# 2. Set your API key
export GEMINI_API_KEY="your_key"

# 3. Run with defaults — should produce console output + report.md
python main.py

# 4. Verify the report was generated
cat report.md   # or type report.md on Windows

# 5. Verify schema validation catches errors
python main.py --metric nonexistent_column
# Expected: clear error message about missing column
```

---

## Known Limitations

- **Pre-aggregated CSV input required**: The agent expects tabular CSV data with consistent dimension schemas across baseline and current files. It does not query databases directly.
- **LLM hypothesis quality depends on dimension naming**: Descriptive column names (e.g., `country`, `device`, `channel`) yield better diagnostic reasoning than opaque identifiers (e.g., `dim1`, `dim2`).
- **API rate limits apply**: Gemini API usage is subject to your Google AI Studio tier's rate limits and quota. The agent retries across model fallbacks but does not implement exponential backoff.
- **Non-deterministic LLM output**: While the math decomposition is 100% reproducible, Gemini's diagnostic reasoning will vary between runs. The sample output in this README is representative, not exact.
- **No streaming**: The current implementation waits for the full Gemini response before printing. Large diagnostic outputs may have a noticeable delay.

---

## Guardrails

The agent implements multiple safety layers to prevent misuse, resource exhaustion, and LLM misbehavior:

| Layer | Guardrail | Description |
|:---|:---|:---|
| **Input** | CSV file-size limit | Rejects files > 10 MB before loading into memory |
| **Input** | Row count limit | Rejects CSVs with > 1M rows to prevent memory exhaustion |
| **Compute** | Cohort explosion cap | Caps at 10,000 unique dimension combinations; keeps top cohorts by absolute delta |
| **Prompt** | Dimension value sanitization | Strips special characters and truncates long values to prevent prompt injection from CSV data |
| **LLM** | Scope constraint instructions | System-level prompt rules forbid the model from performing arithmetic, executing code, or producing off-topic content |
| **LLM** | Response validation | Checks for empty, `None`, or blocked responses and retries with the next fallback model |
| **Output** | Sensitive path guard | Refuses to write the report to protected system directories (`/etc`, `/usr`, `C:\Windows`, etc.) |

---

## Security & Privacy Considerations

- **Secrets Handling**: The API key is loaded via environment variable or `.env` file (managed by `python-dotenv`). The `.gitignore` excludes `.env` to prevent accidental commits. The `.env.example` contains only placeholder values.
- **Data Privacy**: Only aggregated cohort-level statistics (not raw row-level data) are sent to the Gemini API. Dimension values are sanitized before prompt assembly. No PII is transmitted unless your dimension columns contain PII — review your data before use.
- **Safety**: The agent does not execute shell commands, write to databases, or perform any destructive operations. It reads CSVs and writes a local markdown file. The LLM is explicitly instructed not to execute code or access external systems.

---

## Future Improvements

- [ ] Add BigQuery / database connector for live data ingestion instead of CSV.
- [ ] Support local models via Ollama for air-gapped environments.
- [ ] Implement streaming Gemini responses for real-time output.
- [ ] Add multi-period trend analysis (3+ snapshots) for drift velocity detection.
- [ ] Interactive Streamlit/Gradio dashboard for non-CLI users.

---

## License

*This project is contributed under the repository's open-source license.*
