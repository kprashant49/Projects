import streamlit as st
import base64
import os

# Base64 signatures for type detection during decode
FILE_SIGNATURES = {
    "/9j/": ".jpg",
    "iVBORw0KGgo": ".png",
    "JVBER": ".pdf",
    "UEsDB": ".xlsx",
    "0M8R4KGx": ".xls",
    "Q29sdW1u": ".csv"
}

def detect_file_type(encoded_data: str) -> str:
    for signature, ext in FILE_SIGNATURES.items():
        if encoded_data.startswith(signature):
            return ext
    return ".bin"

# ---------------- UI ---------------- #
st.set_page_config(page_title="Base64 Encoder / Decoder", layout="centered")
st.title("Base64 Encoder / Decoder")

mode = st.radio("Choose Operation", ["Encode", "Decode"])

uploaded_file = st.file_uploader(
    "Upload file",
    type=["pdf", "png", "jpg", "jpeg", "xls", "xlsx", "csv", "txt"]
)

# ---------------- ENCODE ---------------- #
if uploaded_file and mode == "Encode":
    original_name, _ = os.path.splitext(uploaded_file.name)

    raw_bytes = uploaded_file.read()
    encoded = base64.b64encode(raw_bytes).decode("utf-8")

    st.success("File encoded successfully")
    st.text_area("Base64 Output", encoded, height=220)

    st.download_button(
        label="Download Base64 (.txt)",
        data=encoded,
        file_name=f"{original_name}_base64.txt",
        mime="text/plain"
    )

# ---------------- DECODE ---------------- #
elif uploaded_file and mode == "Decode":
    original_name, _ = os.path.splitext(uploaded_file.name)

    encoded_text = uploaded_file.read().decode("utf-8")
    detected_ext = detect_file_type(encoded_text)

    decoded_bytes = base64.b64decode(encoded_text)

    st.success(f"File decoded successfully ({detected_ext})")

    st.download_button(
        label="Download Decoded File",
        data=decoded_bytes,
        file_name=f"{original_name}{detected_ext}",
        mime="application/octet-stream"
    )
