import os
import logging
from helpers import (
    setup_logger,
    get_all_files,
    get_last_processed,
    update_last_processed,
    read_input,
    save_output,
)
from config import INPUT_DIR, categorize_transactions

def main():
    setup_logger()
    logging.info("===== Starting Incremental File Processor =====")

    try:
        all_files = [f for f, _ in get_all_files(INPUT_DIR)]
        processed_files = get_last_processed()

        files_to_process = [f for f in all_files if f not in processed_files]

        if not files_to_process:
            logging.info("No new files to process.")
            return

        for filename in files_to_process:
            logging.info(f"Processing new file: {filename}")
            filepath = os.path.join(INPUT_DIR, filename)
            df = read_input(filepath)
            df = categorize_transactions(df)
            output = save_output(df, filepath)
            update_last_processed(filename)
            logging.info(f"File processed successfully → {output}")

    except Exception as e:
        logging.error(f"Processing failed: {e}")

    logging.info("===== Job Finished =====")

if __name__ == "__main__":
    main()