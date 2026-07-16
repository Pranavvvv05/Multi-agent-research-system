"""
ui/document_reader.py
----------------------
Extracts plain text from an uploaded PDF / DOCX / TXT file so it can be
handed to the agent pipeline as the source document. This runs on the
frontend regardless of whether graph/workflow.py exists yet — reading
an upload isn't agent logic, so there's no "demo mode" for it.

Requires: pypdf, python-docx (add to requirements.txt if not present).
"""

import io


def extract_text(uploaded_file) -> str:
    """uploaded_file: a Streamlit UploadedFile (from st.file_uploader)."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise RuntimeError("Install pypdf to read PDF files: pip install pypdf") from e

        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # ── DEBUG: confirm whether extraction actually got real text ──
        print(f"DEBUG: PDF '{uploaded_file.name}' — {len(reader.pages)} page(s), "
              f"{len(text)} char(s) extracted.")
        print("DEBUG: PDF TEXT SAMPLE (first 300 chars):", repr(text[:300]))

        if len(text.strip()) < 20:
            # Almost nothing came out — very likely a scanned/image-only
            # PDF with no embedded text layer, which pypdf can't read.
            print(
                "DEBUG WARNING: Extracted text is nearly empty. This PDF is "
                "likely scanned/image-based and has no selectable text layer — "
                "pypdf cannot OCR it. An OCR step (e.g. pytesseract) would be "
                "needed to handle this file."
            )

        return text

    if name.endswith(".docx"):
        try:
            import docx
        except ImportError as e:
            raise RuntimeError("Install python-docx to read DOCX files: pip install python-docx") from e
        document = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")