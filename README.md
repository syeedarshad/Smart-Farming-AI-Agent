# Smart Farming AI – Multilingual Farmer Assistant

A Streamlit-based multilingual AI farming assistant that guides Indian farmers through the complete crop lifecycle using a Retrieval-Augmented Generation (RAG) pipeline. Built for the IBM Smart Farming AI hackathon (Problem Statement No. 9).

---

## Features

- **4 languages**: English, Tamil (தமிழ்), Telugu (తెలుగు), Hindi (हिंदी)
- **All Indian states** with detailed demo data for Tamil Nadu, Andhra Pradesh and Maharashtra
- **25+ crops** across all major categories
- **12-stage crop lifecycle roadmap** for every supported crop
- **AI Farming Assistant** using TF-IDF + cosine RAG pipeline
- **Natural farming guidance**: compost, FYM, neem, vermicompost, mulching, crop rotation
- **Pest and disease guidance** with responsible IPM safeguards
- **Farmer safety module**: cyclones, floods, lightning, heat, electrical, pesticides
- **Approximate market prices** with clear disclaimers
- **IBM Granite integration** ready via watsonx.ai (activate with credentials)
- **Demo mode** with honest fallback (no fabricated Granite responses)

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| RAG Retrieval | TF-IDF + cosine similarity (scikit-learn) |
| LLM (demo) | Template-based from retrieved knowledge |
| LLM (production) | IBM Granite via watsonx.ai |
| Data | Local JSON knowledge base |
| Language | Python 3.10+ |
| Config | python-dotenv |

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows PowerShell (or any terminal)

### Step 1 – Clone or download the project

```powershell
cd "D:\AI Agent for Smart Farming"
```

### Step 2 – Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you see an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 3 – Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 – Configure environment

```powershell
Copy-Item .env.example .env
```

Edit `.env` if needed. The default `LLM_PROVIDER=demo` works without any credentials.

### Step 5 – Run the application

```powershell
streamlit run app.py
```

The application opens at `http://localhost:8501`.

---

## Running Tests

```powershell
python -m pytest tests/ -v
```

Or run individual test files:

```powershell
python tests/test_data_loader.py
python tests/test_retrieval.py
python tests/test_rag_pipeline.py
```

---

## IBM Granite Integration

The application is fully prepared for IBM Granite. To activate it:

1. Create an IBM Cloud account and access IBM watsonx.ai.
2. Generate an API key in IBM Cloud IAM.
3. Create a watsonx.ai project and copy the Project ID.
4. Update your `.env` file:

```
LLM_PROVIDER=ibm_granite
IBM_WATSONX_API_KEY=your_actual_api_key
IBM_WATSONX_PROJECT_ID=your_actual_project_id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```

5. Install the IBM SDK:

```powershell
pip install ibm-watsonx-ai
```

6. Restart the Streamlit application.

> **Never commit your `.env` file to GitHub.** It is listed in `.gitignore`.

---

## Project Structure

```
smart-farming-ai/
├── app.py                      Home page and navigation
├── requirements.txt
├── .env.example                Environment variable template
├── README.md
│
├── data/                       Agricultural knowledge base (JSON)
│   ├── crops.json
│   ├── state_crop_mapping.json
│   ├── crop_roadmaps.json
│   ├── natural_farming.json
│   ├── pest_management.json
│   ├── farmer_safety.json
│   └── market_prices.json
│
├── src/                        Application logic
│   ├── config.py               Settings and environment
│   ├── data_loader.py          Loads and validates JSON knowledge files
│   ├── retrieval.py            TF-IDF chunker and cosine retrieval
│   ├── rag_pipeline.py         Orchestrates retrieval → prompt → LLM
│   ├── language_service.py     Language names, UI labels, translation
│   ├── farming_advisor.py      High-level query handler
│   ├── market_service.py       Market price provider
│   └── llm/
│       ├── base.py             Abstract LLMProvider interface
│       ├── demo_provider.py    Demo mode (no credentials needed)
│       └── ibm_granite_provider.py  IBM watsonx.ai integration
│
├── pages/                      Streamlit multi-page navigation
│   ├── 1_Farmer_Profile.py
│   ├── 2_Crop_Explorer.py
│   ├── 3_Crop_Roadmap.py
│   ├── 4_AI_Farming_Assistant.py
│   ├── 5_Natural_Farming.py
│   ├── 6_Pest_Management.py
│   ├── 7_Weather_and_Safety.py
│   └── 8_Market_Guidance.py
│
└── tests/
    ├── test_data_loader.py
    ├── test_retrieval.py
    └── test_rag_pipeline.py
```

---

## Data Sources and Disclaimers

- Crop information is based on publicly available guidance from the Department of Agriculture & Farmers Welfare, IMD Agromet, state agriculture departments and KVK resources.
- Market prices shown are **illustrative approximate ranges only** — not real-time mandi data. Always verify current prices at your local AGMARKNET or e-NAM portal.
- Weather safety information is sourced from NDMA SACHET dos-and-don'ts guidelines.
- Pest and disease guidance follows IPM principles from official sources.
- This application is an **information aid only**, not a substitute for a local agricultural officer, KVK scientist, plant pathologist or emergency service.
- IBM Granite model responses (when enabled) are grounded in retrieved knowledge and will clearly state when information is insufficient.

---

## Responsible AI

- The assistant will not invent weather alerts, market prices, pesticide dosages or crop statistics.
- Demo mode responses are clearly labelled as such.
- Safety information always takes priority over productivity advice.
- The application asks clarifying questions rather than guessing when information is insufficient.

---

*Built for IBM Smart Farming AI Hackathon — Problem Statement No. 9*
