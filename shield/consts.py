"""
Constants for Froggit

This module global constants for the game Froggit. These constants need to be 
used in the model, the view, and the controller. As these are spread across 
multiple modules, we separate the constants into their own module. This allows 
all modules to access them.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026
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
ROCKET_COLOR = introcs.RGB(109, 179, 255)
ROCKET_TAIL  = introcs.RGB(109, 179, 255, 72)

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
THEME_FONT = 'Roboto-Bold.ttf'
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

# the original state numbers stay the same for classic waves
STATE_SCORING = 6

### extra time settings ###
# converts the original aim speed from frames into seconds
AIM_FRAME_SCALE = 60
PHYSICS_STEP = 1 / 120

### extra tools only enabled by custom json ###
FORECAST_SECONDS = 1.5

# extra guides appear if their JSON feature flags are true
# forecasts show a possible position but never destroy a bomb
# aiming spots do not redirect rockets that are already in the air
# the slow field changes bomb speed but doesn't destroy bombs
# charge is measured in seconds and never goes below zero
# rocket refunds never put more than AMMO_COUNT in a silo
# the HUD counters show game data without changing the rules
# aircraft appear if they are listed in a custom wave JSON
# the slow field has four seconds of charge
BUBBLE_CAPACITY = 4.0
BUBBLE_RADIUS = 125
BUBBLE_SPEED_FACTOR = 0.22
BUBBLE_RECHARGE = 0.4

# every three intercepted bombs return one rocket if a silo has room
RECYCLE_GROUP_SIZE = 3

### the colors for the custom ui ###
HUD_MINT = (0.98, 0.92, 0.50, 1)
HUD_AMBER = (0.95, 0.73, 0.37, 1)
HUD_PAPER = (0.93, 0.96, 0.95, 1)

UI_BG = introcs.RGB(9, 17, 26)
UI_SURFACE = introcs.RGB(12, 22, 34, 255)
UI_SURFACE_SOFT = introcs.RGB(27, 36, 49, 255)
UI_BORDER = introcs.RGB(56, 78, 87, 190)
UI_TEXT = introcs.RGB(237, 245, 241)
UI_MUTED = introcs.RGB(150, 173, 181)
UI_ACCENT = introcs.RGB(250, 235, 128)
UI_AMBER = introcs.RGB(243, 186, 95)
UI_DANGER = introcs.RGB(255, 149, 135)

# this one is from the supplied fonts folder
DISPLAY_FONT = 'Neonix.ttf'

# pls why does this file need this many settings 😭