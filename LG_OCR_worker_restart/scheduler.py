from apscheduler.schedulers.background import BackgroundScheduler
from powershell_subprocess import restart_ocr_worker_service
from datetime import datetime
import time

scheduler = BackgroundScheduler()

# scheduler.add_job(restart_ocr_worker_service, 'cron', hour=10, minute=30)
# scheduler.add_job(restart_ocr_worker_service, 'cron', hour=14, minute=0)
# scheduler.add_job(restart_ocr_worker_service, 'cron', hour=18, minute=0)

scheduler.add_job(restart_ocr_worker_service, 'interval', hours=1)  # every 1 hour

scheduler.start()

while True:
    time.sleep(60)
