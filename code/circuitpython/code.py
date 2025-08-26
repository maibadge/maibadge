import asyncio, random
import board, busio, time, gc, os
import gc9a01, displayio, adafruit_imageload
import bitmaptools, gifio, struct

# --------------------- 
# Setup RGB lights
# ---------------------
'''
import neopixel, colorsys
pixels = neopixel.NeoPixel(board.IO15, 8)
pixels.brightness = 0.03

def show_pixels(offset=0):
    for i in range(pixels.n):
        pixelHue = (i / pixels.n) + offset
        pixels[i] = colorsys.hsv_to_rgb(pixelHue, 1, 1)
    
    pixels.show()

async def update_pixel():
    while True:
        for i in range(10):
            await asyncio.sleep(0.15)
            show_pixels(i * 0.1)
'''
# --------------------- 
# Setup OLED display
# ---------------------

# Release any resources currently in use for the displays
displayio.release_displays()

# Setup display communication
spi = busio.SPI(
    clock=board.IO14,
    MOSI=board.IO13)    
display_bus = displayio.FourWire(spi, 
    command=board.IO10, 
    chip_select=board.IO11,
    reset=board.IO12)
display_bus.send(0x28, b"\x01") # Blank
display = gc9a01.GC9A01(display_bus, width=240, height=240, rotation=0)
display.root_group = displayio.Group()
#display_bus.send(0x36, b"\x18") # Set orientation to 180 degree
display_bus.send(0x29, b"\x01") # Unblank

# Load image
def load_image(img_filename):
    img_bitmap, img_palette = adafruit_imageload.load(img_filename)
    img_tilegrid = displayio.TileGrid(img_bitmap, pixel_shader=img_palette)
    display.root_group.append(img_tilegrid)
    del img_bitmap, img_palette

# Load GIF
update_gif = None

def load_gif(filename):
    odg = gifio.OnDiskGif(filename)
    next_delay = odg.next_frame()  # Load the first frame

    async def update_fn():
        while True:
            # Direct write to LCD
            next_delay = odg.next_frame()
            await asyncio.sleep(next_delay)
            display_bus.send(42, struct.pack(">hh", 0, odg.bitmap.width - 1))
            display_bus.send(43, struct.pack(">hh", 0, odg.bitmap.height - 1))
            display_bus.send(44, odg.bitmap)
    
    global update_gif
    update_gif = update_fn

# --------------------- 
# Main loop
# ---------------------

files = os.listdir("/image")
#while F := random.choice(files):


try:
    import microcontroller
    file_index = microcontroller.nvm[0]
    F = files[file_index]
except:
    file_index = 0
    F = random.choice(files)
    
if True:
    print(F, file_index)
    if F.lower().endswith('.jpg') or F.lower().endswith('.bmp'):
        load_image("/image/" + F)
        #break
    if F.lower().endswith('.gif'):
        print("Load Gif")
        load_gif("/image/" + F)
        #break

import digitalio, time
button = digitalio.DigitalInOut(board.IO0)
button.direction = digitalio.Direction.INPUT
async def change_file():
    while True:
        if button.value == False:
            microcontroller.nvm[0] = file_index+1
            microcontroller.reset()
        await asyncio.sleep(0)

async def main():
    tasks = []
    #tasks.append(asyncio.create_task(update_pixel()))
    tasks.append(asyncio.create_task(change_file()))
    if update_gif:
        tasks.append(asyncio.create_task(update_gif()))
    await asyncio.gather(*tasks)

asyncio.run(main())
