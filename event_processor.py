import asyncio
from asyncio.subprocess import PIPE, STDOUT

WAIT_TIME_SECONDS = .25

class Event_Processor(object):
    def __init__(self, list_of_queues):
        self.running_webservice = False
        self.wifi_connected = False
        self.wifi_configuring = False
        # instantiate queues here
        self.button_queue = list_of_queues[0]
        self.web_from_queue = list_of_queues[1]
        self.web_to_queue = list_of_queues[2]
        self.led_queue = list_of_queues[3]

    async def check_wifi_services(self):
        #  write script to check wifi
        print('Checking wifi')
        process = await asyncio.create_subprocess_shell('/usr/sbin/iwconfig | grep ESSID', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout = await process.communicate()
        if process.returncode == 0:
            for f in stdout:
                line = f.decode().strip()
                if 'ESSID' in line and 'off' in line:
                    # There is no connected wifi. Load the appropriate scripts
                    # and set up the webserver.
                    print('Not found in line: {}'.format(line))
                    return False
                else:
                    tmp = line.split(':')
                    if len(tmp) > 1:
                        
                        print('Connected to WiFi {}'.format(tmp[1]))
                        return True
                    else:
                        print('Error receiving data? {} '.format(tmp))
        else: 
            # Couldn't execute the command ?
            print('Error, failed to execute the command to find wifi')

        return False

    async def run(self):
        while True:

            if  not self.wifi_connected and not self.wifi_configuring:
                self.wifi_configuring = True
                found = await self.check_wifi_services()
                if not found:
                    self.running_webservice = True
                     # Let the webservice know it needs to start up and 
                    # process the ssid info.
                    process = await asyncio.create_subprocess_shell('/usr/local/lib/supervisor/start_portal.sh', \
                        stdin = PIPE, stdout = PIPE, stderr = STDOUT)
                    await process.wait()

                    await self.web_to_queue.put('start')
            
                else:
                    self.wifi_connected = True
                    self.wifi_configuring = False

            # check all the queues to see if there is anything that needs doing.
            if not self.button_queue.empty():
                button_value = await self.button_queue.get()
                if button_value == 1:
                    # Show info on display. What info ?
                    print('show stuff here')
                elif button_value == 2:
                    # Turn on Managemnt SSD
                    print('Do ssid stuff here')
                    #blink slow
                    await self.led_queue.put(2)
                elif button_value == 3:
                    # Factory Reset?
                    print('What exactly is a factory reset')
                    # blink fast
                    await self.led_queue(3)
            
            if not self.web_from_queue.empty():
                # What are we looking for here ? Oh . . maybe that the config was done ?
                info = await self.web_from_queue.get()
                if info == 'success':
                    # configured properly. Stop the portal and bounce the net connection.
                    process = await asyncio.create_subprocess_shell('/usr/local/lib/supervisor/stop_portal.sh', stdin = PIPE, stdout = PIPE, stderr = STDOUT)
                    await process.wait()

                    # bounce the net connection
                    process = await asyncio.create_subprocess_shell('/usr/sbin/netplan apply', \
                        stdout = PIPE, stderr = STDOUT)
                    await process.wait()
                    await self.web_to_queue.put('stop')
                    # Give the system time to connect
                    await asyncio.sleep(5)
                    self.wifi_configuring = False
                    self.wifi_connected = False

                # do we have any other statuses ?
            

            await asyncio.sleep(WAIT_TIME_SECONDS)





        
