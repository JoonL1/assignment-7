"""
the screens and main controller for missile shield: night post.

this file handles menus, loading, pausing, sound preferences, and results.
Wave handles the actual game, so the screens only use public wave methods.
the pictures, fonts, and sounds all came with the assignment package.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026
"""
from consts import *
from game2d import *
from wave import Wave
import introcs
from kivy.logger import Logger


class MissileShield(GameApp):
    """
    handles the screens and the six states of one complete game.

    loading creates a wave on the next frame. similarly, continue removes
    the pause panel on the next frame, but keeps the same wave. a loading
    error uses complete, so r can retry and m can open the menu.

    all added attributes are hidden. the inherited view and input are the
    GView and GInput from GameApp, and title is the inherited window title.
    the app only calls public methods of Wave because the game objects
    belong to that controller. drawing never changes a gameplay timer.
    """
    # _state: one of the six STATE constants from consts.
    # _wave: a Wave, or None before loading or after a loading failure.
    # _background: a GImage covering the entire window.
    # _sky_tint: a GRectangle that makes the sunset quieter and darker.
    # _title: a GLabel in STATE_INACTIVE, and None in other states.
    # _text: a GLabel message, or None; always None in STATE_ACTIVE.
    # _screen_labels: a list of GLabels for the current menu or panel.
    # _screen_shapes: decorative GRectangles, GEllipses, or GPaths.
    # _selected_wave_file: a nonempty filename kept with its original case.
    # _sounds_enabled: a bool that keeps the mute choice across new waves.
    # _audio_label: a GLabel in a menu or panel, or None during gameplay.

    def start(self):
        """sets up the window, background, sound preference, and menu."""
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
        reads mute once, then handles the state at the start of this frame.

        only the active state advances Wave. loading and continue each use
        one frame, so neither accidentally advances the next state too.

        parameter dt: real seconds since the previous update
        precondition: dt is a finite nonnegative int or float
        """
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
        """draws the sky, game, and current screen in that order."""
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

    def on_stop(self):
        """stops any remaining wave sounds when the game window closes."""
        if hasattr(self, '_wave'):
            self._stop_wave_audio()

    def _clear_messages(self):
        """clears old screen graphics, while keeping the sky and wave."""
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._audio_label = None

    def _open_menu(self):
        """opens the welcome screen and lets go of the previous wave."""
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

    def _update_menu(self):
        """starts the selected file with s or the night post wave with c."""
        if self.input.is_key_pressed('s'):
            self._begin_loading(DEFAULT_WAVE)
        elif self.input.is_key_pressed('c'):
            self._begin_loading('nightpost.json')

    def _begin_loading(self, filename):
        """
        prepares to load a fresh wave on the following frame.

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

    def _load_wave(self):
        """
        reads the file, makes a wave, and starts its sound after success.

        failures say which step failed and show the actual exception. the
        screen is lowercase, but the terminal keeps the original case and
        full traceback so paths and exception names can still be checked.
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

    def _read_wave_file(self):
        """
        returns the selected data, or raises a clear loading error.

        is_json uses the Data folder of this app. a missing file raises
        FileNotFoundError, while unreadable json raises ValueError. valid
        json with the wrong structure goes to Wave for a separate check.
        filenames keep their original case because case matters for paths.
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
        pauses on p, or advances the wave and checks loss before victory.

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

    def _pause_wave(self):
        """freezes gameplay and sound, then shows the controls for this mode."""
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

    def _update_paused(self):
        """waits for r to resume the same wave or m to leave it."""
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _continue_wave(self):
        """clears the pause panel without changing the wave or its resources."""
        self._clear_messages()
        self._state = STATE_ACTIVE

    def _finish_wave(self, player_won):
        """
        shows the result and plays its single completion cue.

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

    def _update_complete(self):
        """restarts the selected file with r or opens the menu with m."""
        if self.input.is_key_pressed('r'):
            self._begin_loading(self._selected_wave_file)
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _show_load_error(self, loading_step, error_details, next_step):
        """
        shows a readable error with a filename, details, and retry controls.

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

    def _add_error_details(self, error_details):
        """
        wraps an error into at most three lowercase lines of 48 characters.

        the log keeps the original full message, so a long path does not
        push the controls offscreen. words stay together when possible.

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
        """adds a quiet header, two mode cards, and a decorative sky map."""
        self._add_left_label('night post', 72, 811, 20, UI_TEXT, THEME_FONT)
        self._add_left_label('missile shield / after hours',
                             830, 811, 14, UI_MUTED)
        self._add_rule(778)
        self._add_card(315, 294, 486, 192, False)
        self._add_card(837, 294, 486, 192, True)
        self._make_sky_map()
        self._add_rule(166)

    def _make_sky_map(self):
        """makes the menu illustration from rings, paths, and small stars."""
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
        """adds the small aiming mark and caption of the menu illustration."""
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

    def _make_menu_heading(self):
        """sets the lowercase title and a short goal above the mode cards."""
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
        """labels the card that starts the exact command-line wave choice."""
        self._add_keycap('s', 104, 348, False)
        self._add_left_label('selected wave', 134, 348, 23,
                             UI_TEXT, THEME_FONT)
        self._add_left_label('start the wave chosen for this session.',
                             96, 307, 17, UI_MUTED)
        self._add_left_label('selected / ' + DEFAULT_WAVE,
                             96, 275, 15, UI_MUTED, limit=430)
        self._add_left_label('press s to start', 96, 233, 17, UI_TEXT)

    def _make_custom_card(self):
        """introduces the optional tools without a wall of instructions."""
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
        """shows the shared keys and explains where the full help lives."""
        self._text = self._make_label('choose a wave. make every shot count.',
                                     self.width / 2, 136, 18, UI_MUTED)
        self._add_key_hint('arrows', 'aim', 299, 92)
        self._add_key_hint('1 / 2 / 3', 'fire', 507, 92)
        self._add_key_hint('p', 'pause + help', 720, 92)
        self._make_audio_label(41)

    def _make_custom_help(self):
        """shows only the controls enabled by the current custom wave."""
        help_rows = self._wave.getHelpRows()
        for row_number in range(len(help_rows)):
            row_text = help_rows[row_number]
            row_y = 465 - row_number * 42
            self._add_center_label(row_text, row_y, 17, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               284, 15, UI_ACCENT)

    def _make_standard_help(self):
        """explains the standard goal in a few short readable lines."""
        self._add_center_label('fire from the left, center, or right silo.',
                               455, 19, UI_MUTED)
        self._add_center_label('rockets burst at the point where you aimed.',
                               414, 19, UI_MUTED)
        self._add_center_label('catch falling bombs inside the growing blast.',
                               373, 19, UI_MUTED)
        self._add_center_label('keep at least one city standing.',
                               308, 19, UI_ACCENT)
        # ugh im so tired but the spacing finally makes sense 😭

    def _make_win_message(self):
        """shows the final score and the remaining cities and ammunition."""
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

    def _make_loss_message(self):
        """shows the loss immediately after the last city disappears."""
        self._add_center_label('lights out.', 587, 44,
                               UI_DANGER, THEME_FONT)
        self._text = self._make_label('all six cities were lost.',
                                     self.width / 2, 515, 27, UI_TEXT)
        self._add_center_label('the night shift ends here.',
                               457, 20, UI_MUTED)
        self._add_center_label('there is another sky to save.',
                               412, 18, UI_MUTED)

    def _make_panel(self, panel_height):
        """
        puts a centered readable panel over a dimmed version of the game.

        parameter panel_height: height of the center panel
        precondition: panel_height is positive and <= self.height
        """
        veil = GRectangle(x=self.width / 2, y=self.height / 2,
                          width=self.width, height=self.height,
                          fillcolor=introcs.RGB(3, 10, 17, 160))
        self._screen_shapes.append(veil)
        self._add_card(self.width / 2, self.height / 2,
                       760, panel_height, False)

    def _add_card(self, center_x, center_y, width, height, highlighted):
        """
        adds a dark card with a thin border and a soft offset shadow.

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
        adds a quiet horizontal divider.

        parameter y: vertical position; must be a number
        parameter left: left edge; must be a number
        parameter width: line width; must be a positive number
        """
        divider = GRectangle(x=left + width / 2, y=y,
                             width=width, height=1, fillcolor=UI_BORDER)
        self._screen_shapes.append(divider)

    def _add_keycap(self, key, x, y, highlighted):
        """
        draws a small lowercase keyboard key at the given center.

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

    def _add_key_hint(self, key, words, x, y, highlighted=False):
        """
        puts an action label to the right of a keyboard key.

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

    def _read_audio_toggle(self):
        """changes the sound preference once for each new press of v."""
        if self.input.is_key_pressed('v'):
            self._sounds_enabled = not self._sounds_enabled
            if self._wave is not None:
                self._wave.setSoundsEnabled(self._sounds_enabled)
            if self._audio_label is not None:
                self._audio_label.text = self._get_audio_words()

    def _stop_wave_audio(self):
        """stops existing sound cues without changing the mute preference."""
        if self._wave is not None:
            self._wave.stopSounds()

    def _get_audio_words(self):
        """returns a short honest description of the current audio setting."""
        if not self._sounds_enabled:
            return 'sound off   /   v to unmute'
        if self._wave is not None:
            if not self._wave.getSoundsAvailable():
                return 'audio unavailable   /   gameplay is still ready'
        return 'sound on   /   v to mute'

    def _make_audio_label(self, y):
        """
        adds the sound setting to the footer of the current screen.

        parameter y: vertical center; must be a number
        """
        self._audio_label = self._make_label(self._get_audio_words(),
                                            self.width / 2, y, 14, UI_MUTED)
        self._screen_labels.append(self._audio_label)

    def _add_center_label(self, words, y, size, color, font=BASIC_FONT):
        """
        adds one centered lowercase label to the current screen.

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
        adds a lowercase label anchored to a fixed left edge.

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

    def _make_label(self, words, x, y, size, color,
                    font=BASIC_FONT, limit=1008):
        """
        returns lowercase text that fits inside the requested width.

        setting font_size also refreshes the actual texture through the
        public GLabel property, so this measures the real letters. a new
        label is used when shrinking because the old rectangle only grows.

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