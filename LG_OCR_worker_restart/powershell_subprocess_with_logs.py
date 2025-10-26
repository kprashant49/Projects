import subprocess
import datetime
import os
import time

# ---------------------------------------
# Configuration
# ---------------------------------------
BASE_DIR = r"C:\Users\lgocrworkerserver"
LOG_FILE = os.path.join(BASE_DIR, "service_restart_log.txt")
SERVICE_PATTERN = "*Loanguard.OCRWorkerService*"
WAIT_SECONDS = 3  # wait between stop and start
# ---------------------------------------

def log_message(message):
    """Write messages with timestamp to both console and log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def run_powershell(command):
    """Run a PowerShell command and return the completed process."""
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )
    if result.stdout.strip():
        log_message(f"OUTPUT:\n{result.stdout.strip()}")
    if result.stderr.strip():
        log_message(f"ERROR:\n{result.stderr.strip()}")
    return result

def restart_services():
    log_message("🚀 Starting OCR Worker service restart process...")
    log_message(f"Target pattern: {SERVICE_PATTERN}")

    # List current status before stopping
    log_message("🔍 Checking current service status...")
    run_powershell(f'Get-Service {SERVICE_PATTERN} | Select-Object Name, Status')

    # Stop all services
    log_message("🛑 Stopping all matching services...")
    stop_result = run_powershell(f'Get-Service {SERVICE_PATTERN} | Stop-Service -Force')

    if stop_result.returncode == 0:
        log_message(f"✅ All services stopped successfully. Waiting {WAIT_SECONDS} seconds...")
        time.sleep(WAIT_SECONDS)

        # Verify stopped
        run_powershell(f'Get-Service {SERVICE_PATTERN} | Select-Object Name, Status')

        # Start all services
        log_message("▶️ Starting all matching services...")
        start_result = run_powershell(f'Get-Service {SERVICE_PATTERN} | Start-Service')

        if start_result.returncode == 0:
            log_message("✅ All services started successfully.")
        else:
            log_message("❌ Failed to start one or more services.")
    else:
        log_message("❌ Failed to stop one or more services. Aborting restart.")

    # Final status check
    log_message("📋 Final service status:")
    run_powershell(f'Get-Service {SERVICE_PATTERN} | Select-Object Name, Status')

    log_message("🏁 Restart process completed.")
    log_message("-" * 70)

if __name__ == "__main__":
    restart_services()
