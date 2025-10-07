import subprocess
from datetime import datetime, timedelta
import time
import os

# ---------------- CONFIG ----------------
RUN_TIMES = ["08:00", "12:00", "18:00"]
SCRIPT_PATH = r"D:\Projects\Data_analytics\Bank_statement_analysis\main.py"
PROCESS_LOG = r"C:\Users\kpras\Desktop\Test_data\Banking_Project\Logs\process.log"

# ---------------- HELPER FUNCTIONS ----------------
def run_main_script():
    print(f"{datetime.now()} - Triggering main.py ...")
    try:
        subprocess.run(["python", SCRIPT_PATH], check=True)
        print(f"{datetime.now()} - main.py completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now()} - main.py failed: {e}\n")

def tail_process_log(last_position):
    if not os.path.exists(PROCESS_LOG):
        return last_position
    with open(PROCESS_LOG, "r", encoding="utf-8") as f:
        f.seek(last_position)
        new_lines = f.readlines()
        for line in new_lines:
            print(line, end="")
        return f.tell()

def seconds_until_next_run():
    now = datetime.now()
    next_run = None
    min_seconds = None

    for run_time in RUN_TIMES:
        hour, minute = map(int, run_time.split(":"))
        run_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_dt <= now:
            run_dt += timedelta(days=1)
        seconds = (run_dt - now).total_seconds()
        if min_seconds is None or seconds < min_seconds:
            min_seconds = seconds
            next_run = run_dt
    return min_seconds

# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    print(f"{datetime.now()} - Scheduler started. Monitoring {PROCESS_LOG}")
    last_position = 0

    while True:
        # Sleep until next scheduled run
        wait_seconds = seconds_until_next_run()
        print(f"{datetime.now()} - Sleeping {int(wait_seconds)} seconds until next run.")
        time.sleep(wait_seconds)

        # Trigger main.py
        run_main_script()

        # Tail process.log after run
        last_position = tail_process_log(last_position)
