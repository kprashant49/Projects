import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from logger import setup_logging
from main import main
from emailer import send_failure_alert
import traceback


def run_job():
    try:
        logging.info("Scheduled job triggered.")
        main()

    except Exception as e:
        error_details = traceback.format_exc()
        logging.error("Scheduled job failed.")
        logging.error(error_details)

        # Send failure alert email
        send_failure_alert(
            subject="Daily Analytics Job",
            error_message=error_details
        )

        # Re-raise if you want scheduler to know job failed
        raise


if __name__ == "__main__":
    setup_logging()
    logging.info("Starting APScheduler service.")

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    scheduler.add_job(
        run_job,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_email_job",
        replace_existing=True
    )

    logging.info("Scheduler initialized. Waiting for jobs.")
    scheduler.start()
