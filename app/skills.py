
import re
import spacy
from spacy.matcher import PhraseMatcher
from rapidfuzz import fuzz, process

nlp = spacy.load("en_core_web_sm")

SKILL_TAXONOMY = [
    "python", "sql", "excel", "tableau", "power bi", "machine learning",
    "pandas", "numpy", "scikit-learn", "git", "data analysis",
    "data visualization", "fastapi", "docker", "react", "typescript",
]

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in SKILL_TAXONOMY]
matcher.add("SKILLS", patterns)


def normalize_camel_case(text: str) -> str:
    """
    Inserts a space before capital letters that follow lowercase letters.
    'PowerBi' -> 'Power Bi', 'scikitLearn' -> 'scikit Learn'
    This alone fixes most camelCase misses before exact matching runs.
    """
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)


def extract_skills_exact(text: str) -> set[str]:
    """Your original exact/token-based matcher, returned as a set."""
    doc = nlp(text)
    matches = matcher(doc)
    return {doc[start:end].text.lower() for _, start, end in matches}


def extract_skills_fuzzy(text: str, threshold: int = 85) -> set[str]:
    """
    Fuzzy fallback: breaks text into candidate n-grams (1-2 words) and
    checks each against the skill taxonomy using similarity scoring.
    Catches typos, hyphenation, spacing variants that exact matching misses.
    """
    
    tokens = [t.text for t in nlp(text) if not t.is_punct and not t.is_space]
    candidates = set(tokens)  # single words
    candidates.update(
        f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)
    )  

    found = set()
    for candidate in candidates:
        
        best_match = process.extractOne(
            candidate.lower(),
            SKILL_TAXONOMY,
            scorer=fuzz.token_sort_ratio,
        )
        if best_match and best_match[1] >= threshold:
            found.add(best_match[0])  
    return found


def extract_skills(text: str) -> list[str]:
    """
    Hybrid pipeline:
    1. Normalize camelCase so 'PowerBi' becomes 'Power Bi'
    2. Run exact PhraseMatcher (fast, zero false positives)
    3. Run fuzzy matching as a fallback to catch what exact missed
    4. Merge and return sorted, deduplicated results
    """
    normalized_text = normalize_camel_case(text)

    exact_found = extract_skills_exact(normalized_text)
    fuzzy_found = extract_skills_fuzzy(normalized_text)

    combined = exact_found | fuzzy_found 
    return sorted(combined)