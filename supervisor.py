import time
from datetime import timedelta
import subprocess
import threading, time, signal
import display
import os
import json
import datetime
import button
WAIT_TIME_SECONDS = .25

def buttonDaemon():
    buttonState = button.checkButton()
    if buttonState == 1:
        display.displayStatus("Button Pressed")
        button.setLED(1)
        time.sleep(2)
        display.clear()
    elif buttonState == 2:
        display.displayStatus("Long Pressed")
        button.setLED(3)
        time.sleep(2)
        display.clear()

def ledDaemon():
    button.runLED()

class ProgramKilled(Exception):
    pass

class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        
    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)


def signal_handler(signum, frame):
    raise ProgramKilled

def startWebServer(port=8000):
    pass

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    buttonJob = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=buttonDaemon)
    buttonJob.start()
    ledJob = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=ledDaemon)
    ledJob.start()
    button.setLED(2)

    while True:
          try:
              time.sleep(1)
          except ProgramKilled:
              print ("Program killed: running cleanup code")
              buttonJob.stop()
              ledJob.stop()
              display.clear()
              button.setLED(False)
              break
