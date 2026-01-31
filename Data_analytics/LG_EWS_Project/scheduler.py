import logging
import traceback
from apscheduler.schedulers.blocking import BlockingScheduler
from logger import setup_logging
from main import main
from emailer import send_failure_alert


def run_job():
    try:
        logging.info("Scheduled job triggered.")
        main()

    except Exception:
        logging.exception("Scheduled job failed.")

        error_details = traceback.format_exc()

        # Send failure alert email
        send_failure_alert(
            subject="EWS Job Failure",
            error_message=error_details
        )

        # Re-raise so APScheduler marks job as failed
        raise


if __name__ == "__main__":
    setup_logging()
    logging.info("Starting APScheduler service.")

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    scheduler.add_job(
        run_job,
        trigger="cron",
        minute="*/30",
        id="ews_email_job",
        replace_existing=True
    )

    logging.info("Scheduler initialized. Waiting for jobs.")
    scheduler.start()