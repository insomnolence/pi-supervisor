import sys
import asyncio
from async_call import async_call

fakeHardware = False
try:
    import Adafruit_GPIO.SPI as SPI
    import Adafruit_SSD1306
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except:
    print("[Warn] unable to load hardware libraries for SSD1306, and starting in simulation mode", file = sys.stderr)
    fakeHardware = True
class Timer:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self.timeout)
        await self.callback()

    async def cancel(self):
        self.task.cancel()
class Display(object):

    def __init__(self, external_display, enable_stdout):
        self.display = None
        self.display_exists = external_display
        self.stdout_enabled = enable_stdout
        self.draw = None
        self.width = 0
        self.height = 0
        self.padding = 0
        self.font = None
        self.image = None
        self.timer = None

    async def setup(self):
        if self.display_exists:
            # Setup the 128x32 OLED screen via I2C
            self.display = await async_call(Adafruit_SSD1306.SSD1306_128_32)(rst=None)
            await async_call(self.display.begin)()
            await async_call(self.display.clear)()
            await async_call(self.display.display)()
            self.width = self.display.width
            self.height = self.display.height
            self.image = await async_call(Image.new)('1', (self.width, self.height))

            # init canvas
            self.draw = await async_call(ImageDraw.Draw)(self.image)
            await async_call(self.draw.rectangle)((0,0,self.width,self.height), outline=0, fill=0)

            # define some constants to allow easy resizing of shapes.
            self.padding = 0

            # Load fonts
            self.font = await async_call(ImageFont.load_default)()
            # bigFontSize = 20
            # bigFont = ImageFont.truetype('zrnic.ttf', bigFontSize)

    async def _clear(self):
        await async_call(self.display.clear)()
        await async_call(self.display.display)()

        if self.timer is not None:
            self.timer = None

    async def clear(self):
        if self.timer is not None:
            await self.timer.cancel()
            self.timer = None

        await self._clear()

    async def message(self, message):
        if not self.display_exists or self.stdout_enabled:
            print(message)

            if not self.display_exists:
                return

        # If there is a timeout currently, cancel it as a new message
        # is going to be written
        if self.timer is not None:
            await self.timer.cancel()
            self.timer = None

        top = 0
        # clear the canvas
        await async_call(self.draw.rectangle)((0,0,self.width,self.height), outline=0, fill=0)

        # # make the numbers pretty
        # Temp = str(round(temperature, 1)) + '°C ' + \
        #     str(round(humidity,1)) + '%'
        # Write two lines of text.
        # (topWidth, topHeight) = bigFont.getsize(Temp)
        # left = (width - topWidth)/2
        # draw.text((left, top), Temp, font=bigFont, fill=255)
        # top += bigFontSize + padding
        await async_call(self.draw.text)((0, top), message, font=self.font, fill=255)

        # Display image.
        await async_call(self.display.image)(self.image)
        await async_call(self.display.display)()

        # Set a timeout for the message to be cleared.
        self.timer = Timer(3600, self._clear)