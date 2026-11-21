"""
Main controller for Missile Shield.

This class only runs the menu, keeps track of which state is active,
and gives user input to the Wave subcontroller. The Wave handles all
bombs, rockets, cities, aiming and collisions.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
"""
from consts import *
from game2d import *
from wave import *
import introcs
from kivy.logger import Logger


class MissileShield(GameApp):
    """The primary controller for this one-wave game.

    Attribute view: The drawing window inherited from GameApp.
    Attribute input: Keyboard events inherited from GameApp.
    Attribute _state: One of the six STATE_ constants in consts.py.
    Attribute _wave: A Wave object, or None before a wave is loaded.
    Attribute _background: The full-screen GImage of the sunset.
    Attribute _title: A GLabel on the welcome screen, else None.
    Attribute _text: A GLabel for screen messages, or None during play.
    Attribute _veil: A translucent GRectangle for readable menus.
    Attribute _footer: A small GLabel for keyboard instructions in menus.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _state: One of the six STATE_ constants in consts.py.
    # Attribute _wave: A Wave object, or None before a wave is loaded.
    # Attribute _background: The full-screen GImage of the sunset.
    # Attribute _title: A GLabel on the welcome screen, else None.
    # Attribute _text: A GLabel for screen messages, or None during play.
    # Attribute _veil: A translucent GRectangle for readable menus.
    # Attribute _footer: A small GLabel for keyboard instructions in menus.
    # end of invariant notes


    # THE THREE GAMEAPP METHODS (DO NOT OVERRIDE __init__)
    def start(self):
        """Starts on the welcome screen, before any wave has been loaded."""
        # finally the sky gets a title screen 🌅
        self._state = STATE_INACTIVE
        self._wave = None
        self._background = GImage(x=self.width/2, y=self.height/2,
                                  width=self.width, height=self.height,
                                  source=BACKGROUND)
        self._veil = GRectangle(x=self.width/2, y=self.height/2,
                                width=self.width, height=self.height,
                                fillcolor=introcs.RGB(19,8,39,70),
                                linecolor=None)
        self._title = None
        self._text = None
        self._footer = None
        self._set_up_welcome_screen()

    def update(self, dt):
        """Chooses which state to run and only advances Wave during play.

        Parameter dt: Seconds since the previous update call.
        Precondition: dt is a number >= 0.
        """
        if self._state == STATE_INACTIVE:
            self._check_first_start()
        elif self._state == STATE_LOADING:
            self._load_wave()
        elif self._state == STATE_ACTIVE:
            self._run_active_frame(dt)
        elif self._state == STATE_PAUSED:
            self._check_resume()
        elif self._state == STATE_CONTINUE:
            self._text = None
            self._footer = None
            self._state = STATE_ACTIVE
        elif self._state == STATE_COMPLETE:
            self._check_restart()

    def draw(self):
        """Draws the sunset, Wave, and messages from back to front."""
        self._background.draw(self.view)
        if self._wave is not None:
            self._wave.draw(self.view)
        if self._state != STATE_ACTIVE and self._state != STATE_LOADING:
            self._veil.draw(self.view)
        if self._title is not None:
            self._title.draw(self.view)
        if self._text is not None:
            self._text.draw(self.view)
        if self._footer is not None:
            self._footer.draw(self.view)

    # STATE HELPERS
    def _set_up_welcome_screen(self):
        """Puts the game name and a short explanation over the sunset."""
        self._title = GLabel(text='MISSILE SHIELD',x=self.width/2,
                             y=self.height*0.66,font_size=THEME_LARGE,
                             font_name=THEME_FONT,linecolor='white')
        self._text = GLabel(text="PRESS 'S' TO START",x=self.width/2,
                            y=self.height*0.51,font_size=THEME_MEDIUM,
                            font_name=BASIC_FONT,linecolor='white')
        self._footer = GLabel(text='three mountains. six cities. one sky.',
                              x=self.width/2,y=self.height*0.41,
                              font_size=23,font_name=BASIC_FONT,
                              linecolor=introcs.RGB(251,208,176))

    def _check_first_start(self):
        """Starts a new wave when the player presses S on the welcome screen."""
        if self.input.is_key_pressed('s'):
            self._title = None
            self._text = None
            self._footer = None
            self._state = STATE_LOADING

    def _load_wave(self):
        """Reads the chosen wave file; displays a message if it is invalid."""
        try:
            wave_information = self.load_json(DEFAULT_WAVE)
            if wave_information is None:
                raise ValueError('Could not load '+DEFAULT_WAVE)
            self._wave = Wave(wave_information)
            self._title = None
            self._text = None
            self._footer = None
            self._state = STATE_ACTIVE
        except Exception as e:
            Logger.info(type(e).__name__+': '+str(e))
            self._wave = None
            self._show_loading_error()

    def _show_loading_error(self):
        """Shows a clear instruction instead of crashing on a malformed JSON."""
        self._state = STATE_COMPLETE
        self._title = None
        self._text = self._make_center_message('THIS WAVE IS UNREADABLE')
        self._footer = self._make_footer('Press R to retry or check Data/')

    def _run_active_frame(self, dt):
        """Handles pausing; otherwise lets Wave run one frame of the game."""
        if self.input.is_key_pressed('p'):
            self._state = STATE_PAUSED
            self._text = self._make_center_message('THE SKY IS FROZEN')
            self._footer = self._make_footer('Press R to resume')
        else:
            self._wave.update(self.input, dt)
            if self._wave.isFinished():
                self._show_final_screen()

    def _check_resume(self):
        """Unpauses using the R key without constructing another Wave."""
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
            self._text = None
            self._footer = None

    def _check_restart(self):
        """Restarts with a brand-new Wave whenever the player presses R."""
        if self.input.is_key_pressed('r'):
            self._state = STATE_LOADING
            self._title = None
            self._text = None
            self._footer = None
            self._wave = None

    def _show_final_screen(self):
        """Displays either the earned score or a loss message and R to retry."""
        self._state = STATE_COMPLETE
        self._title = None
        if self._wave.isWon():
            final_score = self._wave.getScore()
            headline = 'SCORE: '+str(final_score)
            explanation = 'A city survives. Press R to replay.'
        else:
            headline = 'THE LAST CITY FELL'
            explanation = 'Press R to protect another sky.'
        self._text = self._make_center_message(headline)
        self._footer = self._make_footer(explanation)

    # LITTLE DISPLAY HELPERS
    def _make_center_message(self, words):
        """Returns a large readable white label over the middle of the view."""
        return GLabel(text=words,x=self.width/2,y=self.height*0.52,
                      font_size=THEME_MEDIUM,font_name=BASIC_FONT,
                      fillcolor=introcs.RGB(35,16,55,160),
                      linecolor='white')

    def _make_footer(self, words):
        """Returns the smaller caption beneath a main menu message."""
        return GLabel(text=words,x=self.width/2,y=self.height*0.42,
                      font_size=23,font_name=BASIC_FONT,
                      linecolor=introcs.RGB(252,217,178))


# omg this took so long 😭