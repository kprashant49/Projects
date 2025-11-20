import win32serviceutil #pip install pywin32
import win32service
import win32event
import servicemanager
from apscheduler.schedulers.background import BackgroundScheduler
from LG_Karza_ReOCR_Auto_Selenium_deploy import run_automation

class LGKarzaService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LGKarzaScheduler"
    _svc_display_name_ = "LG Karza Auto ReOCR Scheduler"
    _svc_description_ = "Runs APScheduler job for LG Karza ReOCR automation."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.scheduler = BackgroundScheduler()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.scheduler.shutdown()
        servicemanager.LogInfoMsg("LGKarzaScheduler stopped.")

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("LGKarzaScheduler starting...")
        self.scheduler.add_job(run_automation, 'interval', minutes=5)
        self.scheduler.start()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(LGKarzaService)
 