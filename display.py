import sys

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

def clear():
    disp.clear()
    disp.display()

def displayStatus(message):
    if (fakeHardware):
        print(message)
        return
    
    top = 0
    # clear the canvas
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # # make the numbers pretty
    # Temp = str(round(temperature, 1)) + '°C ' + \
    #     str(round(humidity,1)) + '%'
    # Write two lines of text.
    # (topWidth, topHeight) = bigFont.getsize(Temp)
    # left = (width - topWidth)/2
    # draw.text((left, top), Temp, font=bigFont, fill=255)
    # top += bigFontSize + padding
    draw.text((0, top), message, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()

if (not fakeHardware):
    # Setup the 128x32 OLED screen via I2C
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
    disp.begin()
    disp.clear()
    disp.display()
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # init canvas
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # define some constants to allow easy resizing of shapes.
    padding = 0

    # Load fonts
    font = ImageFont.load_default()
    # bigFontSize = 20
    # bigFont = ImageFont.truetype('zrnic.ttf', bigFontSize)