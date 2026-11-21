"""
the shared settings for missile shield and the optional night post waves.

these settings live together because the models, view, and controller all
need them. keeping the values in one file means a change here reaches all
three parts of the game.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026
original constants and assets: the supplied cs 1110 assignment package.
"""
import introcs
import sys

### window settings (all coordinates are in pixels) ###

# the width of the game display
GAME_WIDTH  = 1152
# the height of the game display
GAME_HEIGHT = 864


### the six game states ###

# state before the game has started
STATE_INACTIVE = 0
# state when we are loading in a new level
STATE_LOADING  = 1
# state when the level is activated and in play
STATE_ACTIVE   = 2
# state when we pause the game
STATE_PAUSED   = 3
# state when we continue a paused game
STATE_CONTINUE = 4
#: state when the game is complete (won or lost)
STATE_COMPLETE = 5


### pictures and sizes ###

# the background picture
BACKGROUND = 'sunset@2x.png'

# the picture, size, and speed limits of the aiming reticule
AIM_IMAGE  = 'target@2x.png'
AIM_WIDTH  = 16
AIM_HEIGHT = 16
AIM_SPEED_LIMIT = 10
AIM_SPEED_STEP  = 0.2

# the picture and size of each silo
SILO_IMAGE = 'mountain@2x.png'
SILO_WIDTH  = 128
SILO_HEIGHT = 128

# the picture, size, and bottom offset of each city
CITY_IMAGE = 'city@2x.png'
CITY_WIDTH  = 98
CITY_HEIGHT = 98
CITY_OFFSET = 20 # distance above the bottom of the screen


### rocket settings ###

# colors for the circle and the see-through tail
ROCKET_COLOR = 'blue'
ROCKET_TAIL  = introcs.RGB(0,0,255,92)

# flight speed, starting radius, maximum radius, and growth per second
ROCKET_SPEED = 500
ROCKET_MIN_RADIUS = 3
ROCKET_MAX_RADIUS = 100
ROCKET_STEP_RADIUS = 20

# each silo starts with this many rockets
AMMO_COUNT = 10


### bomb settings ###

# colors for the circle and the see-through tail
BOMB_COLOR = 'white'
BOMB_TAIL  = introcs.RGB(255,255,255,92)

BOMB_RADIUS = 3


### wave and scoring settings ###

# the wave file used unless the command line asks for another one
DEFAULT_WAVE  = 'easy.json'

# points for each leftover rocket and each city still standing
SCORE_AMMO = 5
SCORE_CITY = 100


### fonts and text sizes ###

# the font used for titles
THEME_FONT = 'Magnetar.ttf'
# the font used for messages
BASIC_FONT = 'Roboto-Regular.ttf'
# size of a large message or label
THEME_LARGE  = 112
# size of a medium message or label
THEME_MEDIUM = 60
# size of a small message or label
THEME_SMALL  = 48


### picking a different default wave from the command line ###
"""
sys.argv keeps the arguments after the word python, so running

    python shield default.json

puts ['shield', 'default.json'] in that list. the code below reads the second
item and uses it for DEFAULT_WAVE, which chooses the file loaded when the
player starts the selected wave. for example, medium and medium.json both
select medium.json because the code adds the extension if it is missing.
"""
try:
    file = sys.argv[1]
    if file[-5:].lower() == '.json':
        DEFAULT_WAVE = file
    else:
        DEFAULT_WAVE = file+'.json'
except:
    pass # keep the original value if no argument is available

### extra timing settings ###

# the small aim speeds assume a game running at 60 frames per second.
# so this converts movement to seconds but keeps the same speed limits.
AIM_FRAME_SCALE = 60

# small steps help explosions catch bombs even when a frame takes longer.
PHYSICS_STEP = 1 / 120

### night post settings (enabled only by feature flags in the wave) ###

# a forecast ring looks this far ahead using the current speed of the bomb.
FORECAST_SECONDS = 1.5

# holding space uses up this many seconds of stored bubble charge.
BUBBLE_CAPACITY = 4.0
# radius of the bubble around the reticule, in pixels
BUBBLE_RADIUS = 125
# bombs inside a powered bubble move at this fraction of normal speed.
BUBBLE_SPEED_FACTOR = 0.22
# seconds of charge recovered per real second while space is released
BUBBLE_RECHARGE = 0.4

# every three intercepted bombs give one rocket to the silo with least ammo.
RECYCLE_GROUP_SIZE = 3

# rgba colors for the extra guides and the regular controls
HUD_MINT = (0.65, 0.94, 0.88, 1)
HUD_AMBER = (1, 0.80, 0.49, 1)
HUD_PAPER = (0.92, 0.95, 0.97, 1)

# ugh im so tired but at least the colors match now 😭
# omg this took so long 😭