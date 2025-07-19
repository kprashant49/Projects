import time
import win32serviceutil
import win32service
import win32event
import os

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MyPythonService"
    _svc_display_name_ = "My Python Welcome Service"

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.log_file = os.path.join(os.path.dirname(__file__), "service_log.txt")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)
        self.log("Service is stopping...")

    def SvcDoRun(self):
        self.log("Service is starting...")
        self.main()

    def main(self):
        while self.running:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.log(f"Current Time: {current_time}")
            time.sleep(10)

    def log(self, message):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} {message}\n")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)