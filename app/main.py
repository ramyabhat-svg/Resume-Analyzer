# app/main.py
from fastapi import FastAPI, UploadFile, File, Form
from app.parser import extract_text_from_pdf, split_into_sections
from app.scorer import semantic_similarity, sentence_level_matches
from app.skills import extract_skills
import io
app = FastAPI(title="Resume Analyzer API")

@app.post("/analyze")
async def analyze(job_description: str = Form(...), resume: UploadFile = File(...)):
    pdf_bytes = await resume.read()
    resume_text = extract_text_from_pdf(io.BytesIO(pdf_bytes))
    sections = split_into_sections(resume_text)

    overall_score = semantic_similarity(job_description, resume_text)
    jd_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)
    missing_skills = [s for s in jd_skills if s not in resume_skills]
    top_matches = sentence_level_matches(job_description, resume_text)

    return {
        "match_score_percent": round(overall_score * 100, 2),
        "jd_skills": jd_skills,
        "resume_skills": resume_skills,
        "missing_skills": missing_skills,
        "top_matching_lines": [{"line": line, "score": round(score, 3)} for line, score in top_matches],
        "sections_detected": list(sections.keys()),
    }

@app.get("/health")
def health():
    return {"status": "ok"}