# Smart Farming AI – Multilingual Farmer Assistant

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![IBM Granite Ready](https://img.shields.io/badge/IBM%20Granite-watsonx.ai%20Ready-054ADA.svg)](https://www.ibm.com/granite)
[![Retrieval scikit-learn](https://img.shields.io/badge/RAG-TF--IDF%20%2B%20Cosine-orange.svg)](https://scikit-learn.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hackathon Problem Statement](https://img.shields.io/badge/IBM%20Hackathon-Problem%20Statement%20%239-purple.svg)](https://github.com/syeedarshad/Smart-Farming-AI-Agent)

**Smart Farming AI** is a multilingual agricultural advisory system engineered to empower Indian farmers with localized, stage-by-stage crop lifecycle guidance, sustainable natural farming practices, integrated pest management, disaster safety protocols, and market price estimates.

Built for the **IBM Smart Farming AI Hackathon (Problem Statement No. 9)**, the application combines a grounded **Retrieval-Augmented Generation (RAG)** pipeline with complete UI localization in **English**, **Tamil (தமிழ்)**, **Telugu (తెలుగు)**, and **Hindi (हिंदी)**. It operates out of the box in **Demo Mode** using a verified offline agricultural knowledge base and includes built-in architecture for live cloud inference via **IBM Granite** on **watsonx.ai**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Application Screenshots](#application-screenshots)
- [Technology Stack](#technology-stack)
- [System Architecture & Workflow](#system-architecture--workflow)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [IBM Granite Integration](#ibm-granite-integration)
- [Data Sources and Limitations](#data-sources-and-limitations)
- [Responsible AI & Guardrails](#responsible-ai--guardrails)
- [Future Enhancements](#future-enhancements)
- [Acknowledgements](#acknowledgements)

---

## Project Overview

Indian agriculture supports hundreds of millions of livelihoods across diverse agro-climatic zones, soils, and languages. However, smallholder and regional farmers frequently encounter critical information barriers:

- **Linguistic Divide:** Crucial agronomic advisories and weather alerts are predominantly published in English or standardized Hindi, leaving non-Hindi regional farmers underserved.
- **Fragmented Lifecycle Guidance:** Farmers often lack structured, sequential guidance covering all stages—from land preparation, seed selection, and sowing to pest protection, harvesting, and post-harvest storage.
- **Risk of LLM Hallucinations:** Generic foundation models often generate unverified chemical recommendations or hallucinated agricultural metrics that could damage crops or harm farm health.
- **Connectivity and Cost Constraints:** Rural communities require solutions that can run reliably in lightweight environments without high ongoing cloud API expenses.

**Smart Farming AI** directly addresses these challenges by implementing:
1. **Full Regional Localization:** Four-language native navigation and content presentation (English, தமிழ், తెలుగు, हिंदी).
2. **Deterministic RAG Retrieval:** Agricultural knowledge is retrieved from curated public domain sources using TF-IDF vectorization and cosine similarity scoring.
3. **Dual Execution Modes:** A zero-credential offline Demo Mode for instant deployment and testing, coupled with an enterprise-ready IBM Granite watsonx.ai provider.
4. **Safety-First Guardrails:** Immediate hazard override detection prioritizing emergency protocols (cyclones, lightning, floods, heatwaves, chemical safety) over standard agronomic tips.

> **Architecture Clarification:** This repository is implemented as a **modular single-agent Streamlit application** powered by a deterministic TF-IDF RAG pipeline and specialized domain services. It does *not* use multi-agent frameworks or Langflow orchestration.

---

## Key Features

| Capability | Description |
|---|---|
| 🌐 **Multilingual Native UX** | Complete interface and advisory localization across English, Tamil (`தமிழ்`), Telugu (`తెలుగు`), and Hindi (`हिंदी`). |
| 📍 **Location-Aware Profiling** | State-level agro-climatic filtering covering all Indian states and Union Territories, featuring rich regional datasets for Tamil Nadu, Andhra Pradesh, and Maharashtra. |
| 🌾 **25+ Curated Crops** | Comprehensive agronomic database covering cereals (paddy, wheat, maize), pulses (chickpea, pigeon pea), oilseeds (groundnut, mustard), cash crops (cotton, sugarcane), and horticultural crops. |
| 🗓️ **12-Stage Lifecycle Roadmap** | Step-by-step guidance tracking the full cultivation timeline: Land Prep &rarr; Variety Selection &rarr; Seed Treatment &rarr; Sowing &rarr; Water Management &rarr; Nutrient Application &rarr; Weed Control &rarr; Pest Management &rarr; Flower/Pod Stage &rarr; Maturity &rarr; Harvesting &rarr; Post-Harvest Storage. |
| 🤖 **Grounded RAG Assistant** | Query retrieval grounded in curated knowledge chunks with cosine similarity ranking, source transparency, and strict anti-hallucination prompts. |
| 🌿 **Natural Farming Module** | Sustainable, low-cost organic practices including Farmyard Manure (FYM), Jeevamrutha, neem-based repellents, vermicompost, green manuring, and mulching techniques. |
| 🛡️ **Integrated Pest Management (IPM)** | Responsible pest and pathogen identification emphasizing cultural, physical, biological controls, and cautious chemical safety. |
| ⚠️ **Weather & Disaster Safety** | Priority safety cards alerting farmers to extreme weather dos-and-don'ts (cyclones, floods, lightning strikes, heatwaves, electrical pump safety) sourced from NDMA SACHET guidelines. |
| 📊 **Market Guidance & Estimations** | Approximate commodity price ranges, seasonality indices, and direct links to official mandi portals (AGMARKNET & e-NAM). |

---

## Application Screenshots

The application supports four Indian languages and provides fully localized farming guidance, state-aware crop discovery, lifecycle roadmaps, and emergency advisories.

### English Interface
![English Interface](assets/screenshots/english/dashboard.png)

*English interface displaying the location-personalized dashboard, farming modules, and crop advisory tools.*

---

### தமிழ் Interface
![தமிழ் Interface](assets/screenshots/tamil/dashboard.png)

*தமிழ் (Tamil) interface showing localized agricultural terms, seasonal crop mappings, and natural farming guidance.*

---

### తెలుగు Interface
![తెలుగు Interface](assets/screenshots/telugu/dashboard.png)

*తెలుగు (Telugu) interface presenting localized crop roadmaps, soil management advice, and safety alerts.*

---

### हिंदी Interface
![हिंदी Interface](assets/screenshots/hindi/dashboard.png)

*हिंदी (Hindi) interface providing Hindi-language farming assistance, pest management recommendations, and market insights.*

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                       STREAMLIT UI                          │
│          Multi-Page Web App (English, தமிழ், తెలుగు, हिंदी)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG RETRIEVAL ENGINE                     │
│         TF-IDF Vectorizer + Cosine Similarity (scikit-learn) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     LLM PROVIDER ROUTER                     │
│  ┌─────────────────────────────┐ ┌────────────────────────┐ │
│  │   Demo Mode (Local KB)      │ │ IBM Granite watsonx.ai │ │
│  │   Deterministic & Verified  │ │ ibm/granite-4-h-small  │ │
│  └─────────────────────────────┘ └────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   KNOWLEDGE BASE (JSON)                     │
│   Crops • Roadmaps • Natural Farming • Pests • Safety • Price│
└─────────────────────────────────────────────────────────────┘
```

| Layer | Component | Specification |
|---|---|---|
| **User Interface** | [Streamlit](https://streamlit.io/) | Multi-page interactive application (`app.py` + 8 modular pages) |
| **Language & Runtime** | [Python](https://www.python.org/) | Python 3.10 to 3.13 |
| **RAG Retrieval Engine** | [scikit-learn](https://scikit-learn.org/) | In-memory TF-IDF vectorizer with cosine similarity ranking |
| **Primary LLM Integration** | [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai) | `ibm/granite-4-h-small` (REST API & `ibm-watsonx-ai` SDK paths) |
| **Fallback LLM Provider** | Template Engine | Deterministic prompt-synthesis engine running on local JSON corpus |
| **Knowledge Base** | Structured JSON | 7 curated domain files (crops, roadmaps, safety, pests, natural farming) |
| **Data Processing & Viz** | Pandas, Plotly | Tabular market prices and interactive crop charts |
| **Configuration** | `python-dotenv` | Standard 12-factor environment configuration |
| **Test Suite** | `pytest` | 55 unit and integration tests |

---

## System Architecture & Workflow

The solution operates as a single-agent RAG workflow designed for deterministic reliability:

```mermaid
flowchart TD
    A[Farmer Query / Input] --> B[Language Detection & State Profile]
    B --> C{Safety Hazard Triggered?}
    C -- Yes --> D[NDMA Safety Card Override]
    C -- No --> E[TF-IDF Chunk Search across Curated JSON KB]
    E --> F[Cosine Similarity Ranking & Top-K Extraction]
    F --> G[Grounded Context Synthesis]
    G --> H{LLM Provider Configured?}
    H -- "LLM_PROVIDER=demo (Default)" --> I[Local Verified Response Generator]
    H -- "LLM_PROVIDER=ibm_granite" --> J[IBM watsonx.ai API / SDK]
    J -- Success --> K[IBM Granite 4-H-Small Output]
    J -- Missing / Failed Credentials --> L[Graceful Error Display - No Mock Granites]
    I --> M[Streamlit UI Display with Citations & Disclaimers]
    K --> M
    D --> M
    L --> M
```

### Key Workflow Principles
1. **Hazard Pre-emption:** Safety keywords (e.g., cyclone, lightning, chemical burn, electric shock) immediately trigger emergency safety cards from NDMA SACHET before processing standard crop queries.
2. **Context-Grounded Answering:** Prompts enforce strict grounding in retrieved knowledge chunks. If the system lacks specific information, it states its limitations rather than hallucinating.
3. **No Fabricated Granite Output:** If IBM Granite credentials are missing or call limits fail, the system reports the authentication/API state transparently; it does not substitute mock text under the Granite label.

---

## Project Structure

```text
smart-farming-ai/
├── app.py                              # Main landing page and state-aware dashboard
├── requirements.txt                    # Python project dependencies
├── .env.example                        # Template for environment configuration
├── .gitignore                          # Git exclusions (protects .env, venv, caches)
├── README.md                           # Project documentation
│
├── assets/                             # Visual media and interface documentation
│   └── screenshots/
│       ├── english/                    # English UI captures
│       ├── tamil/                      # Tamil (தமிழ்) UI captures
│       ├── telugu/                     # Telugu (తెలుగు) UI captures
│       └── hindi/                      # Hindi (हिंदी) UI captures
│
├── data/                               # Domain knowledge base (curated JSON files)
│   ├── crops.json                      # 25+ detailed crop profiles and agronomic metrics
│   ├── state_crop_mapping.json         # State-to-crop mappings across Kharif, Rabi, Zaid
│   ├── crop_roadmaps.json              # 12-stage cultivation plans per crop
│   ├── natural_farming.json            # Low-cost sustainable organic formulations
│   ├── pest_management.json            # IPM thresholds, symptoms, and organic remedies
│   ├── farmer_safety.json              # NDMA SACHET guidelines for disasters and hazards
│   └── market_prices.json              # Approximate historical commodity price ranges
│
├── pages/                              # Streamlit multi-page interface modules
│   ├── 1_Farmer_Profile.py             # Farm location, state, and language preferences
│   ├── 2_Crop_Explorer.py              # Crop catalogue search and comparative filters
│   ├── 3_Crop_Roadmap.py               # Interactive 12-stage lifecycle visualizer
│   ├── 4_AI_Farming_Assistant.py       # Grounded RAG chat interface with source citations
│   ├── 5_Natural_Farming.py            # Step-by-step bio-fertilizer and compost recipes
│   ├── 6_Pest_Management.py            # IPM symptoms, prevention, and organic controls
│   ├── 7_Weather_and_Safety.py         # Extreme weather alerts and farm safety protocols
│   └── 8_Market_Guidance.py            # Approximate price trends and mandi disclaimers
│
├── scripts/                            # Operational and diagnostic utilities
│   └── test_ibm_connection.py          # Standalone verification script for watsonx.ai
│
├── src/                                # Core application source code
│   ├── config.py                       # Application settings and environment loader
│   ├── data_loader.py                  # Knowledge base ingestion and chunk validator
│   ├── retrieval.py                    # TF-IDF indexer and cosine similarity retriever
│   ├── rag_pipeline.py                 # RAG orchestrator, prompt synthesis, response builder
│   ├── language_service.py             # UI strings, terminology translation, language mappings
│   ├── content_localization.py         # Localized content dictionaries
│   ├── farming_advisor.py              # High-level domain advisory routines
│   ├── market_service.py               # Approximate market pricing and disclaimer handler
│   ├── shared_utils.py                 # Common Streamlit layout and session components
│   └── llm/                            # Modular LLM provider abstractions
│       ├── base.py                     # Abstract base class for LLM providers
│       ├── demo_provider.py            # Zero-credential local offline engine
│       └── ibm_granite_provider.py     # watsonx.ai REST & SDK client implementation
│
└── tests/                              # Automated test suite (pytest)
    ├── test_data_loader.py             # Verifies JSON integrity, chunk schemas, mappings
    ├── test_language_service.py        # Verifies 4-language coverage and translation fallbacks
    ├── test_rag_pipeline.py            # Tests RAG pipeline, safety checks, mock providers
    └── test_retrieval.py               # Tests TF-IDF search, keyword scoring, Top-K filters
```

---

## Installation and Setup

### Prerequisites
- **Python:** Version 3.10, 3.11, 3.12, or 3.13 installed
- **Terminal:** Windows PowerShell, Command Prompt, or Unix bash/zsh
- **Git:** Installed on your system

### 1. Clone the Repository and Navigate to the Project

```powershell
git clone https://github.com/syeedarshad/Smart-Farming-AI-Agent.git
cd "D:\AI Agent for Smart Farming\smart-farming-ai"
```

> **Note:** If you already cloned the repository to `D:\AI Agent for Smart Farming\smart-farming-ai`, navigate directly into that folder.

### 2. Create and Activate a Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*If you encounter a PowerShell execution policy restriction, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

All required packages—including Streamlit, scikit-learn, and the optional `ibm-watsonx-ai` client library—are managed via `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your local `.env` configuration file from the provided template:

```powershell
Copy-Item .env.example .env
```

*(On Linux / macOS use: `cp .env.example .env`)*

By default, `.env` is configured with `LLM_PROVIDER=demo`, allowing full local functionality without requiring any external API keys or cloud credentials.

---

## Environment Configuration

The application reads configuration values exclusively through `src/config.py` using `python-dotenv`. Both primary short names (`WATSONX_*`) and backward-compatible prefix names (`IBM_WATSONX_*`) are supported.

| Environment Variable | Default Value | Description |
|---|---|---|
| `LLM_PROVIDER` | `demo` | Provider selector: `demo` (local deterministic) or `ibm_granite` (IBM watsonx.ai). |
| `WATSONX_API_KEY` *(or `IBM_WATSONX_API_KEY`)* | *(empty)* | IBM Cloud IAM API Key for watsonx.ai access. |
| `WATSONX_PROJECT_ID` *(or `IBM_WATSONX_PROJECT_ID`)* | *(empty)* | Project ID associated with your watsonx.ai instance. |
| `WATSONX_URL` *(or `IBM_WATSONX_URL`)* | `https://us-south.ml.cloud.ibm.com` | Regional endpoint for your IBM watsonx.ai service. |
| `GRANITE_MODEL_ID` *(or `IBM_GRANITE_MODEL_ID`)* | `ibm/granite-4-h-small` | Exact model identifier in the watsonx.ai catalogue. |
| `IBM_CLOUD_IAM_URL` | `https://iam.cloud.ibm.com/identity/token` | IBM Cloud IAM token exchange URL. |
| `APP_NAME` *(or `APP_TITLE`)* | `Smart Farming AI` | Title displayed across Streamlit header and sidebar. |
| `APP_ENV` | `development` | Deployment environment flag (`development`, `staging`, `production`). |
| `APP_PORT` | `8501` | Local port used by the Streamlit web server. |
| `APP_DEBUG` | `false` | Enables verbose debug logging when set to `true`. |

> **Security Rule:** Never commit `.env` to version control. The repository `.gitignore` explicitly prevents `.env` and sensitive credentials from being committed.

---

## Running the Application

To start the multi-page Streamlit application, ensure your virtual environment is active and execute:

```powershell
streamlit run app.py
```

Once initialized, Streamlit will display local and network URLs:
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Navigating the Application
1. **Home / Dashboard (`app.py`):** Select your preferred language and review regional crop summaries.
2. **Farmer Profile (`pages/1_Farmer_Profile.py`):** Set your state, district, land holding, soil type, and irrigation source.
3. **Crop Explorer (`pages/2_Crop_Explorer.py`):** Filter 25+ crops by season, soil compatibility, water requirements, and region.
4. **Crop Roadmap (`pages/3_Crop_Roadmap.py`):** Inspect an end-to-end 12-stage cultivation timeline for your selected crop.
5. **AI Farming Assistant (`pages/4_AI_Farming_Assistant.py`):** Ask agricultural questions in your chosen language and receive grounded RAG responses with citations.
6. **Natural Farming (`pages/5_Natural_Farming.py`):** Access practical recipes for compost, Jeevamrutha, neem-based sprays, and soil enhancement.
7. **Pest Management (`pages/6_Pest_Management.py`):** Diagnose symptoms and apply Integrated Pest Management (IPM) practices.
8. **Weather & Safety (`pages/7_Weather_and_Safety.py`):** Check emergency checklists for cyclones, floods, lightning, and heatwaves.
9. **Market Guidance (`pages/8_Market_Guidance.py`):** View indicative price patterns and direct links to official mandi portals.

---

## Running Tests

The test suite validates data schemas, multilingual UI labels, TF-IDF retrieval scoring, safety hazard detection, and LLM provider interfaces.

Run all tests via `pytest`:

```powershell
python -m pytest tests/ -v
```

### Running Individual Test Suites

```powershell
python -m pytest tests/test_data_loader.py -v
python -m pytest tests/test_language_service.py -v
python -m pytest tests/test_retrieval.py -v
python -m pytest tests/test_rag_pipeline.py -v
```

*All 55 automated unit and integration tests validate knowledge consistency, localized string presence, anti-hallucination guardrails, and graceful error handling.*

---

## IBM Granite Integration

The application contains complete implementation code for IBM's enterprise foundation models via **IBM watsonx.ai**.

### Target Model
- **Model ID:** `ibm/granite-4-h-small` (configured in `src/config.py` and `.env.example`)
- **Hosting Platform:** IBM watsonx.ai Foundation Model Library

### Implementation Architecture
The integration is implemented in [`src/llm/ibm_granite_provider.py`](src/llm/ibm_granite_provider.py) using a resilient dual-path approach:
1. **`ibm-watsonx-ai` SDK Path:** Utilizes the official IBM Python SDK when available.
2. **REST API Path:** A pure-requests client utilizing OAuth2 Bearer token exchange against the IBM Cloud IAM endpoint (`https://iam.cloud.ibm.com/identity/token`) with automatic token caching and expiry tracking.

### Verification Status & Honest Disclosure
> [!IMPORTANT]
> **Implementation vs. Live Testing Status:**
> - The code integration for IBM Granite (REST API client, SDK wrapper, OAuth2 token caching, RAG prompt injection, and error handlers) is **fully implemented** in `src/llm/ibm_granite_provider.py`.
> - However, **live cloud connectivity and API inference have not been verified** due to pending active IBM Cloud / watsonx.ai credentials.
> - When running with `LLM_PROVIDER=ibm_granite` without active credentials, the system gracefully reports the authentication status and does not generate simulated or fabricated Granite responses.

### How to Activate and Test IBM Granite
1. Obtain an IBM Cloud account with access to **watsonx.ai**.
2. Create an IBM Cloud IAM API Key and locate your watsonx.ai Project ID.
3. Edit your `.env` file:
   ```env
   LLM_PROVIDER=ibm_granite
   WATSONX_API_KEY=your_actual_ibm_cloud_api_key
   WATSONX_PROJECT_ID=your_actual_watsonx_project_id
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   GRANITE_MODEL_ID=ibm/granite-4-h-small
   ```
4. Run the diagnostic smoke-test script to test credentials, IAM token generation, REST inference, and RAG integration:
   ```powershell
   python scripts/test_ibm_connection.py
   ```
5. Restart the Streamlit application to begin querying IBM Granite.

---

## Data Sources and Limitations

### Data Sources
- **Crop & Agronomic Profiles:** Public guidance from the Ministry of Agriculture & Farmers Welfare, Indian Council of Agricultural Research (ICAR), state agricultural universities (TNAU, ANGRAU), and Krishi Vigyan Kendras (KVK).
- **Disaster & Farm Safety:** National Disaster Management Authority (NDMA) SACHET advisory guidelines.
- **Natural Farming Formulations:** National Centre of Organic and Natural Farming (NCONF) documentation.

### Limitations & Disclaimers
- **Approximate Market Estimates:** Commodity prices presented in `Market Guidance` are **indicative historical estimates** for trend understanding. They are **NOT real-time mandi prices**. Mandi rates fluctuate continuously based on arrivals, variety, moisture content, and grade. Farmers must verify real-time prices at [AGMARKNET](https://agmarknet.nic.in) or [e-NAM](https://enam.gov.in).
- **Informational Aid Only:** This software is an educational and decision-support tool. It is not a certified replacement for on-ground agricultural extension officers, plant pathologists, or veterinary specialists.
- **Offline Knowledge Boundary:** In Demo Mode, answers are strictly bounded by the curated JSON knowledge base. If a query falls outside the knowledge base, the system will explicitly indicate that information is unavailable.

---

## Responsible AI & Guardrails

The system follows strict Responsible AI guidelines tailored for high-stakes rural agriculture:

1. **Safety Priority Override:** Emergency triggers for natural disasters (cyclones, floods, lightning, heatstrokes) or hazardous chemical exposure immediately override general agronomic guidance.
2. **Zero-Hallucination Grounding:** Prompts instruct the LLM to answer exclusively using retrieved knowledge chunks and explicitly decline to answer rather than fabricate unverified pesticide dosages or chemical mixtures.
3. **Execution Transparency:** Responses generated under Demo Mode are clearly tagged with an informational notice. The application never misrepresents local template answers as live foundation model outputs.
4. **Privacy-Preserving:** The application does not collect, store, or transmit personal farmer data or farm location records.

---

## Future Enhancements

- [ ] **Live e-NAM / AGMARKNET API Integration:** Connect to official government APIs for live daily mandi auction feeds.
- [ ] **Voice-First Regional Interface:** Integrate multilingual speech-to-text and text-to-speech (Whisper / Bhashini) for farmers who prefer audio interactions.
- [ ] **Computer Vision Pest Diagnosis:** Add leaf image upload capabilities for automated visual crop disease diagnosis.
- [ ] **IoT & Micro-Weather Telemetry:** Ingest local soil moisture sensor and automated weather station (AWS) feeds.
- [ ] **Multi-Agent Advisory Architecture:** Expand the single-agent pipeline into specialized collaborative agents (Agronomist Agent, Market Agent, Weather Agent).

---

## Acknowledgements

- **IBM Smart Farming AI Hackathon:** Developed for Problem Statement No. 9.
- **Open Data & Knowledge Sources:** ICAR, IMD Agromet, NDMA SACHET, AGMARKNET, and Department of Agriculture & Farmers Welfare.
- **Open Source Ecosystem:** Streamlit, Scikit-learn, Pandas, Plotly, and Python community contributors.

---

*Smart Farming AI – Empowering Indian agriculture with localized, grounded, and responsible intelligence.*
