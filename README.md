# Multi-Modal Evidence Review System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57)
![License](https://img.shields.io/badge/License-MIT-green)

An **AI-powered insurance claim adjudication system** that leverages **Groq's Llama 4 Scout Vision Model** to analyze submitted images, claim transcripts, and historical user data to determine whether claims are **Supported**, **Contradicted**, or **Lack Sufficient Evidence**.

Built using **FastAPI**, **Streamlit**, and **SQLite**, featuring **vision reasoning**, **risk scoring**, **caching**, and a complete **evaluation pipeline**.

---

# ✨ Features

- Multi-modal reasoning using **text + images**
- Vision-based damage assessment
- Historical user risk analysis
- Rule-based fraud detection
- SQLite caching to reduce API usage
- FastAPI REST API
- Interactive Streamlit dashboard
- Offline evaluation pipeline
- Automated testing with Pytest

---

# 🚀 What It Does

When a user submits an insurance claim, the system automatically performs the following steps:

1. Read the submitted claim transcript.
2. Analyze uploaded evidence images.
3. Check the claimant's historical claim records.
4. Send all evidence to **Groq's Llama 4 Scout Vision Model**.
5. Generate a structured insurance decision with justification.
6. Validate outputs and apply business rules.
7. Cache responses to avoid duplicate API calls.
8. Export the final results to **output.csv**.

**Supported Claim Types**

- 🚗 Car
- 💻 Laptop
- 📦 Package

---

# 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Vision Model** | Groq Llama 4 Scout |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **Database** | SQLite |
| **Programming Language** | Python 3.12 |
| **Testing** | Pytest |
| **API** | REST |

---

# 📁 Project Structure

```text
orchestrate/
│
├── agents/
├── backend/
├── database/
├── dataset/
├── evaluation/
├── frontend/
├── output/
├── scripts/
├── tests/
│
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚡ Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/orchestrate.git

cd orchestrate
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key
```

---

## 5. Prepare Dataset

Place the required files inside:

```text
dataset/

claims.csv
sample_claims.csv
user_history.csv
evidence_requirements.csv

images/
```

---

## 6. Run Evaluation

```bash
python scripts/run_sample.py

python evaluation/evaluate.py
```

Generate the final submission:

```bash
python scripts/run_test.py
```

---

## 7. Launch the Application

### Start Backend

```bash
uvicorn backend.main:app --reload
```

### Start Frontend

```bash
streamlit run frontend/app.py
```

Open:

```
http://localhost:8501
```

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/health` | Health Check |
| GET | `/claims` | List Claims |
| GET | `/claims/{user_id}` | Claim Details |
| POST | `/pipeline/run` | Execute Pipeline |
| GET | `/pipeline/run/{run_id}` | Pipeline Status |
| GET | `/evaluation/metrics` | Evaluation Metrics |

Interactive API Documentation:

```
http://localhost:8000/docs
```

---

# ⚙️ Environment Variables

| Variable | Description |
| :--- | :--- |
| `GROQ_API_KEY` | Groq API Key |
| `MODEL_NAME` | Vision Model |
| `DATASET_DIR` | Dataset Location |
| `TEMPERATURE` | Model Temperature |
| `MAX_RETRIES` | Retry Attempts |
| `RETRY_DELAY_SECONDS` | Retry Delay |
| `IMAGE_MAX_DIMENSION` | Maximum Image Size |
| `MAX_IMAGES_PER_REQUEST` | Maximum Images Per Request |
| `LOG_LEVEL` | Logging Level |

---

# 📄 Output Schema

The generated `output.csv` contains the following fields.

| Field | Description |
| :--- | :--- |
| `user_id` | User Identifier |
| `image_paths` | Evidence Images |
| `user_claim` | Original Transcript |
| `claim_object` | Claim Category |
| `evidence_standard_met` | Evidence Sufficiency |
| `evidence_standard_met_reason` | Justification |
| `risk_flags` | Fraud Indicators |
| `issue_type` | Damage Type |
| `object_part` | Damaged Component |
| `claim_status` | Final Decision |
| `claim_status_justification` | Explanation |
| `supporting_image_ids` | Supporting Images |
| `valid_image` | Image Validation |
| `severity` | Damage Severity |

---

# 📊 Evaluation Results

| Metric | Accuracy |
| :--- | :---: |
| Claim Status | **65%** |
| Object Part | **80%** |
| Evidence Standard | **75%** |
| Valid Image | **75%** |
| Issue Type | **55%** |
| Severity | **50%** |

> **Baseline performance on 20 evaluation claims without prompt tuning.**

---

# 🧪 Running Tests

Run the complete test suite.

```bash
pytest -v
```

> All tests execute completely offline.

---

# 🏗 Design Decisions

### ✅ No Agent Framework

Each claim requires only a single structured model call. Using frameworks like LangChain would introduce unnecessary complexity without improving the workflow.

---

### ✅ Rule-Based Risk Analysis

Fraud indicators are implemented in Python to ensure every decision remains deterministic, explainable, and auditable.

---

### ✅ SQLite Caching

Caching eliminates repeated API calls for identical claims, improving both speed and cost efficiency.

---

### ✅ Groq Llama 4 Scout

Chosen because it offers:

- Native vision capabilities
- Fast inference
- Free tier access
- No credit card requirement
- Simple API integration

---

# 💰 Cost

This project can be run entirely using free services.

| Service | Cost |
| :--- | :---: |
| Groq API | Free Tier |
| SQLite | Free |
| Streamlit Community Cloud | Free |

---

# 📜 License

Licensed under the **MIT License**.

---

## ⭐ If you found this project useful, consider giving it a star!
