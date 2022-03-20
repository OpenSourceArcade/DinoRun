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

font = bitmap_font.load_font("fonts/Junction-regular-24.bdf")

text_score = label.Label(font, text=str(0), color=0xd83c02)
text_score.anchor_point = (0, 0)
text_score.anchored_position = (10, 10)

#gameover
gameover_image, palette = adafruit_imageload.load(
    "images/gameover.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
palette.make_transparent(0)
gameover = displayio.TileGrid(gameover_image, pixel_shader=palette)
gameover.x = 5
gameover.y = 30

#bg
bg_image, palette = adafruit_imageload.load(
    "images/bg.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
palette.make_transparent(0)
bg = displayio.TileGrid(bg_image, pixel_shader=palette)
bg.x = 0
bg.y = 0
bg2 = displayio.TileGrid(bg_image, pixel_shader=palette)
bg2.x = 240
bg2.y = 0

#cacuts
cacuts_image, palette = adafruit_imageload.load(
    "images/cacuts.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
palette.make_transparent(0)
cacuts = displayio.TileGrid(cacuts_image, pixel_shader=palette)
cacuts.x = 240
cacuts.y = 135 - 48

# hero (dino) sprite sheep
hero_sprite_sheet, palette = adafruit_imageload.load("images/dino.bmp",bitmap=displayio.Bitmap,palette=displayio.Palette)
# Create a sprite (tilegrid)
palette.make_transparent(0)
hero = displayio.TileGrid(hero_sprite_sheet, pixel_shader=palette,width = 1,height = 1,tile_width = 45,tile_height = 48)
hero[0] = 0
hero.y = 80
hero.x = 20

class Sprite:
    def __init__(self,TileGrid,speed):
        self.tile=TileGrid
        self.life=1
        self.speed=speed
        
class Hero(Sprite):
    def __init__(self):
        Sprite.__init__(self,hero,10)
        self.status='run'
        self.score='0'
        self.frame = 0
    def update(self):
        if self.status == "run":
            self.frame += 1
        if self.frame == 5 :
            self.frame = 0
        if self.status == "jump":
            hero_frame_current = 1
            self.tile.y -= self.speed
        if self.tile.y <= 0:
            self.tile.y = 10
            self.status = "down"
        if self.status == "down":
            self.frame = 4
            self.tile.y += player.speed
        if self.tile.y >= 80:
            self.tile.y = 80
            self.status = "run"
        hero[0] = self.frame

player = Hero()

class Enemy(Sprite):
    def __init__(self):
        Sprite.__init__(self,cacuts,15)
    def update(self):
        self.tile.x -= self.speed
        if self.tile.x <= -34:
           self.tile.x = 240
           player.score += 1
           text_score.text = str(player.score)
    
        
enemy = Enemy()

group = displayio.Group()
group.append(bg)
group.append(bg2)
display.show(group)


def init():
    player.tile.y = 80
    player.status = "run"
    
    enemy.tile.x = 240
    player.time = 0
    player.score=0
    text_score.text = str(player.score)
    group.append(enemy.tile)
    group.append(player.tile)
    group.append(text_score)
    player.life=1

def game_restart():
    print('restart')
    #group.remove(text_game_over)
    group.remove(gameover)
    group.remove(enemy.tile)
    group.remove(player.tile)
    group.remove(text_score)
    init()

pressed = False

init()

while True:
    if player.life==0 :
        if button_center.value == 0 and pressed == False:
            pressed = True
        if button_center.value == 1 and pressed == True:
               game_restart()
               pressed = False
    else :
        player.time += 1
        if button_up.value == 0 and player.status == "run":
            player.status = "jump"
        if player.time % 2000 == 0:
            player.time = 0
            enemy.update()
            player.update()
            bg.x-=2
            bg2.x-=2
            if bg2.x==0:
                bg.x=240
            if bg.x==0:
                bg2.x=240
            
            if abs(player.tile.x-enemy.tile.x)<30 and abs(player.tile.y-enemy.tile.y)<30:
                #group.append(text_game_over)
                group.append(gameover)
                player.life = 0