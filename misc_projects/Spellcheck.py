import re
import enchant


def spell_check_pipeline(input_text: str):
    # Use British English (closer to Indian usage)
    d = enchant.Dict("en_GB")

    # Custom allowed words (same as your R script)
    custom_words = [
        "MIDC", "SEZ", "Taluka", "Emp", "Aadhar", "UAN",
        "YTD", "TDS", "CamScanner", "LPL", "TFM", "INR",
        "HRA", "LTA"
    ]

    # Step 1: Remove numbers
    text_clean = re.sub(r"[0-9]+", " ", input_text)

    # Step 2: Tokenize
    words = re.findall(r'\b\w+\b', text_clean)

    # Step 3: Identify misspelled words
    wrong_words = []
    for w in words:
        if w in custom_words:
            continue
        if not d.check(w):
            wrong_words.append(w)

    # Step 4: Unique
    wrong_words = list(set(wrong_words))

    # Step 5: Length > 2
    wrong_words = [w for w in wrong_words if len(w) > 2]

    # Step 6: Must contain vowel
    wrong_words = [
        w for w in wrong_words
        if re.search(r"[aeiouAEIOU]", w)
    ]

    # Step 7: Uppercase / lowercase logic
    uppercase_words = [w for w in wrong_words if w.isupper() and len(w) > 3]
    lowercase_words = [w for w in wrong_words if not w.isupper()]

    final_list = uppercase_words + lowercase_words

    return final_list


# Example usage
if __name__ == "__main__":
    import sys

    input_text = sys.argv[1] if len(sys.argv) > 1 else "Sample MIDC text with wrongg wordd and INR 5000"

    result = spell_check_pipeline(input_text)
    print(result)