
from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_similarity(text_a: str, text_b: str) -> float:
    """Returns cosine similarity between 0 and 1 using sentence embeddings."""
    embeddings = _model.encode([text_a, text_b], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score, 4)

def sentence_level_matches(jd_text: str, resume_text: str, top_k: int = 5):
    """
    Splits resume into sentences/bullets, embeds each, and finds
    the top_k resume sentences most relevant to the JD.
    This is what powers 'explainability' — showing WHICH lines matched.
    """
    resume_sentences = [s.strip() for s in resume_text.split("\n") if len(s.strip()) > 15]
    if not resume_sentences:
        return []

    jd_embedding = _model.encode(jd_text, convert_to_tensor=True)
    resume_embeddings = _model.encode(resume_sentences, convert_to_tensor=True)

    scores = util.cos_sim(jd_embedding, resume_embeddings)[0]
    ranked = sorted(zip(resume_sentences, scores.tolist()), key=lambda x: -x[1])
    return ranked[:top_k]