"""Parses uploaded pitch decks / documents into plain text (blueprint FR-02).

Supports PDF, DOCX and plain text/markdown/CSV. Anything else is skipped rather than guessed at.
"""

import io

from docx import Document
from pypdf import PdfReader

MAX_CHARS_PER_DOC = 6000


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    try:
        if lower.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        elif lower.endswith(".docx"):
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
        elif lower.endswith((".txt", ".md", ".csv")):
            text = content.decode("utf-8", errors="ignore")
        else:
            return ""
    except Exception:
        return ""
    return text.strip()[:MAX_CHARS_PER_DOC]
