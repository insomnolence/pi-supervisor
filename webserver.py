import asyncio
import aiofiles
from aiohttp import web

WAIT_TIME_SECONDS = .25

async def create_server(from_server_queue, to_server_queue):
    server = WebServer()
    await server._init()
    return server
class WebServer:
    def __init__(self, from_server_queue, to_server_queue):
        # whatever the path is.
        self.path = '/usr/local/lib/supervisor/templates/'
        self.to_processor_queue = from_server_queue
        self.from_processor_queue = to_server_queue
        self.runner = None
        self.app = web.Application()
        self.site = None

    async def html_format(self, file_name):
        try:
            async with aiofiles.open(self.path+file_name) as f:
                index = await f.read()
                return index
        except Exception as e:
           print(e)
           return 'File error when opening {} to serve html'.format(file_name)

    async def handle_ssid(self, request):
        response = await self.html_format('index.html')
        return web.Response(text=response, content_type='text/html')

    async def handle_ssid_post(self, request):
        if request.method == 'POST':
            form = await request.post()

            ssid = form['ssid']
            passwd = form['password']

            if ssid != '':
                # Set the ssid here
                print('TBD, set the net config !')
                await self.to_processor_queue.put('success')

            return web.Response(text='SSID and Password submitted Successfully, Configuring . . .')

    async def _init(self):

        self.app.add_routes([web.get('/', self.handle_ssid),
                             web.post('/login', self.handle_ssid_post)])

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, None, 80)
        #await self.site.start()

        while True:

            # Check the queue for any new info
            if not self.from_processor_queue.empty():
                message = await self.from_processor_queue.get()
                
                if message == 'start':
                    await self.site.start()

                elif message == 'stop':
                    await self.site.stop()

                else:
                    print('Invalid message received: {}'.format(message))



            await asyncio.sleep(WAIT_TIME_SECONDS)
