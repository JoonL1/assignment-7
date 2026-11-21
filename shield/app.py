"""
Primary module for Missile Shield

This module contains the main controller class for the MissileShield application. 
There is no need for any any need for additional classes in this module. If you 
need more classes, 99% of the time they belong in either the wave module or the 
models module. If you are ensure about where a new class should go, post a 
question on Ed Discussion.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026
"""
from consts import *
from game2d import *
from wave import Wave
import introcs
import os
from kivy.logger import Logger


# PRIMARY RULE: MissileShield can only access attributes in wave.py via getters/setters
# MissileShield is NOT allowed to access anything in wave.py or models.py.


class MissileShield(GameApp):
    """
    The primary controller class for the Missile Shiled application
    
    This class extends GameApp and implements the various methods necessary for 
    processing the player inputs and starting/running a game.
    
        Method start begins the application.
    
        Method update either changes the state or updates the Level object
    
        Method draw displays the Level object and any other elements on screen
    
    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class. Any initialization should be done in
    the start method instead. This is only for this class. All other classes
    behave normally.
    
    Most of the work handling the game is actually provided in the class Level.
    Level should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.
    
    The primary purpose of this class is managing the game state: when is the
    game started, paused, completed, etc. It keeps track of that in a hidden
    attribute
    
    Attribute view: The game view, used in drawing (see examples from class)
    Invariant: view is an instance of GView and is inherited from GameApp
    
    Attribute input: The user input, used to control the ship and change state
    Invariant: input is an instance of GInput and is inherited from GameApp
    """
    # HIDDEN ATTRIBUTES
    # Attribute _state: The current state of the game (taken from const.py)
    # Invariant: _state is one of STATE_INACTIVE, STATE_LOADING, STATE_ACTIVE, 
    #            STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE
    #
    # Attribute _wave: The subcontroller for a wave, managing the game
    # Invariant: _wave is a Wave object or None if no wave is currently active
    #
    # Attribute _background: The background image
    # Invariant: _background is a GImage
    #
    # Attribute _title: The title of the game
    # Invariant: _title is a GLabel, or None if there is no title to display
    #
    # Attribute _text: A message to display to the player
    # Invariant: _text is a GLabel, or None if there is no message to display
    
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # _sky_tint: a GRectangle over the sunset (so the sky is less bright)
    # _screen_labels: a list of GLabels for whatever screen is up
    # invariant: _screen_labels is a list and each value is a GLabel
    # _screen_shapes: list of rectangles + ellipses + paths for decoration
    # invariant: _screen_shapes only holds objects with a draw method
    # _selected_wave_file: a nonempty filename and keep the case as given
    # invariant: _selected_wave_file is a filename and never empty
    # _sounds_enabled: a bool and the mute choice sticks between waves
    # invariant: _sounds_enabled is always a bool
    # _audio_label: status label on a menu (None during active play)
    # invariant: _audio_label is a GLabel or None
    # _state also allows STATE_SCORING and counting a finished round
    # _campaign_rounds: list of data dictionaries for the current campaign
    # invariant: _campaign_rounds is a list of wave dictionaries
    # _endless_campaign: bool + True if the last round repeats faster
    # invariant: _endless_campaign is a bool
    # _round_number: nonnegative int + current round index starting at zero
    # invariant: _round_number is an int at least zero
    # _saved_cities: None before round one (list of saved city slots later)
    # invariant: _saved_cities is None or a list of original city slots
    # _total_score: nonnegative integer for all finished rounds so far
    # invariant: _total_score is an int at least zero
    # _score_icons: two GImages that briefly grow when a score beat happens
    # invariant: _score_icons is a list of no more than two GImages
    # _score_rocket_text: GLabel counting leftover rockets already scored
    # invariant: _score_rocket_text is a GLabel during score counting
    # _score_city_text: GLabel counting surviving cities already scored
    # invariant: _score_city_text is a GLabel during score counting
    # _round_ammo: 0 to 30 rockets left when a round ends
    # invariant: _round_ammo is an int from 0 to 30
    # _round_cities: 0 to 6 cities left when a round ends
    # invariant: _round_cities is an int from zero to six
    # _counted_ammo: number of rocket icons already counted this round
    # invariant: _counted_ammo is never larger than _round_ammo
    # _counted_cities: number of city icons already counted this round
    # invariant: _counted_cities is never larger than _round_cities
    # _score_time: nonnegative seconds collected for the next score beat
    # invariant: _score_time is nonnegative seconds
    # _score_hold: seconds after all score beats end (never negative)
    # invariant: _score_hold is nonnegative seconds
    # _score_was_loss: True if the current tally follows the loss of all cities
    # invariant: _score_was_loss is a bool
    # _final_shown: number currently displayed on the final score (int >= 0)
    # invariant: _final_shown is an int from zero to _total_score
    # _final_counting: bool (False on menus and loading errors)
    # invariant: _final_counting is a bool
    # _high_score: greatest total saved on this computer (int at least zero)
    # invariant: _high_score is a nonnegative int
    # _menu_glow: a decorative ring that changes size on the menu
    # invariant: _menu_glow is a GEllipse or None
    # _menu_time: seconds spent showing the welcome menu
    # invariant: _menu_time is nonnegative seconds
    
    # DO NOT MAKE A NEW INITIALIZER!
    
    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.
        
        This method is distinct from the built-in initializer __init__ (which 
        you should not override or change). This method is called once the 
        game is running. You should use it to initialize any game specific 
        attributes.
        
        This method should make sure that all of the attributes satisfy the 
        given invariants. When done, it sets the state to STATE_INACTIVE and 
        creates both the title and a message saying that the user should press 
        a key to play a game.
        """
        # IMPLEMENT ME
        self.title = 'missile shield'
        self._state = STATE_INACTIVE
        self._wave = None
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._selected_wave_file = DEFAULT_WAVE
        self._sounds_enabled = True
        self._audio_label = None
        self._campaign_rounds = []
        self._endless_campaign = False
        self._round_number = 0
        self._saved_cities = None
        self._total_score = 0
        self._score_was_loss = False
        self._final_shown = 0
        self._final_counting = False
        self._score_icons = []
        self._prepare_backdrop()
        self._open_menu()

    def update(self, dt):
        """
        It is the method that does most of the work. It is NOT in charge of 
        playing the game. That is the purpose of the class Level. The primary 
        purpose of this game is to determine the current state, and -- if the 
        game is active -- pass the input to the Level object to play the game.
        
        As part of the assignment, you are allowed to add your own states. 
        However, at a minimum you must support the following states: 
        STATE_INACTIVE, STATE_LOADING, STATE_ACTIVE, STATE_PAUSED, and 
        STATE_COMPLETE. Each one of these does its own thing and might even 
        need its own helper. We describe these below.
        
        STATE_INACTIVE: This is the state when the application first opens. 
        It is a paused state, waiting for the player to start the game. It 
        displays the title and a simple message on the screen. The application 
        remains in this state so long as the player never presses a key.
        
        STATE_LOADING: This is the state that creates a new wave and shows it 
        on the screen. The application switches to this state if the state was 
        STATE_INACTIVE in the previous frame, and the player pressed a key. 
        This state only lasts one animation frame (the amount of time to load
        the data from the file) before switching to STATE_ACTIVE. One of the
        key things about this level is that it resizes the window to match the
        level file.
        
        STATE_ACTIVE: This is a session of normal gameplay. The missiles will
        start to arrive and the player can defend against them. All of this 
        should be handled inside of class Wave (NOT in this class). Hence the 
        Wave class should have  an update() method, just like the subcontroller 
        example in lecture.
        
        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, 
        the game is still visible on the screen.
        
        STATE_CONTINUE: Like STATE_LOADING, in that is the frame before playing
        the game. However, instead of loading a new game, it resumes an existing
        game.
        
        STATE_COMPLETE: The level is over (all cities are destroyed or all 
        missiles are shot down), and is either won or lost.
        
        You are allowed to add more states if you wish. Should you do so, you 
        should describe them here.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # IMPLEMENT ME
        self._read_audio_toggle()
        if self._state == STATE_INACTIVE:
            self._update_menu(dt)
        elif self._state == STATE_LOADING:
            self._load_wave()
        elif self._state == STATE_ACTIVE:
            self._update_active(dt)
        elif self._state == STATE_PAUSED:
            self._update_paused()
        elif self._state == STATE_CONTINUE:
            self._continue_wave()
        elif self._state == STATE_SCORING:
            self._update_scoring(dt)
        elif self._state == STATE_COMPLETE:
            self._update_complete(dt)

    def draw(self):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject. To draw 
        a GObject g, simply use the method g.draw(self.view). It is that easy!
        
        While this class will draw the welcome message, most of the game 
        terrain (e.g. silos and cities) are attributes of Wave. In order to 
        draw them, you either need to add getters for these attributes or you 
        need to add a draw method to the class Wave. We suggest the latter. 
        See the example subcontroller.py from lecture.
        """
        # IMPLEMENT ME
        self._background.draw(self.view)
        self._sky_tint.draw(self.view)
        if self._wave is not None:
            self._wave.draw(self.view)
        for current_shape in self._screen_shapes:
            current_shape.draw(self.view)
        for current_icon in self._score_icons:
            current_icon.draw(self.view)
        for current_label in self._screen_labels:
            current_label.draw(self.view)
        if self._title is not None:
            self._title.draw(self.view)
        if self._text is not None:
            self._text.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE
    def on_stop(self):
        """
        stops the sound of the current wave when the window closes
        """
        if hasattr(self, '_wave'):
            self._stop_wave_audio()

    def _clear_messages(self):
        """
        removes labels and shapes from the previous menu or panel (not the
        sky or wave)
        """
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._audio_label = None
        self._score_icons = []

    def _open_menu(self):
        """
        drops the old wave and shows the two start choices (resetting the
        campaign score)
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._state = STATE_INACTIVE
        self._selected_wave_file = DEFAULT_WAVE
        self._campaign_rounds = []
        self._endless_campaign = False
        self._round_number = 0
        self._saved_cities = None
        self._total_score = 0
        self._score_was_loss = False
        self._final_counting = False
        self._menu_time = 0
        self._make_menu_decoration()
        self._make_menu_heading()
        self._make_standard_card()
        self._make_custom_card()
        self._make_menu_controls()
        self._add_center_label('personal best  ' + str(self._high_score),
                               533, 19, UI_ACCENT, THEME_FONT)

    def _update_menu(self, dt):
        """
        keeps the menu moving and checks s for classic or c for campaign
        parameter dt: seconds since the previous screen update
        precondition: dt is a nonnegative number
        """
        self._animate_menu(dt)
        if self.input.is_key_pressed('s'):
            self._begin_loading(DEFAULT_WAVE)
        elif self.input.is_key_pressed('c'):
            self._begin_loading('nightpost_campaign.json')

    def _begin_loading(self, filename):
        """
        saves the requested filename and opens a loading screen for the next
        update
        parameter filename: the exact file to start or retry
        precondition: filename is a nonempty string
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._selected_wave_file = filename
        self._campaign_rounds = []
        self._endless_campaign = False
        self._round_number = 0
        self._saved_cities = None
        self._total_score = 0
        self._score_was_loss = False
        self._final_counting = False
        self._state = STATE_LOADING
        self._make_panel(240)
        self._add_center_label('getting ready', 483, 14, UI_ACCENT)
        self._text = self._make_label('preparing the sky...',
                                     self.width / 2, 427, 36, UI_TEXT)
        self._add_center_label(filename, 375, 16, UI_MUTED)

    def _load_wave(self):
        """
        reads the chosen json and creates a playable wave (or displays its
        loading error)
        """
        loading_step = 'could not read the wave file.'
        next_step = 'check the data folder.'
        try:
            file_information = self._read_wave_file()
            loading_step = 'could not make the wave.'
            next_step = 'check the wave data + try again.'
            if 'rounds' in file_information:
                rounds = file_information['rounds']
                if type(rounds) != list or len(rounds) == 0:
                    raise ValueError('rounds must be a nonempty list')
                self._campaign_rounds = rounds
                self._endless_campaign = file_information.get('endless') is True
            else:
                self._campaign_rounds = [file_information]
                self._endless_campaign = False
            self._round_number = 0
            self._start_round()
        except Exception as error:
            details = type(error).__name__ + ': ' + str(error)
            Logger.exception('MissileShield: ' + details)
            self._show_load_error(loading_step, details, next_step)

    def _read_wave_file(self):
        """
        returns the json dictionary from Data (or raises an error if the file
        fails)
        is_json checks the Data folder of this app. no matching file means
        FileNotFoundError and a failed parse or json null means ValueError
        other errors show their original exception names in the terminal read
        errors reach the loading error screen. parsed data still goes through
        the structure checks in Wave. keep filenames as given because
        changing the case can make a real file look missing
        """
        if not self.is_json(self._selected_wave_file):
            missing_file = 'Missing file: Data/' + self._selected_wave_file
            raise FileNotFoundError(missing_file)
        wave_information = self.load_json(self._selected_wave_file)
        if wave_information is None:
            invalid_file = 'Could not read JSON: Data/'
            raise ValueError(invalid_file + self._selected_wave_file)
        return wave_information

    def _update_active(self, dt):
        """
        pressing p pauses the wave (otherwise advances the wave and checks
        its result)
        parameter dt: seconds since the previous update and must be
        nonnegative
        precondition: dt is a finite number at least zero
        """
        if self.input.is_key_pressed('p'):
            self._pause_wave()
            return
        self._wave.update(self.input, dt)
        if self._wave.getLost():
            # the cities are gone already so we can count the last score now
            self._begin_scoring()
        elif self._wave.getWon():
            self._begin_scoring()

    def _pause_wave(self):
        """
        stops current audio and shows the paused controls without moving the
        wave
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._state = STATE_PAUSED
        self._make_panel(594)
        self._add_center_label(self._wave.getModeName() + ' / paused',
                               679, 14, UI_ACCENT)
        self._text = self._make_label('paused', self.width / 2,
                                     622, 44, UI_TEXT, THEME_FONT)
        self._add_rule(546, 250, 652)
        self._add_center_label('arrow keys to aim   /   1, 2, 3 to fire',
                               513, 19, UI_TEXT)
        if self._wave.getCustomEnabled():
            self._make_custom_help()
        else:
            self._make_standard_help()
        self._add_rule(241, 250, 652)
        self._add_key_hint('r', 'resume', 394, 203, True)
        self._add_key_hint('m', 'back to menu', 622, 203)
        self._make_audio_label(165)

    def _update_paused(self):
        """
        pressing r schedules a resume (pressing m returns to the menu)
        """
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _continue_wave(self):
        """
        removes the pause screen and resumes the same wave without resetting
        it
        """
        self._clear_messages()
        self._state = STATE_ACTIVE

    # the result reads the finished wave (so the score comes from that run)
    def _finish_wave(self, player_won):
        """
        shows a final win or loss result with the running score and remaining
        cities
        parameter player_won: whether the player cleared this wave
        precondition: player_won is a bool and _wave is a Wave
        """
        self._wave.finishSounds(player_won)
        if not player_won and not self._score_was_loss:
            self._total_score = self._total_score + self._wave.getScore()
        self._save_high_score()
        self._clear_messages()
        self._state = STATE_COMPLETE
        self._make_panel(520)
        self._add_card(421, 446, 302, 184, True)
        self._add_card(740, 446, 275, 184, False)
        self._add_center_label('final results', 653, 14, UI_ACCENT)
        if player_won:
            self._make_win_message()
        else:
            self._make_loss_message()
        self._add_key_hint('r', 'play again', 390, 292, True)
        self._add_key_hint('m', 'menu', 654, 292)
        self._final_shown = 0
        self._final_counting = True
        self._text.text = '0'

    def _update_complete(self, dt):
        """checks restart keys and counts the final score toward its real total

        parameter dt: seconds since the last animation frame (at least zero)
        """
        self._animate_final_number(dt)
        if self.input.is_key_pressed('r'):
            self._begin_loading(self._selected_wave_file)
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _animate_final_number(self, dt):
        """moves the number on final results toward the real score

        this only changes the visible label (not the saved or earned points)
        parameter dt: seconds since last frame (a nonnegative number)
        """
        if not self._final_counting:
            return
        steps = int(self._total_score * dt * 1.5)
        if steps < 1:
            steps = 1
        self._final_shown = self._final_shown + steps
        if self._final_shown >= self._total_score:
            self._final_shown = self._total_score
            self._final_counting = False
        self._text.text = str(self._final_shown)

    def _show_load_error(self, loading_step, error_details, next_step):
        """
        shows the failing filename and exception with retry and menu controls
        parameter loading_step: the short description of the failed step
        parameter error_details: the exception type and its message
        parameter next_step: the suggestion for fixing the problem
        precondition: all three parameters are nonempty strings
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._state = STATE_COMPLETE
        self._final_counting = False
        self._make_panel(594)
        self._add_center_label('could not open this sky.', 623, 37,
                               UI_TEXT, THEME_FONT)
        self._text = self._make_label(loading_step, self.width / 2,
                                     575, 21, UI_MUTED)
        self._add_center_label(self._selected_wave_file, 530, 18, UI_ACCENT)
        self._add_error_details(error_details)
        self._add_center_label(next_step, 348, 17, UI_MUTED)
        self._add_center_label('the terminal has the full error + path.',
                               319, 15, UI_MUTED)
        self._add_rule(270, 250, 652)
        self._add_key_hint('r', 'retry', 402, 220, True)
        self._add_key_hint('m', 'back to menu', 622, 220)
        self._make_audio_label(165)

    def _add_error_details(self, error_details):
        """
        puts the exception on at most three short lowercase lines (clipping
        extra text)

        each line holds at most 48 characters the last one can add '...' if
        more words are left is more. words stay together when possible. the
        full text stays in the log (so a huge path does not push the retry
        controls off the screen)
        parameter error_details: the exception type and its message
        precondition: error_details is a nonempty string
        """
        remaining_text = error_details.replace('\n', ' ').strip().lower()
        for line_number in range(3):
            if len(remaining_text) > 48:
                split_position = remaining_text.rfind(' ', 0, 48)
                if split_position < 1:
                    split_position = 48
            else:
                split_position = len(remaining_text)
            current_line = remaining_text[:split_position]
            remaining_text = remaining_text[split_position:].lstrip()
            if line_number == 2 and remaining_text != '':
                current_line = current_line + '...'
            line_height = 468 - 28 * line_number
            self._add_center_label(current_line, line_height, 18, UI_AMBER)

    def _make_menu_decoration(self):
        """
        adds two dark rounded mode cards and the small sky drawing
        """
        self._add_card(315, 294, 486, 192, False)
        self._add_card(837, 294, 486, 192, True)
        self._make_sky_map()

    def _make_sky_map(self):
        """
        makes the decorative map from simple rings and short paths
        """
        for diameter in [460, 350, 240]:
            ring = GEllipse(x=576, y=619, width=diameter, height=diameter,
                            fillcolor=(0, 0, 0, 0), linewidth=1,
                            linecolor=introcs.RGB(247, 207, 121, 35))
            self._screen_shapes.append(ring)
        glow = GEllipse(x=576, y=619, width=275, height=275,
                        fillcolor=introcs.RGB(247, 207, 121, 10))
        self._menu_glow = glow
        self._screen_shapes.append(glow)
        paths = [[193, 688, 316, 734], [959, 685, 833, 737],
                 [363, 455, 443, 496]]
        for points in paths:
            trail = GPath(points=points, linewidth=1.3,
                           linecolor=introcs.RGB(247, 207, 121, 100))
            self._screen_shapes.append(trail)
            dot = GEllipse(x=points[2], y=points[3], width=6, height=6,
                           fillcolor=UI_ACCENT)
            self._screen_shapes.append(dot)
        self._make_map_details()

    def _make_map_details(self):
        """
        adds crosshair lines and small stars to the decorative map
        """
        horizontal = GRectangle(x=576, y=795, width=25, height=1,
                                fillcolor=UI_ACCENT)
        vertical = GRectangle(x=576, y=795, width=1, height=25,
                              fillcolor=UI_ACCENT)
        self._screen_shapes.append(horizontal)
        self._screen_shapes.append(vertical)
        stars = [[280, 645], [935, 545], [940, 740], [350, 472]]
        for position in stars:
            star = GEllipse(x=position[0], y=position[1], width=3,
                            height=3, fillcolor=UI_ACCENT)
            self._screen_shapes.append(star)

    def _make_menu_heading(self):
        """
        puts the lowercase game title above the start cards
        """
        shadow = self._make_label('missile shield', self.width / 2,
                                  621, 100, UI_BG, DISPLAY_FONT, 800)
        shadow.y = 617
        self._screen_labels.append(shadow)
        self._title = self._make_label('missile shield', self.width / 2,
                                      621, 100, UI_TEXT, DISPLAY_FONT, 800)

    def _make_standard_card(self):
        """
        labels the normal mode and explains that it plays the selected json
        wave
        """
        self._add_keycap('s', 104, 348, False)
        self._add_left_label('classic', 134, 348, 23,
                             UI_TEXT, THEME_FONT)
        self._add_left_label('stop falling bombs before they hit the cities.',
                             96, 305, 17, UI_MUTED, limit=420)
        self._add_left_label('press s to play', 96, 269, 17, UI_TEXT)

    def _make_custom_card(self):
        """
        labels the campaign and names its extra aiming and defense tools
        """
        self._add_keycap('c', 626, 348, True)
        self._add_left_label('campaign', 656, 348, 23,
                             UI_TEXT, THEME_FONT)
        self._add_left_label('protect cities through harder rounds.',
                             618, 305, 17, UI_MUTED, limit=425)
        self._add_left_label('press c to play', 618, 269, 17, UI_ACCENT)

    def _make_menu_controls(self):
        """
        shows the basic aiming and firing keys at the bottom of the menu
        """
        self._text = None
        self._add_key_hint('arrows', 'aim', 299, 101)
        self._add_key_hint('1 / 2 / 3', 'fire', 507, 101)
        self._add_key_hint('p', 'pause', 720, 101)
        self._make_audio_label(45)

    def _make_custom_help(self):
        """
        adds one help line for each enabled custom feature of this wave
        """
        help_rows = self._wave.getHelpRows()
        for row_number in range(len(help_rows)):
            row_text = help_rows[row_number]
            row_y = 465 - row_number * 42
            self._add_center_label(row_text, row_y, 17, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               284, 15, UI_ACCENT)

    def _make_standard_help(self):
        """
        describes firing rockets into bomb paths and saving at least one city
        """
        self._add_center_label('fire from the left, center, or right silo.',
                               455, 19, UI_MUTED)
        self._add_center_label('rockets burst at the point where you aimed.',
                               414, 19, UI_MUTED)
        self._add_center_label('catch falling bombs inside the growing blast.',
                               373, 19, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               308, 19, UI_ACCENT)
        
    def _make_win_message(self):
        """shows total points on the left and saved cities on the right"""
        self._add_center_label('wave cleared', 595, 40,
                               UI_TEXT, DISPLAY_FONT)
        self._make_result_numbers()

    def _make_loss_message(self):
        """shows the total score after every city has already been lost"""
        self._add_center_label('all cities destroyed', 595, 37,
                               UI_DANGER, DISPLAY_FONT)
        self._make_result_numbers()

    def _make_result_numbers(self):
        """centers the score name and number as one group inside the left card

        the card center is (421, 446). its small label is above the number
        and both words fit in the card with a gap between them
        """
        # pls help why was this so hard to center 😭
        score_name = self._make_label('total score', 421, 494,
                                      17, UI_MUTED)
        self._screen_labels.append(score_name)
        self._text = self._make_label(str(self._total_score), 421, 428,
                                      76, UI_ACCENT, THEME_FONT)
        self._add_left_label('cities saved', 663, 516, 17, UI_MUTED)
        saved = str(self._wave.getCitiesLeft()) + ' / 6'
        self._add_left_label(saved, 663, 472, 34, UI_TEXT, THEME_FONT)
        self._add_left_label('rounds cleared', 663, 418, 17, UI_MUTED)
        count = self._round_number
        if not self._score_was_loss:
            count = count + 1
        self._add_left_label(str(count), 663, 377, 32, UI_TEXT, THEME_FONT)
        # i can't believe the other numbers lined up finally 😭

    def _make_panel(self, panel_height):
        """
        dims the sunset and adds one centered borderless rounded dark panel

        parameter panel_height: height of the panel + greater than zero
        """
        veil = GRectangle(x=self.width / 2, y=self.height / 2,
                          width=self.width, height=self.height,
                          fillcolor=introcs.RGB(3, 7, 12, 123))
        self._screen_shapes.append(veil)
        self._add_card(self.width / 2, self.height / 2,
                       760, panel_height, False)

    def _add_card(self, center_x, center_y, width, height, highlighted):
        """
        adds a borderless dark card using simple rectangles and round corner
        circles

        parameter center_x: horizontal center and must be a number
        parameter center_y: vertical center and must be a number
        parameter width: positive card width
        parameter height: positive card height
        parameter highlighted: True uses the brighter dark fill
        precondition: highlighted is a bool
        """
        fill = UI_SURFACE
        if highlighted:
            fill = UI_SURFACE_SOFT
        radius = 19
        middle = GRectangle(x=center_x, y=center_y,
                            width=width - 2 * radius, height=height,
                            fillcolor=fill)
        side = GRectangle(x=center_x, y=center_y,
                          width=width, height=height - 2 * radius,
                          fillcolor=fill)
        self._screen_shapes.extend([middle, side])
        self._add_card_corners(center_x, center_y, width, height, radius, fill)

    def _add_rule(self, y, left=72, width=1008):
        """
        adds one thin horizontal divider at the given height

        parameter y: vertical position and must be a number
        parameter left: left edge and must be a number
        parameter width: line width and must be a positive number
        precondition: y is a number
        """
        divider = GRectangle(x=left + width / 2, y=y,
                             width=width, height=1, fillcolor=UI_BORDER)
        self._screen_shapes.append(divider)

    # a keycap is a label and box (so it never reads the keyboard itself)
    def _add_keycap(self, key, x, y, highlighted):
        """
        makes a little box and text label for one keyboard key

        parameter key: key name and must be a nonempty string
        parameter x: horizontal center and must be a number
        parameter y: vertical center and must be a number
        parameter highlighted: whether this is a primary action
        precondition: highlighted is a bool
        """
        key_width = max(28, len(key) * 7 + 16)
        key_color = UI_TEXT
        if highlighted:
            key_color = UI_ACCENT
        key_shape = GRectangle(x=x, y=y, width=key_width, height=28,
                               linewidth=0,
                               fillcolor=UI_SURFACE_SOFT)
        self._screen_shapes.append(key_shape)
        key_label = self._make_label(key, x, y, 14, key_color, THEME_FONT)
        self._screen_labels.append(key_label)

    def _add_key_hint(self, key, words, x, y, highlighted=False):
        """
        puts one action label next to its keyboard key badge

        parameter key: key name and must be a nonempty string
        parameter words: action description and must be a string
        parameter x: center of the key and must be a number
        parameter y: vertical center and must be a number
        parameter highlighted: whether this is the primary action
        precondition: highlighted is a bool
        """
        self._add_keycap(key, x, y, highlighted)
        key_width = max(28, len(key) * 7 + 16)
        label_left = x + key_width / 2 + 12
        label_color = UI_MUTED
        if highlighted:
            label_color = UI_TEXT
        self._add_left_label(words, label_left, y, 17, label_color)

    def _read_audio_toggle(self):
        """
        switches sound once each time v is newly pressed (not every held
        frame)
        """
        if self.input.is_key_pressed('v'):
            self._sounds_enabled = not self._sounds_enabled
            if self._wave is not None:
                self._wave.setSoundsEnabled(self._sounds_enabled)
            if self._audio_label is not None:
                self._audio_label.text = self._get_audio_words()

    def _stop_wave_audio(self):
        """
        stops sounds already playing but keeps the current mute setting
        """
        if self._wave is not None:
            self._wave.stopSounds()

    def _get_audio_words(self):
        """
        returns the text for muted sound or enabled sound or unavailable
        audio
        """
        if not self._sounds_enabled:
            words_for_sound = 'sound off   /   v to unmute'
            return words_for_sound
        if self._wave is not None:
            if not self._wave.getSoundsAvailable():
                words_for_sound = 'audio unavailable'
                more_sound_words = '   /   gameplay is still ready'
                words_for_sound = words_for_sound + more_sound_words
                return words_for_sound
        words_for_sound = 'sound on   /   v to mute'
        return words_for_sound

    def _make_audio_label(self, y):
        """
        puts the current sound status in the panel footer

        parameter y: vertical center and must be a number
        precondition: y is a number
        """
        self._audio_label = self._make_label(self._get_audio_words(),
                                            self.width / 2, y, 14, UI_MUTED)
        self._screen_labels.append(self._audio_label)

    def _add_center_label(self, words, y, size, color, font=BASIC_FONT):
        """
        creates a lowercase label at the horizontal center and adds it to
        this screen

        parameter words: text to display and must be a string
        parameter y: vertical center and must be a number
        parameter size: font size and must be positive
        parameter color: text color and must be a valid game2d color
        parameter font: font file and must name a supplied .ttf font
        precondition: y is a number
        """
        current_label = self._make_label(words, self.width / 2, y,
                                         size, color, font, 690)
        self._screen_labels.append(current_label)

    def _add_left_label(self, words, left, y, size, color,
                        font=BASIC_FONT, limit=500):
        """
        creates a lowercase label and puts its left edge at the requested
        position

        parameter words: text to display and must be a string
        parameter left: left edge and must be a number
        parameter y: vertical center and must be a number
        parameter size: font size and must be positive
        parameter color: text color and must be a valid game2d color
        parameter font: font file and must name a supplied .ttf font
        parameter limit: maximum text width and must be positive
        precondition: y is a number
        """
        current_label = self._make_label(words, 0, y, size,
                                         color, font, limit)
        current_label.halign = 'left'
        current_label.left = left
        self._screen_labels.append(current_label)

    def _make_label(self, words, x, y, size, color,
                    font=BASIC_FONT, limit=1008):
        """
        returns a lowercase GLabel whose font shrinks until it fits the width
        limit

        setting font_size refreshes the real text texture through the public
        GLabel property (so the width check measures the actual letters. use
        a fresh label when shrinking because the old rectangle only gets
        bigger)
        parameter words: text to display and must be a string
        parameter x: horizontal center and must be a number
        parameter y: vertical center and must be a number
        parameter size: wanted font size and must be positive
        parameter color: text color and must be a valid game2d color
        parameter font: font file and must name a supplied .ttf font
        parameter limit: maximum text width and must be positive
        precondition: y is a number
        """
        chosen_size = size
        current_label = GLabel(text=words.lower(), x=x, y=y,
                               font_size=chosen_size, font_name=font,
                               linecolor=color)
        current_label.font_size = chosen_size
        while current_label.width > limit and chosen_size > 1:
            chosen_size = chosen_size - 1
            current_label = GLabel(text=words.lower(), x=x, y=y,
                                   font_size=chosen_size, font_name=font,
                                   linecolor=color)
            current_label.font_size = chosen_size
        label_for_this_spot = current_label
        return label_for_this_spot

    def _add_card_corners(self, x, y, width, height, radius, color):
        """
        adds four filled circles at the corners of a dark card to make
        rounded ends

        parameter x: horizontal center of the card
        parameter y: vertical center of the card
        parameter width: full card width in pixels
        parameter height: full card height in pixels
        parameter radius: radius of each rounded corner in pixels
        parameter color: fill color used by all four corner circles
        precondition: x and y and width and height and radius are numbers
        precondition: width and height and radius are positive
        precondition: color is valid for a game2d filled ellipse
        """
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for side_x, side_y in offsets:
            corner_x = x + side_x * (width / 2 - radius)
            corner_y = y + side_y * (height / 2 - radius)
            corner = GEllipse(x=corner_x, y=corner_y,
                              width=2 * radius, height=2 * radius,
                              fillcolor=color)
            self._screen_shapes.append(corner)

    def _prepare_backdrop(self):
        """sets the saved score and the background once at startup"""
        self._high_score = self._read_high_score()
        self._menu_glow = None
        self._menu_time = 0
        self._background = GImage(source=BACKGROUND, width=self.width,
                                  height=self.height, x=self.width / 2,
                                  y=self.height / 2)
        nighttime_color = introcs.RGB(5, 16, 26, 88)
        self._sky_tint = GRectangle(x=self.width / 2, y=self.height / 2,
                                   width=self.width, height=self.height,
                                   fillcolor=nighttime_color)

    def _high_score_path(self):
        """returns the path of the small optional local score file"""
        here = os.path.dirname(__file__)
        return os.path.join(here, 'Data', 'highscore.txt')

    def _read_high_score(self):
        """returns the saved score as an int (or zero if the file is missing)"""
        try:
            score_file = open(self._high_score_path(), 'r')
            words = score_file.read().strip()
            score_file.close()
            if words.isdigit():
                return int(words)
        except (OSError, ValueError):
            pass
        return 0

    def _save_high_score(self):
        """saves a personal best without crashing if the disk is unavailable"""
        if self._total_score <= self._high_score:
            return
        self._high_score = self._total_score
        try:
            score_file = open(self._high_score_path(), 'w')
            score_file.write(str(self._high_score))
            score_file.close()
        except OSError:
            pass

    def _animate_menu(self, dt):
        """makes the faint gold ring breathe without affecting the game"""
        self._menu_time = self._menu_time + dt
        if self._menu_glow is not None:
            pulse = (self._menu_time % 3.2) / 3.2
            diameter = 235 + 65 * pulse
            self._menu_glow.width = diameter
            self._menu_glow.height = diameter

    def _start_round(self):
        """
        creates the next Wave with saved cities (reusing the last json at
        higher speed)

        the first round creates all six cities and later rounds keep only
        survivors
        campaigns with endless enabled repeat the final designed round at
        higher speed
        """
        number_in_file = self._round_number
        if number_in_file >= len(self._campaign_rounds):
            number_in_file = len(self._campaign_rounds) - 1
        information = dict(self._campaign_rounds[number_in_file])
        if self._endless_campaign or len(self._campaign_rounds) > 1:
            information['round_number'] = self._round_number + 1
        if self._round_number >= len(self._campaign_rounds):
            extra_rounds = self._round_number - len(self._campaign_rounds) + 1
            information['speed'] = information['speed'] + 5 * extra_rounds
        self._wave = Wave(information, self._saved_cities)
        self._wave.showRoundStart()
        self._wave.setSoundsEnabled(self._sounds_enabled)
        self._wave.startSounds()
        self._clear_messages()
        self._state = STATE_ACTIVE

    def _begin_scoring(self):
        """
        saves the ammo and city counts before the score starts its animation

        loss already ended the wave so its final points can still count here
        """
        self._wave.stopSounds()
        self._score_was_loss = self._wave.getLost()
        self._saved_cities = self._wave.getSurvivingSlots()
        total_ammunition = 0
        for ammo_count in self._wave.getAmmoCounts():
            total_ammunition = total_ammunition + ammo_count
        self._round_ammo = total_ammunition
        self._round_cities = self._wave.getCitiesLeft()
        self._counted_ammo = 0
        self._counted_cities = 0
        self._score_time = 0
        self._score_hold = 0
        self._clear_messages()
        self._state = STATE_SCORING
        self._make_scoring_panel()

    def _make_scoring_panel(self):
        """
        makes the score display with one large icon for each point source

        the numbers start at zero (and grow one item each beat)
        rockets are 5 points each and surviving cities are 100 points each
        """
        self._make_panel(530)
        number = str(self._round_number + 1)
        heading = 'round ' + number + ' cleared'
        if self._score_was_loss:
            heading = 'final score'
        self._add_center_label(heading, 650, 35, UI_TEXT, DISPLAY_FONT)
        self._add_center_label('total score', 583, 16, UI_MUTED)
        self._text = self._make_label(str(self._total_score),
                                     self.width / 2, 525, 63,
                                     UI_ACCENT, THEME_FONT)
        self._make_score_rows()
        if self._has_next_round():
            self._add_key_hint('n / r', 'next round', 386, 325, True)
        else:
            self._add_key_hint('n / r', 'see results', 386, 325, True)
        self._add_key_hint('m', 'menu', 692, 325)

    def _make_score_rows(self):
        """
        puts the rocket count next to a rocket picture (same for cities)

        the labels change as the score animation counts each item
        """
        self._score_icons = []
        rocket = GImage(source='missile@2x.png', x=330, y=421,
                        width=24, height=46)
        city = GImage(source='city@2x.png', x=659, y=421,
                      width=48, height=46)
        self._score_icons.append(rocket)
        self._score_icons.append(city)
        self._score_rocket_text = self._make_label('', 478, 421,
                                                  19, UI_TEXT)
        self._score_city_text = self._make_label('', 796, 421,
                                                19, UI_TEXT)
        self._screen_labels.append(self._score_rocket_text)
        self._screen_labels.append(self._score_city_text)
        self._refresh_score_rows()

    def _refresh_score_rows(self):
        """shows how many rockets and cities have been counted so far"""
        rockets = str(self._counted_ammo) + '/' + str(self._round_ammo)
        cities = str(self._counted_cities) + '/' + str(self._round_cities)
        self._score_rocket_text.text = rockets + ' rockets  (+5 each)'
        self._score_city_text.text = cities + ' cities  (+100 each)'

    def _shrink_score_icons(self, dt):
        """gently shrinks the picture after each score beat

        parameter dt: seconds since the last frame (a nonnegative number)
        """
        for icon in self._score_icons:
            if icon.height > 46:
                icon.height = max(46, icon.height - 80 * dt)

    def _update_scoring(self, dt):
        """
        adds one rocket or city score beat every 0.085 seconds

        n or r skips the rest of the tally and moves to the next screen
        a failed or single wave shows the final results after a short hold
        parameter dt: elapsed seconds from the last frame
        precondition: dt is a nonnegative number
        """
        if self.input.is_key_pressed('m'):
            self._open_menu()
            return
        if self.input.is_key_pressed('n') or self.input.is_key_pressed('r'):
            self._finish_score_count()
            self._move_past_score()
            return
        self._shrink_score_icons(dt)
        self._score_time = self._score_time + dt
        while self._score_time >= 0.085:
            self._score_time = self._score_time - 0.085
            if not self._count_score_item():
                if not self._has_next_round():
                    self._score_hold = self._score_hold + 0.085
                    if self._score_hold >= 1.2:
                        self._move_past_score()
                        return
                else:
                    break

    def _count_score_item(self):
        """
        adds one leftover rocket (5 points) or one living city (100 points)

        returns True if it counted something and False if the tally is done
        each item updates its count and makes the matching sound and image pulse
        """
        if self._counted_ammo < self._round_ammo:
            self._counted_ammo = self._counted_ammo + 1
            self._total_score = self._total_score + SCORE_AMMO
            self._add_score_icon('missile@2x.png', self._counted_ammo, 0)
            self._wave.playScoreTick(0)
        elif self._counted_cities < self._round_cities:
            self._counted_cities = self._counted_cities + 1
            self._total_score = self._total_score + SCORE_CITY
            self._add_score_icon('city@2x.png', self._counted_cities, 1)
            self._wave.playScoreTick(1)
        else:
            self._save_high_score()
            return False
        self._text.text = str(self._total_score)
        self._refresh_score_rows()
        return True

    def _add_score_icon(self, filename, index, kind):
        """
        makes one existing score icon grow briefly for its next counted item

        parameter filename: supplied sprite name for this item (a string)
        parameter index: number of these items already counted (int >= 1)
        parameter kind: 0 for a rocket or 1 for a city
        precondition: kind is 0 or 1 and index is at least 1
        """
        if kind == 0:
            self._score_icons[0].height = 58
        else:
            self._score_icons[1].height = 58

    def _finish_score_count(self):
        """
        adds all uncounted score items at once when the player skips the
        animation
        """
        missing_ammo = self._round_ammo - self._counted_ammo
        missing_cities = self._round_cities - self._counted_cities
        self._total_score = self._total_score + missing_ammo * SCORE_AMMO
        self._total_score = self._total_score + missing_cities * SCORE_CITY
        self._save_high_score()
        self._counted_ammo = self._round_ammo
        self._counted_cities = self._round_cities
        self._text.text = str(self._total_score)
        self._refresh_score_rows()

    def _has_next_round(self):
        """
        returns True only if this was a win and another campaign round exists

        endless campaigns reuse the last wave after the designed rounds
        loss never allows another round because no cities remain
        """
        if self._score_was_loss:
            return False
        more_rounds = self._round_number + 1 < len(self._campaign_rounds)
        if self._endless_campaign:
            more_rounds = True
        return more_rounds

    def _move_past_score(self):
        """
        starts the next campaign round after a win or shows final results

        losing always goes to final results because every city is gone
        """
        self._save_high_score()
        if self._score_was_loss:
            self._finish_wave(False)
        elif self._has_next_round():
            self._round_number = self._round_number + 1
            try:
                self._start_round()
            except Exception as error:
                details = type(error).__name__ + ': ' + str(error)
                self._show_load_error('could not start the next round.',
                                      details, 'check the campaign json.')
        else:
            self._finish_wave(True)


# omg this took so long 😭