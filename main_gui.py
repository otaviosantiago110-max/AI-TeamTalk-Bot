
import sys
from startup_check import run_startup_check
run_startup_check()
import wx
from main import ApplicationController, setup_logging

if __name__ == "__main__":
    setup_logging() # Also log GUI sessions to file
    controller = ApplicationController(nogui_mode=False)
    controller.start() # This will enter the GUI path inside the controller
    sys.exit(0)
