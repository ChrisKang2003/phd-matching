# Rightfit PhD

AI-powered student–professor recommendation system using web crawling, OpenAlex enrichment, and transformer-based semantic ranking.

---

# Overview

Rightfit PhD is an NLP-based recommendation system designed to help graduate students identify professors whose research interests align with their academic goals.

The project combines:

* Faculty web crawling
* Research-profile enrichment
* Transformer-based semantic ranking
* Web deployment

The system crawls university faculty pages, enriches professor profiles using scholarly metadata from OpenAlex, and ranks professors using a fine-tuned MiniLM cross-encoder model.

---

# Features

* Multi-university faculty crawling
* OpenAlex publication/topic enrichment
* Transformer-based recommendation model
* Semantic student–professor matching
* Flask backend API
* React frontend website
* Multi-discipline support
* Single-command deployment

---

# Supported Disciplines

* Computer Science & AI
* Electrical Engineering
* Biomedical Engineering
* Business & Finance

---

# Supported Universities

Example universities currently included:

* Stanford University
* MIT
* Carnegie Mellon University
* Cornell University
* Princeton University
* Johns Hopkins University
* Duke University
* Georgia Tech
* UIUC
* University of Michigan
* University of Pennsylvania

---

# Project Architecture

```text
Faculty Websites
        ↓
Faculty Crawler
        ↓
Professor Dataset (CSV)
        ↓
OpenAlex Research Enrichment
        ↓
MiniLM Cross-Encoder Model
        ↓
Flask Backend API
        ↓
React Frontend Website
```

---

# Repository Structure

```text
phd-matching/
│
├── crawler_to_csv.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── processed/
│   │   └── professors.csv
│   │
│   └── training_pairs/
│       └── student_professor_pairs.csv
│
├── model/
│   ├── __init__.py
│   ├── config.py
│   ├── dataset.py
│   ├── train_model.py
│   ├── rank_professors.py
│   ├── predict_match.py
│   ├── evaluate.py
│   └── classify_discipline.py
│
├── utils/
│   └── enrich_professors_openalex.py
│
└── web/
    ├── backend/
    │   └── app.py
    │
    └── frontend/
        ├── package.json
        ├── index.html
        └── src/
            ├── App.jsx
            └── style.css
```

---

# Model Information

## Base Model

```text
cross-encoder/ms-marco-MiniLM-L6-v2
```

## Why MiniLM?

The MiniLM cross-encoder model was selected because:

* Only 22M parameters
* Can be fine-tuned on RTX 4060 GPUs
* Strong semantic ranking performance
* Efficient inference speed
* Suitable for sentence-pair similarity tasks

## Why Cross-Encoder?

The cross-encoder jointly processes both:

* student profile
* professor profile

This allows the model to capture token-level semantic relationships and generate higher-precision recommendation scores.

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/ChrisKang2003/phd-matching.git
cd phd-matching
```

---

## 2. Create Virtual Environment

### Windows PowerShell

```powershell
py -3.13 -m venv .venv313
.venv313\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If using Playwright:

```bash
playwright install
```

---

## 4. Install Frontend Dependencies

```bash
cd web/frontend
npm install
cd ../..
```

---

# Running the Full Pipeline

## Step 1: Crawl Faculty Data

```bash
python crawler_to_csv.py
```

Creates:

```text
data/processed/professors.csv
```

---

## Step 2: Enrich Professor Profiles

```bash
python utils/enrich_professors_openalex.py
```

Creates:

```text
data/processed/professors_enriched.csv
```

---

## Step 3: Train Recommendation Model

```bash
python model/train_model.py
```

Creates:

```text
model/checkpoints/rightfit_cross_encoder/
```

---

## Step 4: Launch Website

```bash
python web/backend/app.py
```

Open:

```text
http://localhost:5000
```

---

# Example Training Dataset

The training dataset contains labeled student–professor pairs.

Example format:

```csv
student_profile,professor_profile,label
"Interested in machine learning and NLP", "Research interests include NLP and transformers",1
```

The project currently includes:

* 1000 student–professor pairs
* 275+ professor profiles
* 11 universities

---

# Technologies Used

## Machine Learning

* PyTorch
* SentenceTransformers
* Transformers
* Scikit-learn

## Web Development

* Flask
* React
* Vite

## Data Collection

* Requests
* BeautifulSoup
* OpenAlex API

---

# API Endpoints

## Health Check

```text
GET /api/health
```

---

## Generate Recommendations

```text
POST /api/recommend
```

Request Body:

```json
{
  "student_profile": "I am interested in machine learning and NLP",
  "discipline": "auto",
  "top_k": 5
}
```

---

# Future Improvements

Potential future improvements include:

* Larger training datasets
* Real-time publication updates
* Citation graph analysis
* Better topic clustering
* Cloud deployment
* User authentication
* GPU inference optimization
* Multi-language support

---

# Authors

Jash Italiya, 
Xiangpeng Deng, 
Christopher Kang


Stevens Institute of Technology

---

# License

This project is intended for academic and educational purposes.
