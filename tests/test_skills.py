# tests/test_skills.py
from app.skills import extract_skills

def test_extract_skills_finds_known_terms():
    text = "Experienced in Python, SQL and Power BI dashboards."
    result = extract_skills(text)
    assert "python" in result
    assert "sql" in result
    assert "power bi" in result

def test_extract_skills_ignores_irrelevant_words():
    text = "I enjoy hiking and photography."
    result = extract_skills(text)
    assert result == []