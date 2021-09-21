'''
    Defines a Button to be used. There are two modes for buttons. 
    Simple -> Just catches that a button was pressed
    Timed -> Length of press is tracked in <2, 5, and 30 seconds

    Call create_button(pin, mode) to ensure async creation. 

    For this purpose return 1 if short push happened, 2 for a long push, and 3 for very long
'''

import RPi.GPIO as GPIO
import asyncio


class Button(object):
    def __init__(self, pin, mode, button_queue: asyncio.Queue):
        self.button_pin = pin
        self.mode = mode
        self.scan_time = .05 # 50ms untis of being held down. must be held down for at least 50ms
        self.button_queue = button_queue

    async def _init(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, GPIO.setmode(GPIO.BCM)) # Maybe Put this elsewhere
        await loop.run_in_executor(None, GPIO.setup(self.button_pin, \
            GPIO.IN, pull_up_down=GPIO.PUD_UP))
        

    async def check_button(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, GPIO.setmode, GPIO.BCM) #(GPIO.BCM)) # Maybe Put this elsewhere
        await loop.run_in_executor(None, GPIO.setup, self.button_pin, GPIO.IN, GPIO.PUD_UP) #(self.button_pin, \
            #GPIO.IN, pull_up_down=GPIO.PUD_UP))

        while True:
            loop = asyncio.get_event_loop()
            pushed_length = 0
            while await loop.run_in_executor(None, GPIO.input, self.button_pin) == GPIO.LOW: #(self.button_pin)) == GPIO.LOW:
                pushed_length += 1
                asyncio.sleep(self.scan_time)
                if pushed_length > 30/self.scan_time:
                    # Bail is it's a super long press
                    break 
            
            if pushed_length < 2:
                continue
            elif self.mode != 'Timed' or pushed_length < 5/self.scan_time:
                await self.button_queue.put(1)
            elif pushed_length < 30/self.scan_time:
                await self.button_queue.put(2)
            else:
                await self.button_queue.put(3)


async def create_button(pin, mode, button_queue) -> Button:
    button = Button(pin, mode, button_queue)
    await button._init()
    return button


