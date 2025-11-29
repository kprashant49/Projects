import base64
import os

def encode_pdf_to_base64(pdf_path):
    output_txt = os.path.splitext(pdf_path)[0] + ".txt"
    with open(pdf_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    with open(output_txt, "w") as f:
        f.write(encoded)
    print(f"Encoded → {output_txt}")

def decode_base64_to_pdf(txt_path):
    output_pdf = os.path.splitext(txt_path)[0] + ".pdf"
    with open(txt_path, "r") as f:
        encoded = f.read()
    with open(output_pdf, "wb") as f:
        f.write(base64.b64decode(encoded))
    print(f"Decoded → {output_pdf}")

def auto_process(input_path):
    ext = os.path.splitext(input_path)[1].lower()

    if ext == ".pdf":
        encode_pdf_to_base64(input_path)

    elif ext == ".txt":
        decode_base64_to_pdf(input_path)

    else:
        print("Only .pdf or .txt supported.")

if __name__ == "__main__":
    input_file = r"C:\Users\kpras\Desktop\test.txt"
    auto_process(input_file)
