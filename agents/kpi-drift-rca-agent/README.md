# KPI Drift RCA Agent

An automated Root Cause Analysis (RCA) agent designed to diagnose sudden metric drift in business metrics. It combines deterministic data decomposition in Python with generative reasoning via the Google GenAI SDK, isolating anomaly cohorts and generating actionable triage queries with zero mathematical hallucinations.

---

## Overview

When critical Key Performance Indicators (KPIs) like conversion rates, revenue, or daily active users unexpectedly drop, analytics and engineering teams spend hours slicing dimensional cubes to pinpoint what went wrong.

The **KPI Drift RCA Agent** automates this workflow:
1. **Deterministic Variance Decomposition**: Uses Pandas to calculate exact mathematical differences across dimensional cohorts ($Current - Baseline$), isolating the cohorts that contributed most heavily to the variance.
2. **Diagnostic Reasoning**: Feeds the isolated mathematically sound cohort variances into Google's Gemini model to synthesize executive summaries, hypothesize technical or operational root causes, and write targeted SQL triage queries for further investigation.

---

## Architecture & Harness

The agent uses a two-tier pattern separating calculation from reasoning:

```
[ Baseline & Current CSVs ]
            │
            ▼
┌───────────────────────────────────────┐
│          Deterministic Harness        │
│  - Pandas cohort-level aggregation    │
│  - Mathematical variance (Δ = C - B)  │
│  - Absolute & % delta contribution    │
│  - Zero hallucinations / 100% exact   │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│        Gemini Reasoning Engine        │
│  - Evaluates primary negative cohorts │
│  - Executive business impact summary  │
│  - Plausible engineering hypotheses   │
│  - Generates targeted SQL triage      │
└──────────────────┬────────────────────┘
                   │
                   ▼
          [ Actionable RCA Report ]
```

### 1. The Harness (Deterministic Grounding)
LLMs are prone to arithmetic errors when computing variances over multi-dimensional tables. The deterministic harness executes purely in Pandas:
- Aggregates metrics across user-specified dimensions (e.g., `country`, `device`, `channel`).
- Calculates cohort-level drift: $\Delta = Metric_{current} - Metric_{baseline}$.
- Computes percentage contribution to total variance: $(\Delta_{cohort} / |\Delta_{total}|) \times 100$.
- Sorts and extracts the primary negative drag cohorts and positive buffer cohorts.

### 2. The Reasoning Engine (Gemini)
Gemini receives only verified numerical facts and cohort rankings:
- Evaluates the top drag cohorts against contextual dimensions (e.g., traffic vs. conversions).
- Formulates realistic technical hypotheses (e.g., mobile web checkout errors, API rate limits, tracking script drops).
- Produces targeted, copy-pasteable SQL and log inspection queries for analytics engineers.

---

## Directory Structure

```text
agents/kpi-drift-rca-agent/
├── data/
│   ├── baseline.csv      # Baseline cohort snapshot (e.g., prior period)
│   └── current.csv       # Current cohort snapshot with metric drift
├── .env.example          # Template for required environment variables
├── .gitignore            # Git ignore rules for virtual environments and keys
├── main.py               # Deterministic harness and Gemini RCA agent logic
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

---

## Setup & Execution

### Prerequisites
- **Python 3.10+**
- A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone & Navigate
Navigate to the agent directory:
```bash
cd agents/kpi-drift-rca-agent
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Or Windows (Command Prompt):
.venv\Scripts\activate.bat
# Activate on Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` or set the variable directly in your terminal:

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_actual_api_key_here"
```

Alternatively, create a `.env` file in `agents/kpi-drift-rca-agent/`:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Agent
```bash
python main.py
```

---

## Sample Output

When executed on the included test dataset, the agent produces the following two-step diagnostic output:

```text
=================================================================
STEP 1: Computing Deterministic Cohort Decomposition...
=================================================================
Target Metric : conversions
Variance      : 2200.0 -> 1750.0 (-20.45%)
Top Culprit   : US / Mobile / Paid (Delta: -420.0)

=================================================================
STEP 2: Calling Gemini for Root Cause Diagnosis...
=================================================================

### 1. Executive Summary
Conversions decreased by 20.45% (-450 conversions) week-over-week, dropping from 2,200 to 1,750 total events. This decline is overwhelmingly concentrated in a single traffic segment, heavily impacting mobile campaign efficiency in the US market.

### 2. Primary Anomaly Cohort
- **Cohort**: `country = 'US'`, `device = 'Mobile'`, `channel = 'Paid'`
- **Baseline vs. Current**: 600 -> 180 conversions
- **Impact**: -420 conversions, accounting for **93.33%** of the net negative variance.
- **Context**: Total sessions for this cohort remained stable (~10,000 -> 9,800), pinpointing a severe conversion rate drop rather than traffic acquisition failure.

### 3. Plausible Technical & Business Hypotheses
1. **Mobile Web Checkout Regression**: A recent frontend release introduced an unhandled JavaScript exception or layout break on mobile viewports for US users during checkout.
2. **Third-Party Payment Gateway Outage**: A mobile-preferred US payment method (such as Apple Pay or Google Pay) experienced latency or transaction rejections during the current period.
3. **Broken Tracking Event / Tag Drop**: An update to the tag manager or analytics SDK suppressed client-side purchase completion firing exclusively on mobile browsers.

### 4. Targeted Triage Queries

```sql
-- Step-funnel conversion analysis to locate checkout dropoff point
SELECT
    event_name,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(DISTINCT user_id) AS unique_users
FROM analytics_events
WHERE country = 'US'
  AND device_type = 'Mobile'
  AND acquisition_channel = 'Paid'
  AND event_date BETWEEN '2026-10-10' AND '2026-10-17'
GROUP BY 1
ORDER BY total_sessions DESC;
```

```sql
-- Check payment gateway error rates for mobile checkout attempts
SELECT
    payment_method,
    error_code,
    COUNT(*) AS failure_count
FROM payment_gateway_logs
WHERE country = 'US'
  AND client_device = 'Mobile'
  AND status = 'FAILED'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY 1, 2
ORDER BY failure_count DESC;
```
```
