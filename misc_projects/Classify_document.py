#!/usr/bin/env python3
"""
classify_document.py
--------------------
Classifies an Indian identity document from a base64-encoded PDF
and extracts key-value fields — no LLM required.

Supported documents & extracted fields:
  PAN Card         → pan_number, name, father_name, dob
  Aadhaar Card     → aadhaar_number, name, dob, gender, address
  Driving License  → dl_number, name, dob, valid_till, vehicle_classes, address
  Voter ID         → epic_number, name, father_or_husband_name, dob, address, constituency
  Passport         → passport_number, surname, given_name, dob,
                     date_of_issue, date_of_expiry, place_of_birth, nationality

Dependencies:
  pip install pdfplumber pdf2image Pillow pytesseract opencv-python numpy

Usage:
  python classify_document.py --file path/to/doc.pdf
  python classify_document.py --file path/to/doc.pdf --json
  python classify_document.py --file path/to/doc.pdf --debug
  python classify_document.py --base64 "<base64_string>"
  cat encoded.txt | python classify_document.py --stdin
"""

import argparse
import base64
import json
import os
import re
import sys
import tempfile

import cv2
import numpy as np
import pdfplumber

# ── Windows paths (edit if installed elsewhere) ────────────────────────────────
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH   = None   # e.g. r"C:\poppler\Library\bin"


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CLASSIFICATION RULES
# ══════════════════════════════════════════════════════════════════════════════

DOCUMENT_RULES = {
    "PAN Card": {
        "keywords": [
            "permanent account number",
            "income tax department",
            "govt. of india",
            "government of india",
        ],
        "patterns": [
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
            re.compile(r"income\s+tax\s+department", re.IGNORECASE),
        ],
        "threshold": 3,
    },
    "Aadhaar Card": {
        "keywords": [
            "aadhaar", "aadhar", "uidai",
            "unique identification authority",
            "enrolment no", "mera aadhaar",
        ],
        "patterns": [
            re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
            re.compile(r"uidai", re.IGNORECASE),
        ],
        "threshold": 3,
    },
    "Driving License": {
        "keywords": [
            "driving licence", "driving license", "dl no",
            "motor vehicles act", "transport department", "rto",
            "regional transport", "class of vehicle", "validity",
        ],
        "patterns": [
            re.compile(r"\b[A-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{5,7}\b"),
            re.compile(r"driving\s+licen[sc]e", re.IGNORECASE),
        ],
        "threshold": 3,
    },
    "Voter ID": {
        "keywords": [
            "election commission", "electors photo identity card",
            "epic", "electoral roll", "constituency", "assembly",
        ],
        "patterns": [
            re.compile(r"\b[A-Z]{3}[0-9]{7}\b"),
            re.compile(r"election\s+commission\s+of\s+india", re.IGNORECASE),
            re.compile(r"electors?\s+photo\s+identity", re.IGNORECASE),
        ],
        "threshold": 3,
    },
    "Passport": {
        "keywords": [
            "passport", "republic of india", "ministry of external affairs",
            "place of issue", "place of birth", "date of issue",
            "date of expiry", "given name",
        ],
        "patterns": [
            re.compile(r"\b[A-Z][0-9]{7}\b"),
            re.compile(r"P<IND[A-Z<]{39}"),
            re.compile(r"passport\s+no", re.IGNORECASE),
        ],
        "threshold": 3,
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — TEXT EXTRACTION  (pdfplumber → OpenCV-enhanced OCR fallback)
# ══════════════════════════════════════════════════════════════════════════════

def _extract_pdfplumber(pdf_path: str, debug: bool = False) -> str:
    parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if debug:
                print(f"  [pdfplumber] {len(pdf.pages)} page(s) found")
            for i, page in enumerate(pdf.pages):
                t = page.extract_text()
                if debug:
                    print(f"  [pdfplumber] Page {i+1}: {len(t or '')} chars")
                if t:
                    parts.append(t)
    except Exception as e:
        if debug:
            print(f"  [pdfplumber] ERROR: {e}")
    return "\n".join(parts)


def _pdf_to_images(pdf_path: str, dpi: int = 300, debug: bool = False):
    """Convert PDF to list of PIL images via pdf2image."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        if debug:
            print("  [OCR] pdf2image not installed — run: pip install pdf2image")
        return []
    try:
        kwargs = {"dpi": dpi}
        if POPPLER_PATH:
            kwargs["poppler_path"] = POPPLER_PATH
        images = convert_from_path(pdf_path, **kwargs)
        if debug:
            print(f"  [OCR] Converted to {len(images)} image(s) at {dpi} DPI")
        return images
    except Exception as e:
        if debug:
            print(f"  [OCR] pdf2image ERROR: {e}")
        return []


def _preprocess(img_rgb: np.ndarray) -> np.ndarray:
    """
    OpenCV preprocessing — CLAHE contrast enhancement + Otsu threshold.
    Improves OCR accuracy on faded or low-contrast scans.
    """
    gray    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    clahe   = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def _ocr_easyocr(images: list, debug: bool = False) -> str:
    """
    Primary OCR engine: EasyOCR (deep learning based).
    Much more robust than Tesseract on poor quality / low-contrast scans.
    Install: pip install easyocr
    First run downloads ~100MB model — cached after that.
    """
    try:
        import easyocr
    except ImportError:
        if debug:
            print("  [EasyOCR] Not installed — run: pip install easyocr")
        return ""

    if debug:
        print("  [EasyOCR] Loading model (first run downloads ~100MB, cached after)...")

    # gpu=False for CPU-only; set True if you have a CUDA GPU for faster inference
    reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    page_results = []
    for i, pil_img in enumerate(images):
        try:
            img_np    = np.array(pil_img)
            processed = _preprocess(img_np)

            # EasyOCR accepts numpy arrays directly
            detections = reader.readtext(processed, detail=0, paragraph=True)
            text       = "\n".join(detections)

            if debug:
                alpha = len(re.findall(r"[A-Za-z0-9]", text))
                print(f"  [EasyOCR] Page {i+1}: {len(text)} chars, {alpha} alphanumeric")
                print(f"  [EasyOCR] Preview:\n{'─'*50}\n{text[:600]}\n{'─'*50}")

                # Save debug image
                save_path = os.path.abspath(f"debug_page_{i+1}.png")
                pil_img.save(save_path)
                print(f"  [EasyOCR] Raw image saved → {save_path}")

            page_results.append(text)
        except Exception as e:
            if debug:
                print(f"  [EasyOCR] ERROR on page {i+1}: {e}")

    return "\n".join(page_results)


def _ocr_tesseract(images: list, debug: bool = False) -> str:
    """
    Fallback OCR engine: Tesseract.
    Used only if EasyOCR is not installed.
    """
    try:
        import pytesseract
    except ImportError:
        if debug:
            print("  [Tesseract] Not installed — run: pip install pytesseract")
        return ""

    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        if debug:
            print(f"  [Tesseract] Binary: {TESSERACT_PATH}")

    psm_modes   = ["--psm 6 -l eng", "--psm 4 -l eng", "--psm 3 -l eng"]
    page_results = []

    for i, pil_img in enumerate(images):
        img_np    = np.array(pil_img)
        processed = _preprocess(img_np)
        best_text = ""

        for psm in psm_modes:
            try:
                text        = pytesseract.image_to_string(processed, config=psm)
                alpha_count = len(re.findall(r"[A-Za-z0-9]", text))
                if alpha_count > len(re.findall(r"[A-Za-z0-9]", best_text)):
                    best_text = text
            except Exception as e:
                if debug:
                    print(f"  [Tesseract] Error ({psm}): {e}")

        if debug:
            alpha = len(re.findall(r"[A-Za-z0-9]", best_text))
            print(f"  [Tesseract] Page {i+1}: {len(best_text)} chars, {alpha} alphanumeric")
            print(f"  [Tesseract] Preview:\n{'─'*50}\n{best_text[:600]}\n{'─'*50}")

        page_results.append(best_text)

    return "\n".join(page_results)


def _extract_ocr(pdf_path: str, debug: bool = False) -> str:
    """
    OCR pipeline:
      1. Convert PDF → images (pdf2image)
      2. Preprocess with OpenCV (CLAHE + Otsu)
      3. Try EasyOCR first (better accuracy on poor scans)
      4. Fall back to Tesseract if EasyOCR not installed
    """
    images = _pdf_to_images(pdf_path, dpi=300, debug=debug)
    if not images:
        return ""

    # Try EasyOCR first
    try:
        import easyocr  # noqa: F401
        if debug:
            print("  [OCR] Using EasyOCR (primary)")
        text = _ocr_easyocr(images, debug)
        if len(re.findall(r"[A-Za-z0-9]", text)) > 20:
            return text
        if debug:
            print("  [OCR] EasyOCR returned too little text, trying Tesseract...")
    except ImportError:
        if debug:
            print("  [OCR] EasyOCR not installed, falling back to Tesseract")
        if debug:
            print("  [OCR] Tip: pip install easyocr  ← much better for poor scans")

    # Fall back to Tesseract
    if debug:
        print("  [OCR] Using Tesseract (fallback)")
    return _ocr_tesseract(images, debug)


def get_text(pdf_path: str, debug: bool = False) -> str:
    """Try pdfplumber first; fall back to OpenCV+OCR for scanned PDFs."""
    if debug:
        print("\n[Step 1] pdfplumber extraction...")
    text = _extract_pdfplumber(pdf_path, debug)

    if len(text.strip()) >= 30:
        if debug:
            print(f"[Step 1] OK — {len(text)} chars, skipping OCR")
        return text

    if debug:
        print(f"\n[Step 2] Only {len(text.strip())} chars — switching to OCR...")
    ocr_text = _extract_ocr(pdf_path, debug)

    if ocr_text.strip():
        if debug:
            print(f"[Step 2] OCR returned {len(ocr_text)} chars")
        return ocr_text

    if debug:
        print("[Step 2] OCR also returned empty text!")
    return text


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — FIELD EXTRACTION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _find_after_label(text: str, *labels: str, max_chars: int = 60) -> str | None:
    """Return the value on the same line immediately after a label."""
    for label in labels:
        m = re.search(
            re.escape(label) + r"[\s:]*([^\n]{1," + str(max_chars) + r"})",
            text, re.IGNORECASE,
        )
        if m:
            val = m.group(1).strip().strip(":")
            if val:
                return val
    return None


def _find_date(text: str, *labels: str) -> str | None:
    """Find a DD/MM/YYYY or DD-MM-YYYY date near an optional label."""
    date_pat = r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
    for label in labels:
        m = re.search(re.escape(label) + r"[\s:\/]*" + date_pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    m = re.search(date_pat, text)
    return m.group(1) if m else None


def _clean(value: str | None) -> str | None:
    """Strip common OCR noise: pipes, backslashes, extra whitespace."""
    if not value:
        return None
    value = re.sub(r"[|\\]", "", value)
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip() or None


def _clean_name_lines(text: str, blacklist: list[str]) -> list[str]:
    """
    Extract uppercase name-like lines, filtering out document boilerplate.
    Returns lines that are purely alphabetic with 2+ words.
    """
    lines = []
    for line in text.split("\n"):
        cleaned = re.sub(r"[^A-Z\s]", "", line.upper()).strip()
        if len(cleaned.split()) < 2:
            continue
        if any(b in cleaned for b in blacklist):
            continue
        lines.append(cleaned)
    return lines


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — PER-DOCUMENT FIELD EXTRACTORS
# ══════════════════════════════════════════════════════════════════════════════

def extract_pan(text: str) -> dict:
    pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", text)

    dob = _find_date(text, "date of birth", "dob", "birth")
    if not dob:
        # Fallback: first standalone date in document
        m = re.search(r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b", text)
        dob = m.group(1) if m else None

    blacklist = ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA",
                 "PERMANENT", "ACCOUNT", "NUMBER", "SIGNATURE"]
    name_lines = _clean_name_lines(text, blacklist)

    return {
        "pan_number":  _clean(pan_match.group(1)) if pan_match else None,
        "name":        name_lines[0] if len(name_lines) >= 1 else None,
        "father_name": name_lines[1] if len(name_lines) >= 2 else None,
        "dob":         _clean(dob),
    }


def extract_aadhaar(text: str) -> dict:
    aadhaar_match = re.search(r"\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b", text)
    gender_match  = re.search(r"\b(male|female|transgender)\b", text, re.IGNORECASE)

    name = _find_after_label(text, "name")
    dob  = _find_date(text, "date of birth", "dob", "year of birth")

    addr_match = re.search(
        r"address\s*[:\-]?\s*([\s\S]{10,200}?)(?=\d{4}[\s\-]?\d{4}[\s\-]?\d{4}|$)",
        text, re.IGNORECASE,
    )
    address = re.sub(r"\s+", " ", addr_match.group(1)).strip() if addr_match else None

    return {
        "aadhaar_number": _clean(re.sub(r"[\s\-]", "", aadhaar_match.group(1))) if aadhaar_match else None,
        "name":    _clean(name),
        "dob":     _clean(dob),
        "gender":  gender_match.group(1).capitalize() if gender_match else None,
        "address": _clean(address),
    }


def extract_dl(text: str) -> dict:
    dl_match   = re.search(r"\b([A-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{5,7})\b", text)
    name       = _find_after_label(text, "name", "holder name")
    dob        = _find_date(text, "date of birth", "dob", "d.o.b")
    valid_till = _find_date(text, "valid till", "valid upto", "validity", "expiry date")
    address    = _find_after_label(text, "address", "permanent address", max_chars=150)

    cov_match = re.search(
        r"(?:cov|class of vehicle|vehicle class)\s*[:\-]?\s*([A-Z0-9,\s\/]{2,60})",
        text, re.IGNORECASE,
    )
    vehicle_classes = None
    if cov_match:
        vehicle_classes = [v.strip() for v in re.split(r"[,\/\s]+", cov_match.group(1)) if v.strip()]

    return {
        "dl_number":       _clean(dl_match.group(1)) if dl_match else None,
        "name":            _clean(name),
        "dob":             _clean(dob),
        "valid_till":      _clean(valid_till),
        "vehicle_classes": vehicle_classes,
        "address":         _clean(address),
    }


def extract_voter_id(text: str) -> dict:
    epic_match = re.search(r"\b([A-Z]{3}[0-9]{7})\b", text)
    name       = _find_after_label(text, "elector's name", "electors name", "name of elector", "name")
    relative   = _find_after_label(text, "father's name", "father name",
                                   "husband's name", "husband name", "s/o", "w/o", "d/o")
    dob        = _find_date(text, "date of birth", "dob")
    address    = _find_after_label(text, "address", max_chars=150)
    const      = _find_after_label(text, "constituency", "assembly constituency", max_chars=80)

    return {
        "epic_number":            _clean(epic_match.group(1)) if epic_match else None,
        "name":                   _clean(name),
        "father_or_husband_name": _clean(relative),
        "dob":                    _clean(dob),
        "address":                _clean(address),
        "constituency":           _clean(const),
    }


def extract_passport(text: str) -> dict:
    result = {k: None for k in [
        "passport_number", "surname", "given_name", "dob",
        "date_of_issue", "date_of_expiry", "place_of_birth", "nationality",
    ]}

    # MRZ line 1: P<IND<SURNAME<<GIVEN<NAMES...
    mrz1 = re.search(r"(P<IND[A-Z<]{39})", text)
    # MRZ line 2: passport_no + nationality + dob + sex + expiry
    mrz2 = re.search(r"([A-Z0-9<]{9}[0-9]IND[0-9]{7}[MF<][0-9]{7}[A-Z0-9<]{14}[0-9])", text)

    if mrz1:
        parts = [p for p in mrz1.group(1)[5:].split("<<") if p]
        if parts:
            result["surname"]    = parts[0].replace("<", " ").strip()
        if len(parts) > 1:
            result["given_name"] = parts[1].replace("<", " ").strip()

    if mrz2:
        line = mrz2.group(1)
        result["passport_number"] = line[:9].replace("<", "").strip()
        result["dob"]             = _yymmdd_to_date(line[13:19])
        result["date_of_expiry"]  = _yymmdd_to_date(line[21:27])

    # Labeled field fallbacks
    if not result["passport_number"]:
        m = re.search(r"passport\s*(?:no|number)\s*[:\-]?\s*([A-Z][0-9]{7})", text, re.IGNORECASE)
        result["passport_number"] = m.group(1) if m else None
    if not result["surname"]:
        result["surname"]    = _clean(_find_after_label(text, "surname", "last name"))
    if not result["given_name"]:
        result["given_name"] = _clean(_find_after_label(text, "given name", "given names", "first name"))
    if not result["dob"]:
        result["dob"]        = _clean(_find_date(text, "date of birth", "dob"))
    if not result["date_of_expiry"]:
        result["date_of_expiry"] = _clean(_find_date(text, "date of expiry", "expiry"))

    result["date_of_issue"]  = _clean(_find_date(text, "date of issue", "issue date"))
    result["place_of_birth"] = _clean(_find_after_label(text, "place of birth"))
    result["nationality"]    = _clean(_find_after_label(text, "nationality"))

    return result


def _yymmdd_to_date(yymmdd: str) -> str | None:
    if len(yymmdd) != 6 or not yymmdd.isdigit():
        return None
    yy, mm, dd = int(yymmdd[:2]), yymmdd[2:4], yymmdd[4:]
    full_year  = 2000 + yy if yy <= 30 else 1900 + yy
    return f"{dd}/{mm}/{full_year}"


EXTRACTORS = {
    "PAN Card":        extract_pan,
    "Aadhaar Card":    extract_aadhaar,
    "Driving License": extract_dl,
    "Voter ID":        extract_voter_id,
    "Passport":        extract_passport,
}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — SCORING & CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def score_text(text: str, debug: bool = False) -> dict:
    lowered = text.lower()
    scores  = {}
    for doc_type, rules in DOCUMENT_RULES.items():
        score  = sum(1 for kw  in rules["keywords"] if kw.lower() in lowered)
        score += sum(2 for pat in rules["patterns"]  if pat.search(text))
        scores[doc_type] = score
        if debug and score > 0:
            matched_kw  = [kw for kw in rules["keywords"] if kw.lower() in lowered]
            matched_pat = [p.pattern for p in rules["patterns"] if p.search(text)]
            print(f"  [{doc_type}] score={score}  kw={matched_kw}  regex={matched_pat}")
    return scores


def classify(scores: dict) -> tuple[str, str]:
    """Returns (document_type, confidence)."""
    best_type  = max(scores, key=scores.get)
    best_score = scores[best_type]
    threshold  = DOCUMENT_RULES[best_type]["threshold"]

    if best_score < threshold:
        return "Unknown", "Low"

    gap        = best_score - threshold
    confidence = "High" if gap >= 4 else ("Medium" if gap >= 2 else "Low")
    return best_type, confidence


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def classify_from_base64(pdf_base64: str, debug: bool = False) -> dict:
    """
    Main entry point. Accepts a base64-encoded PDF string.

    Returns:
    {
        "document_type":    "PAN Card",
        "confidence":       "High",
        "scores":           { "PAN Card": 7, ... },
        "extracted_fields": { "pan_number": "ABCDE1234F", ... }
    }
    """
    pdf_bytes = base64.b64decode(pdf_base64)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        text = get_text(tmp_path, debug)

        if not text.strip():
            return {
                "document_type":    "Unknown",
                "confidence":       "Low",
                "scores":           {},
                "extracted_fields": {},
                "reason":           "Could not extract any text from the PDF.",
            }

        if debug:
            print(f"\n[Step 3] Scoring {len(text)} chars of text...")

        scores             = score_text(text, debug)
        doc_type, confid   = classify(scores)
        extractor          = EXTRACTORS.get(doc_type)

        return {
            "document_type":    doc_type,
            "confidence":       confid,
            "scores":           scores,
            "extracted_fields": extractor(text) if extractor else {},
        }
    finally:
        os.unlink(tmp_path)


def classify_from_file(pdf_path: str, debug: bool = False) -> dict:
    """Convenience wrapper: reads a PDF file and classifies it."""
    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return classify_from_base64(b64, debug)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — CLI
# ══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Classify Indian ID documents + extract fields (no LLM).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--base64", metavar="B64",  help="Base64-encoded PDF string.")
    src.add_argument("--file",   metavar="PATH", help="Path to a PDF file.")
    src.add_argument("--stdin",  action="store_true", help="Read base64 from stdin.")
    p.add_argument("--json",    action="store_true", dest="json_output",
                   help="Output raw JSON.")
    p.add_argument("--verbose", action="store_true",
                   help="Show score breakdown for all document types.")
    p.add_argument("--debug",   action="store_true",
                   help="Show step-by-step extraction details.")
    return p


def _pretty_print(result: dict, verbose: bool = False) -> None:
    print("\n┌──────────────────────────────────────────────┐")
    print("│        Document Classification Result         │")
    print("└──────────────────────────────────────────────┘")
    print(f"  Document Type : {result['document_type']}")
    print(f"  Confidence    : {result['confidence']}")

    fields = result.get("extracted_fields", {})
    if fields:
        print("\n  Extracted Fields:")
        for key, val in fields.items():
            if val is None:
                continue
            if isinstance(val, list):
                val = ", ".join(val)
            print(f"    {key:<25} {val}")

    if verbose:
        print("\n  Score Breakdown:")
        for dtype, s in sorted(result.get("scores", {}).items(), key=lambda x: -x[1]):
            thr = DOCUMENT_RULES.get(dtype, {}).get("threshold", "?")
            bar = "█" * s
            print(f"    {dtype:<22} {bar:<15}  score={s}  threshold={thr}")
    print()


def main():
    args = build_parser().parse_args()

    if args.base64:
        b64 = args.base64.strip()
    elif args.file:
        if not os.path.isfile(args.file):
            print(f"Error: file not found — {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
    else:
        b64 = sys.stdin.read().strip()

    if not b64:
        print("Error: empty input.", file=sys.stderr)
        sys.exit(1)

    result = classify_from_base64(b64, debug=args.debug)

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _pretty_print(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
