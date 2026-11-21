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
    # _sky_tint: a GRectangle over the sunset, so the sky is less bright.
    # _screen_labels: a list of GLabels for whatever screen is up.
    # _screen_shapes: a list of GRectangles, GEllipses, or GPaths for looks.
    # _selected_wave_file: a nonempty filename; keep the case as given.
    # _sounds_enabled: a bool; the mute choice sticks between waves.
    # _audio_label: a GLabel on menus/panels, or None while playing.
    
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
        self.title = 'missile shield / night post'
        self._state = STATE_INACTIVE
        self._wave = None
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._selected_wave_file = DEFAULT_WAVE
        self._sounds_enabled = True
        self._audio_label = None
        self._background = GImage(source=BACKGROUND, width=self.width,
                                  height=self.height, x=self.width / 2,
                                  y=self.height / 2)
        nighttime_color = introcs.RGB(5, 16, 26, 216)
        self._sky_tint = GRectangle(x=self.width / 2, y=self.height / 2,
                                   width=self.width, height=self.height,
                                   fillcolor=nighttime_color)
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
            self._update_menu()
        elif self._state == STATE_LOADING:
            self._load_wave()
        elif self._state == STATE_ACTIVE:
            self._update_active(dt)
        elif self._state == STATE_PAUSED:
            self._update_paused()
        elif self._state == STATE_CONTINUE:
            self._continue_wave()
        elif self._state == STATE_COMPLETE:
            self._update_complete()

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
        for current_label in self._screen_labels:
            current_label.draw(self.view)
        if self._title is not None:
            self._title.draw(self.view)
        if self._text is not None:
            self._text.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE

    # closing early can happen before a wave exists, so check first.
    def on_stop(self):
        """cuts off leftover wave sounds when the window closes."""
        if hasattr(self, '_wave'):
            self._stop_wave_audio()

    # the sky stays put while each screen gets fresh labels and shapes.
    def _clear_messages(self):
        """clears the old screen stuff, but keeps the sky and wave."""
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._audio_label = None

    # going back to the menu ends this wave and keeps the mute choice.
    def _open_menu(self):
        """opens the menu again, so the old wave is done here."""
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._state = STATE_INACTIVE
        self._selected_wave_file = DEFAULT_WAVE
        self._make_menu_decoration()
        self._make_menu_heading()
        self._make_standard_card()
        self._make_custom_card()
        self._make_menu_controls()

    # s uses the selected file, while c always picks the custom wave.
    def _update_menu(self):
        """checks s for the selected file or c for night post."""
        if self.input.is_key_pressed('s'):
            self._begin_loading(DEFAULT_WAVE)
        elif self.input.is_key_pressed('c'):
            self._begin_loading('nightpost.json')

    # show loading now so the actual load gets the next frame.
    def _begin_loading(self, filename):
        """
        gets ready to load this exact file on the next frame.

        parameter filename: the exact file to start or retry
        precondition: filename is a nonempty string
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._selected_wave_file = filename
        self._state = STATE_LOADING
        self._make_panel(240)
        self._add_center_label('getting ready', 483, 14, UI_ACCENT)
        self._text = self._make_label('preparing the sky...',
                                     self.width / 2, 427, 36, UI_TEXT)
        self._add_center_label(filename, 375, 16, UI_MUTED)

    # read the file, then build the wave, so errors name the failed step.
    def _load_wave(self):
        """
        loads the file and makes a wave, then starts the sound if that worked.

        if something breaks, the error says which step failed and what happened.
        the screen stays lowercase, but the terminal keeps the full traceback
        and original case because paths and exception names need to stay exact.
        """
        loading_step = 'could not read the wave file.'
        next_step = 'check the selected file inside the data folder.'
        try:
            wave_information = self._read_wave_file()
            loading_step = 'could not create the wave.'
            next_step = 'check the wave values and use '
            next_step = next_step + 'one complete shield folder.'
            self._wave = Wave(wave_information)
            self._wave.setSoundsEnabled(self._sounds_enabled)
            self._wave.startSounds()
            self._clear_messages()
            self._state = STATE_ACTIVE
        except Exception as e:
            error_details = type(e).__name__ + ': ' + str(e)
            Logger.exception('MissileShield: ' + error_details)
            self._show_load_error(loading_step, error_details, next_step)

    # file paths keep the real case, so the loader finds the right file.
    def _read_wave_file(self):
        """
        returns the selected wave data, or raises an error that says why.

        is_json checks the Data folder of this app. no matching file means
        FileNotFoundError; a failed parse or json null means ValueError. other
        read errors reach the loading error screen. parsed data still goes
        through the structure checks in Wave. keep filenames as given because
        changing the case can make a real file look missing.
        """
        if not self.is_json(self._selected_wave_file):
            missing_file = 'Missing file: Data/' + self._selected_wave_file
            raise FileNotFoundError(missing_file)
        wave_information = self.load_json(self._selected_wave_file)
        if wave_information is None:
            invalid_file = 'Could not read JSON: Data/'
            raise ValueError(invalid_file + self._selected_wave_file)
        return wave_information

    # only active play calls the regular wave update.
    def _update_active(self, dt):
        """
        pauses on p; otherwise updates the wave and checks loss before a win.

        parameter dt: real seconds since the previous update
        precondition: dt is nonnegative and _wave is a Wave
        """
        if self.input.is_key_pressed('p'):
            self._pause_wave()
            return
        self._wave.update(self.input, dt)
        if self._wave.getLost():
            self._finish_wave(False)
        elif self._wave.getWon():
            self._finish_wave(True)

    # pause keeps the same wave, but freezes movement and stops sounds.
    def _pause_wave(self):
        """
        pauses the game and sound, then puts the right controls on screen.
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._state = STATE_PAUSED
        self._make_panel(594)
        self._add_center_label(self._wave.getModeName() + ' / paused',
                               679, 14, UI_ACCENT)
        self._text = self._make_label('take a breath.', self.width / 2,
                                     622, 44, UI_TEXT, THEME_FONT)
        self._add_center_label('the sky can wait.', 575, 18, UI_MUTED)
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

    # r keeps this run, while m leaves it for the menu.
    def _update_paused(self):
        """waits here for r to keep playing or m to head back."""
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    # resuming clears the pause panel without making another wave.
    def _continue_wave(self):
        """takes the pause screen away, so the same wave can keep going."""
        self._clear_messages()
        self._state = STATE_ACTIVE

    # the result reads the finished wave, so the score comes from that run.
    def _finish_wave(self, player_won):
        """
        puts the result on screen and plays one completion cue.

        parameter player_won: whether the player cleared this wave
        precondition: player_won is a bool and _wave is a Wave
        """
        self._wave.finishSounds(player_won)
        self._clear_messages()
        self._state = STATE_COMPLETE
        self._make_panel(520)
        self._add_center_label(self._wave.getModeName() + ' / complete',
                               651, 14, UI_ACCENT)
        if player_won:
            self._make_win_message()
        else:
            self._make_loss_message()
        self._add_rule(356, 250, 652)
        self._add_key_hint('r', 'play again', 374, 301, True)
        self._add_key_hint('m', 'back to menu', 622, 301)
        self._make_audio_label(226)

    # retry uses the same saved filename, including a custom wave.
    def _update_complete(self):
        """checks r to retry the same file or m to go back to the menu."""
        if self.input.is_key_pressed('r'):
            self._begin_loading(self._selected_wave_file)
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    # a failed load uses the result state too, so retry still works.
    def _show_load_error(self, loading_step, error_details, next_step):
        """
        shows what failed, which file it was, and how to retry or leave.

        parameter loading_step: the short description of the failed step
        parameter error_details: the exception type and its message
        parameter next_step: the suggestion for fixing the problem
        precondition: all three parameters are nonempty strings
        """
        self._stop_wave_audio()
        self._clear_messages()
        self._wave = None
        self._state = STATE_COMPLETE
        self._make_panel(594)
        self._add_center_label('a small interruption', 677, 14, UI_AMBER)
        self._add_center_label('could not open this sky.', 623, 37,
                               UI_TEXT, THEME_FONT)
        self._text = self._make_label(loading_step, self.width / 2,
                                     575, 21, UI_MUTED)
        self._add_center_label(self._selected_wave_file, 530, 18, UI_ACCENT)
        self._add_error_details(error_details)
        self._add_center_label(next_step, 348, 17, UI_MUTED)
        self._add_center_label('the terminal has the full error and path.',
                               319, 15, UI_MUTED)
        self._add_rule(270, 250, 652)
        self._add_key_hint('r', 'retry', 402, 220, True)
        self._add_key_hint('m', 'back to menu', 622, 220)
        self._make_audio_label(165)

    # long errors wrap here; the terminal still has the complete message.
    def _add_error_details(self, error_details):
        """
        fits the error into three short lowercase lines, then cuts it off.

        each slice holds at most 48 characters; the last can add '...' if there
        is more. words stay together when possible. the full text stays in the
        log, so a huge path does not push the retry controls off the screen.

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

    # these shapes sit behind the menu text and do not change the game.
    def _make_menu_decoration(self):
        """adds the header, two mode cards, and the little sky map."""
        self._add_left_label('night post', 72, 811, 20, UI_TEXT, THEME_FONT)
        self._add_left_label('missile shield / after hours',
                             830, 811, 14, UI_MUTED)
        self._add_rule(778)
        self._add_card(315, 294, 486, 192, False)
        self._add_card(837, 294, 486, 192, True)
        self._make_sky_map()
        self._add_rule(166)

    # the little map is decoration, so no real bombs get made here.
    def _make_sky_map(self):
        """builds the sky map out of rings, lines, and a few stars."""
        for diameter in [318, 238, 152]:
            ring = GEllipse(x=865, y=599, width=diameter, height=diameter,
                            fillcolor=(0, 0, 0, 0), linewidth=1,
                            linecolor=introcs.RGB(145, 231, 215, 52))
            self._screen_shapes.append(ring)
        glow = GEllipse(x=865, y=599, width=151, height=151,
                        fillcolor=introcs.RGB(145, 231, 215, 14))
        self._screen_shapes.append(glow)
        paths = [[720, 704, 805, 624], [1002, 712, 913, 597],
                 [748, 504, 865, 599]]
        for points in paths:
            trail = GPath(points=points, linewidth=1.3,
                           linecolor=introcs.RGB(145, 231, 215, 130))
            self._screen_shapes.append(trail)
            dot = GEllipse(x=points[2], y=points[3], width=6, height=6,
                           fillcolor=UI_ACCENT)
            self._screen_shapes.append(dot)
        self._make_map_details()

    def _make_map_details(self):
        """adds a tiny aiming mark, some stars, and the map caption."""
        horizontal_mark = GRectangle(x=865, y=599, width=25, height=1,
                                      fillcolor=UI_ACCENT)
        vertical_mark = GRectangle(x=865, y=599, width=1, height=25,
                                    fillcolor=UI_ACCENT)
        self._screen_shapes.append(horizontal_mark)
        self._screen_shapes.append(vertical_mark)
        self._add_left_label('a quieter kind of night shift',
                             751, 418, 14, UI_MUTED)
        star_positions = [[700, 605], [999, 545], [940, 740], [796, 458]]
        for position in star_positions:
            star = GEllipse(x=position[0], y=position[1], width=3, height=3,
                            fillcolor=introcs.RGB(237, 245, 241, 90))
            self._screen_shapes.append(star)

    # the big title sits above the choices so both cards stay readable.
    def _make_menu_heading(self):
        """adds the lowercase title and the goal above the two cards."""
        self._add_left_label('civil defense / night shift',
                             74, 746, 15, UI_ACCENT)
        self._title = self._make_label('missile\nshield.', 72, 627,
                                      86, UI_TEXT, THEME_FONT, 500)
        self._title.halign = 'left'
        self._title.left = 68
        self._add_left_label('keep the city lights on.',
                             74, 506, 26, UI_TEXT)
        description = 'one sky. six cities. every interception matters.'
        self._add_left_label(description, 74, 466, 17, UI_MUTED)

    def _make_standard_card(self):
        """labels the s card with the exact wave picked on the command line."""
        self._add_keycap('s', 104, 348, False)
        self._add_left_label('selected wave', 134, 348, 23,
                             UI_TEXT, THEME_FONT)
        self._add_left_label('start the wave chosen for this session.',
                             96, 307, 17, UI_MUTED)
        self._add_left_label('selected / ' + DEFAULT_WAVE,
                             96, 275, 15, UI_MUTED, limit=430)
        self._add_left_label('press s to start', 96, 233, 17, UI_TEXT)

    def _make_custom_card(self):
        """gives the four extra tools a quick intro on the c card."""
        self._add_keycap('c', 626, 348, True)
        self._add_left_label('night post', 656, 348, 23,
                             UI_TEXT, THEME_FONT)
        self._add_left_label('forecasts / saved aim / a slow field',
                             618, 307, 17, UI_MUTED)
        self._add_left_label('plus ammo rewards for interceptions.',
                             618, 275, 15, UI_MUTED)
        self._add_left_label('press c to enter night post',
                             618, 233, 17, UI_ACCENT)

    def _make_menu_controls(self):
        """shows the basic keys and where to find the rest of the help."""
        self._text = self._make_label('choose a wave. make every shot count.',
                                     self.width / 2, 136, 18, UI_MUTED)
        self._add_key_hint('arrows', 'aim', 299, 92)
        self._add_key_hint('1 / 2 / 3', 'fire', 507, 92)
        self._add_key_hint('p', 'pause + help', 720, 92)
        self._make_audio_label(41)

    # ask the wave for enabled controls so disabled tools stay out of help.
    def _make_custom_help(self):
        """shows help for the tools turned on in this wave, and only those."""
        help_rows = self._wave.getHelpRows()
        for row_number in range(len(help_rows)):
            row_text = help_rows[row_number]
            row_y = 465 - row_number * 42
            self._add_center_label(row_text, row_y, 17, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               284, 15, UI_ACCENT)

    # the standard help explains launch points, blasts, and saving a city.
    def _make_standard_help(self):
        """breaks the regular goal into a few short lines."""
        self._add_center_label('fire from the left, center, or right silo.',
                               455, 19, UI_MUTED)
        self._add_center_label('rockets burst at the point where you aimed.',
                               414, 19, UI_MUTED)
        self._add_center_label('catch falling bombs inside the growing blast.',
                               373, 19, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               308, 19, UI_ACCENT)
        # ugh im so tired but the spacing finally makes sense 😭

    # the score and survival counts come from the wave through getters.
    def _make_win_message(self):
        """shows the score, plus how many cities and rounds made it through."""
        self._add_center_label('city lights: on.', 595, 42,
                               UI_TEXT, THEME_FONT)
        self._add_center_label('total score', 538, 15, UI_MUTED)
        score_words = str(self._wave.getScore())
        self._text = self._make_label(score_words, self.width / 2,
                                     476, 82, UI_ACCENT, THEME_FONT)
        total_ammo = 0
        for amount in self._wave.getAmmoCounts():
            total_ammo = total_ammo + amount
        result = str(self._wave.getCitiesLeft()) + ' cities saved'
        result = result + '   /   ' + str(total_ammo) + ' rounds left'
        self._add_center_label(result, 396, 19, UI_MUTED)

    # the loss panel explains the result without restarting the wave.
    def _make_loss_message(self):
        """shows the loss right away because the last city is gone."""
        self._add_center_label('lights out.', 587, 44,
                               UI_DANGER, THEME_FONT)
        self._text = self._make_label('all six cities were lost.',
                                     self.width / 2, 515, 27, UI_TEXT)
        self._add_center_label('the night shift ends here.',
                               457, 20, UI_MUTED)
        self._add_center_label('there is another sky to save.',
                               412, 18, UI_MUTED)

    # screens reuse one panel style, with room set by the requested height.
    def _make_panel(self, panel_height):
        """
        dims the game and puts a readable panel in the middle.

        parameter panel_height: height of the center panel
        precondition: panel_height is positive and <= self.height
        """
        veil = GRectangle(x=self.width / 2, y=self.height / 2,
                          width=self.width, height=self.height,
                          fillcolor=introcs.RGB(3, 10, 17, 160))
        self._screen_shapes.append(veil)
        self._add_card(self.width / 2, self.height / 2,
                       760, panel_height, False)

    # fill, border, and accent show which card should catch the eye.
    def _add_card(self, center_x, center_y, width, height, highlighted):
        """
        adds a dark card, a thin border, and a shadow a little below it.

        parameter center_x: horizontal center; must be a number
        parameter center_y: vertical center; must be a number
        parameter width: width of the card; must be positive
        parameter height: height of the card; must be positive
        parameter highlighted: whether the border uses the accent
        precondition: highlighted is a bool
        """
        shadow = GRectangle(x=center_x, y=center_y - 6, width=width + 8,
                            height=height + 6,
                            fillcolor=introcs.RGB(2, 9, 15, 65))
        border_color = UI_BORDER
        if highlighted:
            border_color = introcs.RGB(145, 231, 215, 140)
        card = GRectangle(x=center_x, y=center_y, width=width,
                          height=height, linewidth=1,
                          fillcolor=UI_SURFACE, linecolor=border_color)
        self._screen_shapes.append(shadow)
        self._screen_shapes.append(card)

    def _add_rule(self, y, left=72, width=1008):
        """
        adds a thin line to give the sections a little breathing room.

        parameter y: vertical position; must be a number
        parameter left: left edge; must be a number
        parameter width: line width; must be a positive number
        """
        divider = GRectangle(x=left + width / 2, y=y,
                             width=width, height=1, fillcolor=UI_BORDER)
        self._screen_shapes.append(divider)

    # a keycap is a label and box, so it never reads the keyboard itself.
    def _add_keycap(self, key, x, y, highlighted):
        """
        adds a small lowercase key badge at this center point.

        parameter key: key name; must be a nonempty string
        parameter x: horizontal center; must be a number
        parameter y: vertical center; must be a number
        parameter highlighted: whether this is a primary action
        precondition: highlighted is a bool
        """
        key_width = max(28, len(key) * 7 + 16)
        key_color = UI_TEXT
        if highlighted:
            key_color = UI_ACCENT
        key_shape = GRectangle(x=x, y=y, width=key_width, height=28,
                               linewidth=1, linecolor=UI_BORDER,
                               fillcolor=UI_SURFACE_SOFT)
        self._screen_shapes.append(key_shape)
        key_label = self._make_label(key, x, y, 14, key_color, THEME_FONT)
        self._screen_labels.append(key_label)

    # keep the key badge and explanation together when placing a control.
    def _add_key_hint(self, key, words, x, y, highlighted=False):
        """
        puts a short action description right beside the key badge.

        parameter key: key name; must be a nonempty string
        parameter words: action description; must be a string
        parameter x: center of the key; must be a number
        parameter y: vertical center; must be a number
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

    # this runs before state handling, so v works on every screen.
    def _read_audio_toggle(self):
        """flips sound on or off once per new v press, so holding v is fine."""
        if self.input.is_key_pressed('v'):
            self._sounds_enabled = not self._sounds_enabled
            if self._wave is not None:
                self._wave.setSoundsEnabled(self._sounds_enabled)
            if self._audio_label is not None:
                self._audio_label.text = self._get_audio_words()

    # no wave means no audio bank to stop, so leaving a menu is fine.
    def _stop_wave_audio(self):
        """stops any current cues, but leaves the mute choice alone."""
        if self._wave is not None:
            self._wave.stopSounds()

    # muted comes first; otherwise say if the loaded sounds are unavailable.
    def _get_audio_words(self):
        """returns the sound status, including when no audio could load."""
        if not self._sounds_enabled:
            return 'sound off   /   v to unmute'
        if self._wave is not None:
            if not self._wave.getSoundsAvailable():
                return 'audio unavailable   /   gameplay is still ready'
        return 'sound on   /   v to mute'

    # menus and panels reuse this sound label and keep it easy to find.
    def _make_audio_label(self, y):
        """
        puts the current sound setting in the footer.

        parameter y: vertical center; must be a number
        """
        self._audio_label = self._make_label(self._get_audio_words(),
                                            self.width / 2, y, 14, UI_MUTED)
        self._screen_labels.append(self._audio_label)

    def _add_center_label(self, words, y, size, color, font=BASIC_FONT):
        """
        adds one lowercase label in the middle of the screen.

        parameter words: text to display; must be a string
        parameter y: vertical center; must be a number
        parameter size: font size; must be positive
        parameter color: text color; must be a valid game2d color
        parameter font: font file; must name a supplied .ttf font
        """
        current_label = self._make_label(words, self.width / 2, y,
                                         size, color, font, 690)
        self._screen_labels.append(current_label)

    def _add_left_label(self, words, left, y, size, color,
                        font=BASIC_FONT, limit=500):
        """
        adds a lowercase label and lines it up with this left edge.

        parameter words: text to display; must be a string
        parameter left: left edge; must be a number
        parameter y: vertical center; must be a number
        parameter size: font size; must be positive
        parameter color: text color; must be a valid game2d color
        parameter font: font file; must name a supplied .ttf font
        parameter limit: maximum text width; must be positive
        """
        current_label = self._make_label(words, 0, y, size,
                                         color, font, limit)
        current_label.halign = 'left'
        current_label.left = left
        self._screen_labels.append(current_label)

    # long text gets a smaller font until it fits or reaches size one.
    def _make_label(self, words, x, y, size, color,
                    font=BASIC_FONT, limit=1008):
        """
        returns a lowercase GLabel, shrinking toward size 1 to fit limit.

        setting font_size refreshes the real text texture through the public
        GLabel property, so the width check measures the actual letters. use a
        fresh label when shrinking because the old rectangle only gets bigger.

        parameter words: text to display; must be a string
        parameter x: horizontal center; must be a number
        parameter y: vertical center; must be a number
        parameter size: wanted font size; must be positive
        parameter color: text color; must be a valid game2d color
        parameter font: font file; must name a supplied .ttf font
        parameter limit: maximum text width; must be positive
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
        return current_label


# omg this took so long 😭