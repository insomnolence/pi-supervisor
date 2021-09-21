'''
    Defines and LED object that takes a pin and state.
    state: 0 -> Off , 1 -> On
    led_requested: 0 -> Off , 1 -> On , 2 -> Blink Slow , 3 -> Blink Fast
    pin: What GPIO pin this led is attached to

    When creating an Led, use the create_led(pin, state) function to ensure proper
    creation and non blocking calling.
 '''

import RPi.GPIO as GPIO
import asyncio

async def create_led(pin, state, led_queue ):
    led = Led(pin, state, led_queue)
    await led._init()
    return led

class Led(object):
    def __init__(self, pin, state, led_queue: asyncio.Queue):
        self.led_pin = pin
        self.state = state
        self.led_requested = 0 # 0: off 1: on 2: blink slow 3: blink fast
        self.led_queue = led_queue
        self.fast_time = 1
        self.slow_time = 5

    async def _init(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, GPIO.setup(self.led_pin, GPIO.OUT))

    async def set_led(self, request):
        self.led_requested = request
        if self.led_requested == 0:
            self.state = False
        elif self.led_requested == 1:
            self.state = True

    async def set_led_state(self, state):
        self.led_state = state
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, GPIO.output(self.led_pin, self.led_state) )

    async def run_led(self):

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, GPIO.setup, self.led_pin, GPIO.OUT) #(self.led_pin, GPIO.OUT))

        while True:

            if not self.led_queue.empty():
                request = await self.led_queue.get()
                if request >= 0 and request < 4:
                    await self.set_led(request)            

            if self.led_requested == 2:
                await self.set_led_state(not self.led_state)
                await asyncio.sleep(self.slow_time)
            
            elif self.led_requested == 3:
                await self.set_led_state(not self.led_state)
                await asyncio.sleep(self.fast_time)
            
            else:
                # Do nothing here as it's either on or off. wait for fast time
                # before checking again
                await asyncio.sleep(self.fast_time)
                 
        
