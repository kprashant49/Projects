
import json
import os
from typing import Any, Dict, List, Optional
from PyPDF2 import PdfReader

def safe_str(value: Optional[Any]) -> Optional[str]:
    """Convert PDF metadata values to plain strings safely."""
    if value is None:
        return None
    # PyPDF2 may return NameObject/TextStringObject—convert to str
    try:
        return str(value)
    except Exception:
        return None

def extract_metadata(reader: PdfReader) -> Dict[str, Optional[str]]:
    """Extract common metadata fields in a normalized way."""
    info = reader.metadata  # may be None
    if not info:
        return {
            "title": None,
            "author": None,
            "subject": None,
            "creator": None,
            "producer": None,
        }
    # PdfReader.metadata uses keys like '/Title', '/Author' in older versions
    return {
        "title": safe_str(getattr(info, "title", None) or info.get("/Title")),
        "author": safe_str(getattr(info, "author", None) or info.get("/Author")),
        "subject": safe_str(getattr(info, "subject", None) or info.get("/Subject")),
        "creator": safe_str(getattr(info, "creator", None) or info.get("/Creator")),
        "producer": safe_str(getattr(info, "producer", None) or info.get("/Producer")),
    }

def extract_pages_text(reader: PdfReader) -> List[Dict[str, Any]]:
    """Extract text for each page and return a list of page dicts."""
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""  # returns None if no embedded text
        except Exception as e:
            text = f""  # fallback to empty if extraction fails
        pages.append({
            "page_number": i,
            "text": text,
        })
    return pages

def pdf_to_json(pdf_path: str) -> Dict[str, Any]:
    """Convert a PDF to a structured JSON with metadata and per-page text."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)

        # Handle encryption
        is_encrypted = bool(getattr(reader, "is_encrypted", False))
        if is_encrypted:
            # Attempt to decrypt with empty password (common for some PDFs)
            try:
                reader.decrypt("")  # returns 0/1 depending on success on older versions
            except Exception:
                pass  # if decryption fails, we continue but won't get text

        json_obj = {
            "file_name": os.path.basename(pdf_path),
            "is_encrypted": is_encrypted,
            "page_count": len(reader.pages),
            "metadata": extract_metadata(reader),
            "pages": extract_pages_text(reader) if not is_encrypted else [],
        }

        return json_obj

if __name__ == "__main__":
    input_pdf = r"C:\Users\kpras\Desktop\Test_data\Aadhar_1.pdf"
    output_json_path = r"C:\Users\kpras\Desktop\Aadhar.txt"

    data = pdf_to_json(input_pdf)

    # Pretty-print to console
    print(json.dumps(data, ensure_ascii=False, indent=2))
    with open(output_json_path, "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)

    print(f"\nSaved JSON to: {output_json_path}")
