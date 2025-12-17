import base64
import os

# Common Base64 signatures for file types
FILE_SIGNATURES = {
    "/9j/": ".jpg",        # JPEG
    "iVBORw0KGgo": ".png", # PNG
    "JVBER": ".pdf",       # PDF
    "UEsDB": ".xlsx",      # XLSX (ZIP-based)
    "0M8R4KGx": ".xls",    # XLS (binary)
    "Q29sdW1u": ".csv"     # CSV (text-based)
}

def detect_file_type(encoded_data):
    for signature, ext in FILE_SIGNATURES.items():
        if encoded_data.startswith(signature):
            return ext
    return None  # Unknown type

def encode_file_to_base64(file_path):
    output_txt = os.path.splitext(file_path)[0] + ".txt"
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    with open(output_txt, "w") as f:
        f.write(encoded)
    print(f"Encoded → {output_txt}")

def decode_base64_to_file(txt_path):
    with open(txt_path, "r") as f:
        encoded = f.read()

    # Try to detect type from Base64 header
    detected_ext = detect_file_type(encoded)

    # Fallback: use original extension if detection fails
    original_ext = os.path.splitext(txt_path)[0].split("_")[-1]  # e.g., "file_pdf.txt"
    if not detected_ext:
        print(f"Could not detect type from Base64. Using fallback: .{original_ext}")
        detected_ext = "." + original_ext if original_ext else ".bin"

    output_file = os.path.splitext(txt_path)[0] + detected_ext
    with open(output_file, "wb") as f:
        f.write(base64.b64decode(encoded))
    print(f"Decoded → {output_file} (Type: {detected_ext})")

def auto_process(input_path):
    if not os.path.isfile(input_path):
        print("File not found.")
        return

    ext = os.path.splitext(input_path)[1].lower()

    if ext in [".pdf", ".png", ".jpeg", ".jpg", ".xls", ".xlsx", ".csv"]:
        encode_file_to_base64(input_path)

    elif ext == ".txt":
        decode_base64_to_file(input_path)

    else:
        print("Unsupported file type.")

if __name__ == "__main__":
    print(">>>>Welcome to Base64 Encoder/Decoder<<<<")
    print("Supported files type >>> .pdf,.png,.jpg,.xls,.xlsx,.csv or.txt")
    path = input("Enter file path: ").strip()
    auto_process(path)