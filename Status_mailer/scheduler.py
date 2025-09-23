import logging
from logging.handlers import RotatingFileHandler
import os
from apscheduler.schedulers.background import BackgroundScheduler
from status_mailer import status_mailer
from datetime import datetime
import time

log_file_path = r"D:\Projects\Status_mailer\scheduler.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set up rotating file handler
handler = RotatingFileHandler(log_file_path, maxBytes=1 * 1024 * 1024, backupCount=5)  # 1 MB
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info("Scheduler started at " + str(datetime.now()))

def run_job():
    try:
        logger.info("Running Status mailer job")
        status_mailer()
        logger.info("Job completed successfully")
    except Exception as e:
        logger.error(f"Job failed: {e}")

def schedule_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, 'cron', hour=10, minute=30)
    scheduler.add_job(run_job, 'cron', hour=14, minute=0)
    scheduler.add_job(run_job, 'cron', hour=18, minute=0)

    scheduler.start()
    logger.info("Scheduler started and job scheduled.")

if __name__ == "__main__":
    logger.info(f"Service started at {datetime.now()}")
    schedule_job()
    try:
        while True:
            time.sleep(60)  # Keep the script running
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
