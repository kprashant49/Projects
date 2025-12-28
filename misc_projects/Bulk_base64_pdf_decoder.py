import streamlit as st
import json
import base64
import os

st.set_page_config(page_title="JSON Base64 → PDF Decoder", layout="centered")

st.title("Bulk Base64 → PDF Decoder")

# Upload JSON
uploaded_file = st.file_uploader(
    "Upload JSON file",
    type=["json"]
)

# Output directory
output_dir = st.text_input(
    "Final output folder path",
    placeholder="e.g. C:/Users/Prashant/Documents/output"
)

if uploaded_file and output_dir:
    if not os.path.exists(output_dir):
        st.error("Output directory does not exist")
        st.stop()

    try:
        data = json.load(uploaded_file)

        if not isinstance(data, list):
            st.error("JSON must be a list of objects")
            st.stop()

        if st.button("Decode PDFs"):
            success = 0
            failed = 0

            for item in data:
                try:
                    filename = item["ApplicationNo"].strip() + ".pdf"
                    b64_data = item["vendor_pdf"].strip()

                    pdf_bytes = base64.b64decode(b64_data)
                    output_path = os.path.join(output_dir, filename)

                    with open(output_path, "wb") as f:
                        f.write(pdf_bytes)

                    success += 1
                except Exception:
                    failed += 1

            st.success(f"PDFs created: {success}")
            if failed:
                st.warning(f"Failed records: {failed}")

    except Exception as e:
        st.error(f"Invalid JSON file: {e}")
