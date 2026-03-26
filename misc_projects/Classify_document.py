#!/usr/bin/env python3

import argparse
import base64
import json
import os
import re
import tempfile

import pdfplumber
import cv2
import numpy as np

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = None

# ═══════════════════════════════════════════════════════
# RULES
# ═══════════════════════════════════════════════════════

DOCUMENT_RULES = {
    "PAN Card": {
        "keywords": ["income tax", "permanent account number"],
        "patterns": [re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")],
        "threshold": 2,
    },
    "Aadhaar Card": {
        "keywords": ["aadhaar", "uidai"],
        "patterns": [re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")],
        "threshold": 2,
    },
    "Driving License": {
        "keywords": ["driving licence", "transport"],
        "patterns": [re.compile(r"\b[A-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{5,7}\b")],
        "threshold": 2,
    },
    "Voter ID": {
        "keywords": ["election commission"],
        "patterns": [re.compile(r"\b[A-Z]{3}[0-9]{7}\b")],
        "threshold": 2,
    },
    "Passport": {
        "keywords": ["passport", "republic of india"],
        "patterns": [re.compile(r"\b[A-Z][0-9]{7}\b")],
        "threshold": 2,
    },
}

# ═══════════════════════════════════════════════════════
# OCR
# ═══════════════════════════════════════════════════════

def extract_text(pdf_path, debug=False):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t
    except:
        pass

    if len(text.strip()) > 30:
        return text

    if debug:
        print("[Using OCR]")

    from pdf2image import convert_from_path
    import pytesseract

    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    images = convert_from_path(pdf_path, dpi=400)

    result = []

    for img in images:
        img = np.array(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        denoise = cv2.medianBlur(thresh, 3)

        text = pytesseract.image_to_string(denoise, config="--psm 6")
        result.append(text)

    full_text = "\n".join(result)

    if debug:
        print("\n[TEXT]")
        print(full_text[:1000])

    return full_text


# ═══════════════════════════════════════════════════════
# CLASSIFICATION
# ═══════════════════════════════════════════════════════

def score_text(text):
    text_l = text.lower()
    scores = {}

    for k, rule in DOCUMENT_RULES.items():
        score = 0
        score += sum(1 for kw in rule["keywords"] if kw in text_l)
        score += sum(2 for p in rule["patterns"] if p.search(text))
        scores[k] = score

    return scores


def classify(scores):
    best = max(scores, key=scores.get)
    if scores[best] < DOCUMENT_RULES[best]["threshold"]:
        return "Unknown"
    return best


# ═══════════════════════════════════════════════════════
# FIELD EXTRACTION
# ═══════════════════════════════════════════════════════

def clean_lines(text):
    lines = [
        re.sub(r"[^A-Z\s]", "", l).strip()
        for l in text.split("\n")
    ]
    return [l for l in lines if len(l.split()) >= 2]


# PAN
def extract_pan(text):
    result = {
        "name": None,
        "father_name": None,
        "pan_number": None,
        "dob": None,
    }

    # PAN number
    pan = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
    if pan:
        result["pan_number"] = pan.group(0)

    # DOB patterns (robust)
    dob_patterns = [
        r"\b\d{2}[\/\-]\d{2}[\/\-]\d{4}\b",   # 01/01/1990
        r"\b\d{2}[\/\-]\d{2}[\/\-]\d{2}\b",   # 01/01/90
    ]

    for pat in dob_patterns:
        m = re.search(pat, text)
        if m:
            result["dob"] = m.group(0)
            break

    # Clean lines
    lines = [
        re.sub(r"[^A-Z\s]", "", l).strip()
        for l in text.split("\n")
    ]
    lines = [l for l in lines if len(l.split()) >= 2]

    blacklist = ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA", "SIGNATURE"]

    clean_lines = [
        l for l in lines
        if not any(b in l for b in blacklist)
    ]

    if len(clean_lines) >= 1:
        result["name"] = clean_lines[0]

    if len(clean_lines) >= 2:
        result["father_name"] = clean_lines[1]

    return result


# Aadhaar
def extract_aadhaar(text):
    aadhaar = re.search(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", text)

    return {
        "aadhaar_number": aadhaar.group(0).replace(" ", "") if aadhaar else None,
        "name": clean_lines(text)[0] if clean_lines(text) else None,
    }


# DL
def extract_dl(text):
    dl = re.search(r"\b[A-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{5,7}\b", text)

    return {
        "dl_number": dl.group(0) if dl else None,
    }


# Voter ID
def extract_voter(text):
    epic = re.search(r"\b[A-Z]{3}[0-9]{7}\b", text)

    return {
        "voter_id": epic.group(0) if epic else None,
    }


# Passport
def extract_passport(text):
    passport = re.search(r"\b[A-Z][0-9]{7}\b", text)

    return {
        "passport_number": passport.group(0) if passport else None,
    }


EXTRACTORS = {
    "PAN Card": extract_pan,
    "Aadhaar Card": extract_aadhaar,
    "Driving License": extract_dl,
    "Voter ID": extract_voter,
    "Passport": extract_passport,
}

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def classify_file(file_path, debug=False):
    text = extract_text(file_path, debug)

    scores = score_text(text)
    doc_type = classify(scores)

    fields = {}
    if doc_type in EXTRACTORS:
        fields = EXTRACTORS[doc_type](text)

    return {
        "document_type": doc_type,
        "scores": scores,
        "extracted_fields": fields
    }


# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    result = classify_file(args.file, args.debug)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\nRESULT\n" + "=" * 40)
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()