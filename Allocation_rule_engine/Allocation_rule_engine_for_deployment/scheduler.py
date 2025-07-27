import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from allocation_engine import Allocation_Rule_Engine
from datetime import datetime
import time

log_file_path = r"D:\Projects\Allocation_rule_engine\Allocation_rule_engine_for_deployment\scheduler.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_job():
    try:
        logging.info("Running Allocation Rule Engine job")
        Allocation_Rule_Engine()
        logging.info("Job completed successfully")
    except Exception as e:
        logging.error(f"Job failed: {e}")

def schedule_job():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(run_job, 'cron', hour=9, minute=20)
    scheduler.add_job(run_job, 'cron', minute=10)
    scheduler.start()
    logging.info("Scheduler started and job scheduled.")

if __name__ == "__main__":
    logging.info(f"Service started at {datetime.now()}")
    schedule_job()
    try:
        while True:
            time.sleep(60)  # Keep the script running
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")