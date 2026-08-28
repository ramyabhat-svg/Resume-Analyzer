
import re
import pypdf  

SECTION_HEADERS = ["education", "experience", "projects", "skills", "certifications"]

def extract_text_from_pdf(file_path_or_bytes) -> str:
    """Extract raw text from a PDF file path or file-like object."""
    reader = pypdf.PdfReader(file_path_or_bytes)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def split_into_sections(text: str) -> dict:
    """
    section splitter: finds section header lines and groups
    everything until the next header under that section.
    """
    lines = text.split("\n")
    sections = {"other": []}
    current = "other"

    for line in lines:
        clean_line = line.strip().lower()
        matched_header = None
        for header in SECTION_HEADERS:
            
            if header in clean_line and len(clean_line) < 30:
                matched_header = header
                break
        if matched_header:
            current = matched_header
            sections.setdefault(current, [])
        else:
            sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}