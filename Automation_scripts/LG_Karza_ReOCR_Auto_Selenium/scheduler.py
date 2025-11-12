from apscheduler.schedulers.background import BackgroundScheduler
from LG_Karza_ReOCR_Auto_Selenium_deploy import run_automation
from datetime import datetime
import time


def schedule_job():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(run_automation, 'cron', hour=10, minute=30)
    # scheduler.add_job(run_automation, 'cron', hour=14, minute=0)
    # scheduler.add_job(run_automation, 'cron', hour=18, minute=0)
    scheduler.add_job(run_automation, 'interval', hours=1)  # every 1 hour
    scheduler.start()

while True:
    time.sleep(60)