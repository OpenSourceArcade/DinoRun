import board
import displayio
import busio
from adafruit_st7789 import ST7789
import adafruit_imageload
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import digitalio
from time import sleep

displayio.release_displays()
spi = busio.SPI(board.GP10,board.GP11)

while not spi.try_lock():
    print(".")
    pass
spi.configure(baudrate=24000000) # Configure SPI for 24MHz
spi.unlock()
tft_cs = board.GP9
tft_dc = board.GP8

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.GP12)

display = ST7789(display_bus, width=240, height=135, rowstart=40,colstart=53,rotation=90)

button_up = digitalio.DigitalInOut(board.GP2)
button_up.direction = digitalio.Direction.INPUT
button_up.pull = digitalio.Pull.UP

button_center = digitalio.DigitalInOut(board.GP3)
button_center.direction = digitalio.Direction.INPUT
button_center.pull = digitalio.Pull.UP

is_game_over = False


time = 0

text = "GAME OVER"
font = bitmap_font.load_font("fonts/LeagueSpartan-Bold-16.bdf")
color = 0xFFFFFF
text_game_over = label.Label(font, text=text, color=color)
text_game_over.anchor_point = (0.5, 0.5)
text_game_over.anchored_position = (120, 75)

score = 0
text_score = label.Label(font, text=str(score), color=color)
text_score.anchor_point = (0, 0)
text_score.anchored_position = (10, 10)

image, palette = adafruit_imageload.load(
    "images/logo.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
palette.make_transparent(0)
tile_grid = displayio.TileGrid(image, pixel_shader=palette)
tile_grid.x = 120 - 39
tile_grid.y = 75 - 50

#cacuts
cacuts_image, palette = adafruit_imageload.load(
    "images/cacuts.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
palette.make_transparent(0)
cacuts = displayio.TileGrid(cacuts_image, pixel_shader=palette)
cacuts.x = 240
cacuts.y = 135 - 42
cacuts_speed = 15

# hero (dino) sprite sheep
hero_frame_max = 5
hero_frame_current = 0
hero_sprite_sheet, palette = adafruit_imageload.load("images/dino.bmp",bitmap=displayio.Bitmap,palette=displayio.Palette)
# Create a sprite (tilegrid)
palette.make_transparent(0)
hero = displayio.TileGrid(hero_sprite_sheet, pixel_shader=palette,width = 1,height = 1,tile_width = 49,tile_height = 53)
hero[0] = hero_frame_current
hero.y = 80
hero.x = 20

hero_status = "run"
hero_speed = 10

group = displayio.Group()
display.show(group)

def init():
    hero.y = 80
    hero_status = "run"
    cacuts.x = 240
    time = 0
    group.append(cacuts)
    group.append(hero)
    group.append(text_score)
    is_game_over = False

def game_restart():
    if is_game_over:
        group.remove(text_game_over)
        group.remove(cacuts)
        group.remove(hero)
        group.remove(text_score)
        init()

init()
while True:
    if is_game_over :
        if button_center.value == 0:
            print('restart')
            game_restart()
    else :
        time += 1
        if button_up.value == 0 and hero_status == "run":
            hero_status = "jump"
        if time % 2000 == 0:
            print('fps')
            cacuts.x -= cacuts_speed
            if cacuts.x <= -34:
                cacuts.x = 240
                score += 1
                text_score.text = str(score)
            if hero_status == "run":
                hero_frame_current += 1
                if hero_frame_current == hero_frame_max :
                    hero_frame_current = 0
            if hero_status == "jump":
                hero_frame_current = 1
                hero.y -= hero_speed
                if hero.y <= 0:
                    hero.y = 10
                    hero_status = "down"
            if hero_status == "down":
                hero_frame_current = 4
                hero.y += hero_speed
                if hero.y >= 80:
                    hero.y = 80
                    hero_status = "run"
            if cacuts.x >= hero.x and cacuts.x <= hero.x+49 :
                if cacuts.y >= hero.y and cacuts.y <= hero.y+53 :
                    group.append(text_game_over)
                    is_game_over = True

        hero[0] = hero_frame_current
