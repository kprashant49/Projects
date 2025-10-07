import logging
from helpers import (
    setup_logger,
    get_latest_file,
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
        latest_path = get_latest_file(INPUT_DIR)
        latest_name = latest_path.split("\\")[-1]
        last_processed = get_last_processed()

        if latest_name == last_processed:
            logging.info(f"No new file to process. Last processed: {latest_name}")
            return

        logging.info(f"New file detected: {latest_name}")
        df = read_input(latest_path)
        df = categorize_transactions(df)
        output = save_output(df, latest_path)
        update_last_processed(latest_name)
        logging.info(f"File processed successfully → {output}")

    except Exception as e:
        logging.error(f"Processing failed: {e}")

    logging.info("===== Job Finished =====")

if __name__ == "__main__":
    main()
