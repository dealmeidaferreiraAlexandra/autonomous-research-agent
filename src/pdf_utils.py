from __future__ import annotations

from typing import Any, Dict, List

from pypdf import PdfReader


def extract_pdf_text(uploaded_file) -> str:
    uploaded_file.seek(0)
    reader = PdfReader(uploaded_file)
    pages: List[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages).strip()


def extract_many_pdfs(files) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    for file_obj in files or []:
        try:
            text = extract_pdf_text(file_obj)
        except Exception:
            text = ""

        docs.append(
            {
                "name": file_obj.name,
                "text": text,
            }
        )

    return docs