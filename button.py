# low level routines to handle the button. This runs in its own trhead so no real need to do anything async

# returns False if nothing is pushed, 1 if a short push happened, 2 for a long push, and 3 for a hecking long push
import RPi.GPIO as GPIO
import time

buttonPin = 13
ledPin = 21

ledBlinkPeriod = 4
ledState = False
ledCounter = 0
ledRequested = 0 # 0: off 1: on 2: blink slow 3: blink fast

GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ledPin, GPIO.OUT)
scanTime = .05 # 50ms untis of being held down. must be held down for at least 50ms

def checkButton():
    pushedLength = 0
    while GPIO.input(buttonPin) == GPIO.LOW:
        pushedLength += 1
        time.sleep(scanTime)
        if pushedLength > 30/scanTime:
            # Bail is it's a super long press
            break 
    
    if pushedLength < 2:
        return 0
    elif pushedLength < 5/scanTime:
        return 1
    elif pushedLength < 30/scanTime:
        return 2
    else:
        return 3


def _setLED(state):
    global ledState
    GPIO.output(ledPin, state)
    ledState = state

def setLED(state):
    global ledState
    global ledCounter
    global ledRequested
    ledRequested = state
    ledCounter = 0
    runLED()

def runLED():
    global ledState
    global ledCounter
    global ledRequested
    # print(f"state: {ledState}, counter: {ledCounter}, requested: {ledRequested}")
    if ledRequested == 0 and ledState:
        _setLED(False)
    elif ledRequested == 1 and not ledState:
        _setLED(True)
    elif ledRequested == 2 and ledCounter == 0: #flip
        _setLED(not ledState)
        ledCounter = 4
    elif ledRequested == 2 and ledCounter != 0: 
        ledCounter -= 1
    elif ledRequested == 3 and ledCounter == 0: #flip
        _setLED(not ledState)
        ledCounter = 1
    elif ledRequested == 3 and ledCounter != 0: 
        ledCounter -= 1