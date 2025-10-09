import os
import logging
import pandas as pd
from logging.handlers import RotatingFileHandler
from config import OUTPUT_DIR, LOG_DIR, LOG_FILE, SHEET_NAME

# ---------------- LOGGING SETUP ----------------
def setup_logger():
    """Rotating logger."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_path = os.path.join(LOG_DIR, "process.log")

    # Rotating file handler
    rotating_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,   # 1 MB
        backupCount=5,
        encoding='utf-8'
    )

    # Console handler
    console_handler = logging.StreamHandler()

    # Logger format
    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Format application to both handlers
    rotating_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Root logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized — using rotating log file.")

# ---------------- FILE UTILITIES ----------------
def get_last_processed():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def update_last_processed(filename):
    with open(LOG_FILE, "a") as f:
        f.write(f"{filename}\n")

def get_all_files(folder):
    files = [f for f in os.listdir(folder)
             if f.lower().endswith(('.csv', '.xls', '.xlsx'))]
    files_with_mtime = [
        (f, os.path.getmtime(os.path.join(folder, f))) for f in files
    ]
    return sorted(files_with_mtime, key=lambda x: x[1])

# ---------------- FILE I/O ----------------
def read_input(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return pd.read_csv(filepath)
    elif ext == ".xls":
        return pd.read_excel(filepath, sheet_name=SHEET_NAME, engine="xlrd")
    else:
        return pd.read_excel(filepath, sheet_name=SHEET_NAME, engine="openpyxl")

def save_output(df, input_path):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base}_processed.xlsx")

    df.to_excel(output_path, index=False, engine="openpyxl")
    return output_path
