"""
Constants for Missile Shield and its optional Night Post waves.

This module holds global constants for Missile Shield. They need to be
used in the model, the view, and the controller. As these are spread across 
multiple modules, we separate the constants into their own module. This allows 
all modules to access them.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
Original constants and assets: the supplied CS 1110 assignment package.
"""
import introcs
import sys

### WINDOW CONSTANTS (all coordinates are in pixels) ###

# the width of the game display
GAME_WIDTH  = 1152
# the height of the game display
GAME_HEIGHT = 864


### GAME CONSTANTS ###

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


### GAME ASSETS ###

# The background image
BACKGROUND = 'sunset@2x.png'

# The constants for the aim target
AIM_IMAGE  = 'target@2x.png'
AIM_WIDTH  = 16
AIM_HEIGHT = 16
AIM_SPEED_LIMIT = 10
AIM_SPEED_STEP  = 0.2

# The constants for a silo
SILO_IMAGE = 'mountain@2x.png'
SILO_WIDTH  = 128
SILO_HEIGHT = 128

# The constants for a city
CITY_IMAGE = 'city@2x.png'
CITY_WIDTH  = 98
CITY_HEIGHT = 98
CITY_OFFSET = 20 # The distance from the screen bottom


### ROCKET CONSTANTS ###

# The colors
ROCKET_COLOR = 'blue'
ROCKET_TAIL  = introcs.RGB(0,0,255,92)

# The explosion parameters
ROCKET_SPEED = 500
ROCKET_MIN_RADIUS = 3
ROCKET_MAX_RADIUS = 100
ROCKET_STEP_RADIUS = 20

# The ammo count of each silo
AMMO_COUNT = 10


### BOMB CONSTANTS ###

# The colors
BOMB_COLOR = 'white'
BOMB_TAIL  = introcs.RGB(255,255,255,92)

BOMB_RADIUS = 3


### WAVE CONSTANTS ###

# The default wave file
DEFAULT_WAVE  = 'easy.json'

# The score values 
SCORE_AMMO = 5
SCORE_CITY = 100


### FONT CHOICES ###

# The font choice for titles
THEME_FONT = 'Magnetar.ttf'
# The font choice for messages
BASIC_FONT = 'Roboto-Regular.ttf'
# A large message or label
THEME_LARGE  = 112
# A medium message or label
THEME_MEDIUM = 60
# A small message or label
THEME_SMALL  = 48


### USE COMMAND LINE ARGUMENTS TO CHANGE DEFAULT LEVEL FILE
"""
sys.argv is a list of the command line arguments when you run python. These 
arguments are everything after the word python. So if you start the game typing

    python shield default.json

Python puts ['shield', 'default.json'] into sys.argv. Below, we take advantage 
of this fact to change the constant DEFAULT_WAVE. This is the wave file to be 
used when you start the game.  
"""
try:
    file = sys.argv[1]
    if file[-5:].lower() == '.json':
        DEFAULT_WAVE = file
    else:
        DEFAULT_WAVE = file+'.json'
except:
    pass # Use original value

### ADD MORE CONSTANTS (PROPERLY COMMENTED) AS NECESSARY ###

# The small supplied aim speeds describe a nominal 60-frame-per-second game.
# This converts them to seconds without changing their getter/setter limits.
AIM_FRAME_SCALE = 60

# Small physics steps help ordinary explosions catch bombs during slow frames.
PHYSICS_STEP = 1 / 120

### NIGHT POST CONSTANTS (enabled only by a wave's feature flags) ###

# A forecast ring shows this many seconds ahead at the bomb's current speed.
FORECAST_SECONDS = 1.5

# Holding Space spends this many seconds of stored slow-bubble charge.
BUBBLE_CAPACITY = 4.0
# Radius of the local bubble around the aiming reticule, in pixels.
BUBBLE_RADIUS = 125
# Bombs inside the powered bubble keep this fraction of their normal speed.
BUBBLE_SPEED_FACTOR = 0.22
# Seconds of charge recovered per real second when Space is released.
BUBBLE_RECHARGE = 0.4

# Every three intercepted bombs return one rocket to the least-stocked silo.
RECYCLE_GROUP_SIZE = 3

# Simple RGBA colors for the extra instruments and readable normal controls.
HUD_MINT = (0.65, 0.94, 0.88, 1)
HUD_AMBER = (1, 0.80, 0.49, 1)
HUD_PAPER = (0.92, 0.95, 0.97, 1)

# ugh im so tired but at least the colors match now 😭
# omg this took so long 😭