# Resume Analyzer — Semantic Match & Skill Gap Detector

A FastAPI service that compares a resume against a job description using
sentence-embedding semantic similarity, and highlights which required
skills are missing. Originally built as a TF-IDF + cosine similarity
notebook prototype (preserved in [`legacy/`](./legacy)); rebuilt as a
full backend service with semantic matching, hybrid skill extraction,
and test coverage.

<!-- 🔗 Live demo: ADD_DEPLOYED_URL_HERE/docs -->

## What it does

Given a job description and a resume (PDF), the API returns:
- An overall **semantic match score** between the JD and resume
- Skills detected in the JD vs. skills detected in the resume
- **Missing skills** — JD requirements not found in the resume
- The **top matching resume lines** for the JD, with similarity scores (explainability — shows *why* the score is what it is, not just the number)
- Detected resume sections (education, skills, projects, etc.)

## Why it's built this way

The original prototype used TF-IDF + cosine similarity, which only
matches exact words — it would miss "ML" vs. "Machine Learning" or
"built REST services" vs. "developed APIs". This version uses:

- **Sentence embeddings** (`all-MiniLM-L6-v2` via `sentence-transformers`)
  for semantic similarity instead of keyword overlap
- **Hybrid skill extraction**: an exact token-based matcher (spaCy
  `PhraseMatcher`) first, with a fuzzy fallback (`rapidfuzz`) to catch
  variants like `PowerBi`, `Power-BI`, or minor typos that exact
  matching misses
- **Section-aware parsing** so matches can eventually be weighted by
  where they appear in the resume, rather than treating it as one flat
  blob of text

## Architecture

```
Client (Swagger UI / curl / frontend)
        │
        ▼
   FastAPI (app/main.py)
        │
        ├── parser.py   → extracts text from PDF, splits into sections
        ├── scorer.py   → sentence-transformer embeddings, semantic
        │                 similarity, sentence-level match ranking
        └── skills.py   → spaCy PhraseMatcher (exact) + rapidfuzz
                           (fuzzy fallback) skill extraction
```

## Project structure

```
.
├── app/
│   ├── main.py        # FastAPI app and /analyze, /health routes
│   ├── parser.py       # PDF text extraction + section splitting
│   ├── scorer.py       # Semantic similarity + sentence-level matching
│   └── skills.py        # Exact + fuzzy skill extraction
├── tests/
│   └── test_skills.py  # Unit tests for skill extraction
├── legacy/
│   └── resume_analyzer_v1.ipynb   # Original TF-IDF notebook prototype
├── requirements.txt
├── Dockerfile
└── README.md
```

## Tech stack

Python · FastAPI · sentence-transformers · spaCy · rapidfuzz · pypdf ·
pytest · Docker

## Running locally

```bash
# Clone and enter the repo
git clone https://github.com/ramyabhat-svg/Resume-Analyzer-using-TF-IDF-Cosine-Similarity.git
cd Resume-Analyzer-using-TF-IDF-Cosine-Similarity

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run the server
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

## Running with Docker

```bash
docker build -t resume-analyzer .
docker run -p 8000:8000 resume-analyzer
```

## API

### `POST /analyze`

**Form data:**
| Field | Type | Description |
|---|---|---|
| `job_description` | string | The job description text |
| `resume` | file (PDF) | The resume to analyze |

**Example response:**
```json
{
  "match_score_percent": 51.17,
  "jd_skills": ["python", "sql", "git", "fastapi", "docker", "react"],
  "resume_skills": ["python", "sql", "git", "pandas", "numpy"],
  "missing_skills": ["fastapi", "docker", "react"],
  "top_matching_lines": [
    { "line": "Programming Languages: Python, SQL, FastAPI", "score": 0.42 }
  ],
  "sections_detected": ["education", "skills", "projects"]
}
```

### `GET /health`
Basic liveness check — returns `{"status": "ok"}`.

## Testing

```bash
pytest tests/ -v
```

## Known limitations

- Fuzzy skill matching trades precision for recall — very short skill
  names (e.g. "R", "Git") are harder to fuzzy-match safely without
  false positives, so the match threshold is tuned conservatively.
- Section parsing is heuristic (regex/keyword-based), not layout-aware
  — unconventional resume formats may not split perfectly into
  sections.
- Semantic similarity scores between a formal JD and a bulleted resume
  are naturally lower than a document-to-document comparison would be;
  scores are best read comparatively (across JDs or resumes) rather
  than as an absolute percentage.

## Roadmap

- Deploy as a public live demo (AWS App Runner)
- Optional lightweight frontend (Streamlit) calling the API
- Per-skill similarity scoring, not just found/missing
