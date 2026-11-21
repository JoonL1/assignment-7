"""
The primary application script for Missile Shield

This is the module with the application code. Make sure that this module is
in a folder with the following files:

    app.py      (the primary controller class)
    wave.py     (the subcontroller for a game wave)
    models.py   (the model classes)
    consts.py   (the application constants)

In addition, you should have the following subfolders

    Data          (json files with the game data)
    Fonts         (fonts to use for GLabel)
    Images        (image files to use in the game)
    Sounds        (sound effects for the game)

Moving any of these folders or files will prevent the game from working properly

Author: Walker M. White (wmw2)
Date:   November 5, 2026
"""
from consts import *
from app import *


# Application code
if __name__ == '__main__':
    MissileShield(width=GAME_WIDTH,height=GAME_HEIGHT).run()
