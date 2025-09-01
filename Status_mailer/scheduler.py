import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from status_mailer import status_mailer
from datetime import datetime
import time

log_file_path = r"D:\Projects\Status_mailer\scheduler.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Scheduler started at " + str(datetime.now()))

def run_job():
    try:
        logging.info("Running Status mailer job")
        status_mailer()
        logging.info("Job completed successfully")
    except Exception as e:
        logging.error(f"Job failed: {e}")

def schedule_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, 'cron', minute=30)
    # scheduler.add_job(run_job, 'cron', hour=9, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=10, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=11, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=12, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=13, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=14, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=15, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=16, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=17, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=18, minute=00)
    # scheduler.add_job(run_job, 'cron', hour=19, minute=00)

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