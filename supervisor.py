
import asyncio
from event_processor import Event_Processor
#import led
#import button
from led import Led
from button import Button, create_button
import signal
#import webserver
from webserver import WebServer

ButtonPin = 13
LedPin = 21

WAIT_TIME_SECONDS = .25

def init_main():

    loop = asyncio.get_event_loop()

    # Define signals to track for shutdown
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    # Define Queues needed for communication
    from_button_queue = asyncio.Queue()
    from_server_queue = asyncio.Queue()
    to_server_queue = asyncio.Queue()
    to_led_queue = asyncio.Queue()

    queues = (from_button_queue, from_server_queue, to_server_queue, to_led_queue)

    # Define the Hardware being used.
    # Put theses in tasks as need be    
    button_1 = Button(ButtonPin, 'Timed', from_button_queue)
    led_1 = Led(LedPin, 1, to_led_queue)

    # Define the Event Processor
    event_processor = Event_Processor(queues)
    
    # Define the Web Server. It won't automatically create unless 
    # it is told to.
    web_server = WebServer(from_server_queue, to_server_queue) 

    try:
        loop.create_task(button_1.check_button())
        loop.create_task(led_1.run_led())
        loop.create_task(event_processor.run())
        loop.create_task(web_server._init())

        loop.run_forever()
            
    finally:
        loop.close()
        print('Shutdown the Supervisor')

async def shutdown(signal, loop):
    # Cleanup tasks tied to the service's shutdown
    print('Received exit signal {}'.format(signal.name))
    tasks = [ t for t in asyncio.all_tasks() if t is not \
        asyncio.current_task()]

    [task.cancel() for task in tasks]

    print('Cancelling {} outstanding tasks.'.format(len(tasks)))

    await asyncio.gather(*tasks, return_exceptions=True)

    loop.stop()

if __name__ == "__main__":

    init_main()
