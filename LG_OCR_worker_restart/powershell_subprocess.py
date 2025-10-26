import subprocess

def restart_ocr_worker_service():
    """
    Stops and restarts the Loanguard OCR Worker Windows service.
    """
    base_dir = r"C:\Users\lgocrworkerserver"

    # Step 1: Stop the service
    stop_command = 'powershell -Command "Get-Service *Loanguard.OCRWorkerService* | Stop-Service"'
    stop_process = subprocess.run(
        stop_command,
        capture_output=True,
        text=True,
        cwd=base_dir,
        shell=True
    )

    if stop_process.returncode == 0:
        print("Service stopped successfully.")
        print(stop_process.stdout)
    else:
        print("Failed to stop service:")
        print(stop_process.stderr)

    # Step 2: Start the service only if stop succeeded
    if stop_process.returncode == 0:
        start_command = 'powershell -Command "Get-Service *Loanguard.OCRWorkerService* | Start-Service"'
        start_process = subprocess.run(
            start_command,
            capture_output=True,
            text=True,
            cwd=base_dir,
            shell=True
        )

        if start_process.returncode == 0:
            print("Service started successfully.")
            print(start_process.stdout)
        else:
            print("Failed to start service:")
            print(start_process.stderr)
