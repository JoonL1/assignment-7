"""
The application controller for Missile Shield: Night Post.

This file handles the welcome screen, loading, pausing, and final messages.
Wave handles the game itself. The artwork and fonts come from the starter.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
"""
from consts import *
from game2d import *
from wave import Wave
import introcs

from kivy.logger import Logger


class MissileShield(GameApp):
    """
    The main controller for one complete wave of Missile Shield.

    This controller owns messages and changes between the six game states.
    It passes input and elapsed time to Wave only during active gameplay.
    It never reads Wave's hidden attributes or accesses the model classes.

    STATE_LOADING creates a new wave on its next update. STATE_CONTINUE
    clears the pause message on its next update without creating a wave.
    A loading failure uses STATE_COMPLETE, allowing R to retry or M to
    return home. The inherited view and input are GView and GInput objects.

    The title exists only in STATE_INACTIVE. The main message is None
    during STATE_ACTIVE. All added instance attributes are hidden.
    """
    # _state: one of the six STATE constants imported from consts.
    # _wave: a Wave, or None before loading or after a loading failure.
    # _background: a GImage covering the entire game window.
    # _sky_tint: a GRectangle giving the background a dark, readable tint.
    # _title: a GLabel in STATE_INACTIVE, and None in every other state.
    # _text: a GLabel message, or None; always None in STATE_ACTIVE.
    # _screen_labels: a list of GLabels for the current menu or message.
    # _screen_shapes: a list of GRectangles for menu and message decoration.
    # _selected_wave_file: a nonempty string naming the wave to load/retry.

    def start(self):
        """
        Initializes the application after the window is ready.

        This replaces an initializer for this GameApp subclass. It creates
        the background, initializes every hidden attribute, and opens the
        welcome screen. It does not create a Wave until the player starts.
        """
        self._state = STATE_INACTIVE
        self._wave = None
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []
        self._selected_wave_file = DEFAULT_WAVE
        self._background = GImage(source=BACKGROUND, width=self.width,
                                  height=self.height, x=self.width / 2,
                                  y=self.height / 2)
        nighttime_color = introcs.RGB(8, 19, 36, 158)
        self._sky_tint = GRectangle(x=self.width / 2, y=self.height / 2,
                                   width=self.width, height=self.height,
                                   fillcolor=nighttime_color)
        self._open_menu()

    def update(self, dt):
        """
        Updates the current application state for one animation frame.

        Inactive waits for S or C. Loading creates a fresh wave. Active
        runs Wave unless P pauses it. Paused waits for R or M. Continue
        removes the pause screen. Complete allows R to retry or M to exit.
        Each call handles only the state present at its beginning.

        Parameter dt: the real seconds since the previous update
        Precondition: dt is a nonnegative int or float
        """
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
        Draws the background, wave, and current application message.

        Wave draws all active game objects and its own HUD. Menu and pause
        panels are drawn afterward so their instructions stay readable.
        Drawing does not advance a timer or change the game state.
        """
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

    def _clear_messages(self):
        """
        Removes the old title, messages, and foreground decoration.

        The background and current Wave are left in place. This helper
        prepares the next screen without changing the application state.
        """
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []

    def _open_menu(self):
        """
        Returns to the welcome screen and discards the previous wave.

        S will load DEFAULT_WAVE, including a command-line override.
        C will load the separate nightpost.json demonstration wave.
        """
        self._clear_messages()
        self._wave = None
        self._state = STATE_INACTIVE
        self._selected_wave_file = DEFAULT_WAVE
        # ugh im so busy pls help 😭
        self._make_menu_decoration()
        self._make_menu_heading()
        self._make_standard_card()
        self._make_custom_card()
        self._make_menu_controls()

    def _update_menu(self):
        """
        Starts the selected wave with S or Night Post with C.

        Only a new key press starts a game. Holding a firing key while
        reading the menu does not dismiss it.
        """
        if self.input.is_key_pressed('s'):
            self._begin_loading(DEFAULT_WAVE)
        elif self.input.is_key_pressed('c'):
            self._begin_loading('nightpost.json')

    def _begin_loading(self, filename):
        """
        Prepares a fresh wave to be loaded on the next animation frame.

        Parameter filename: the wave file to start or retry
        Precondition: filename is a nonempty string
        """
        self._clear_messages()
        self._wave = None
        self._selected_wave_file = filename
        self._state = STATE_LOADING
        pale_color = introcs.RGB(231, 242, 242)
        self._text = self._make_label('Preparing the sky...',
                                     self.width / 2, self.height / 2,
                                     32, pale_color)

    def _load_wave(self):
        """
        Loads the selected JSON file and starts its Wave.

        The starter's load_json returns None for a missing or malformed
        file. This converts that result into a caught ValueError. Other
        loading errors are also logged and displayed without a crash.
        """
        try:
            wave_information = self.load_json(self._selected_wave_file)
            # im so tired bro 😴
            if wave_information is None:
                failure = 'Missing or malformed wave: '
                raise ValueError(failure + self._selected_wave_file)
            next_wave = Wave(wave_information)
            self._wave = next_wave
            self._clear_messages()
            self._state = STATE_ACTIVE
        except Exception as e:
            Logger.info(type(e).__name__ + ': ' + str(e))
            self._show_load_error()

    def _update_active(self, dt):
        """
        Pauses on P or lets Wave advance and checks its result.

        Losing is checked before winning. Wave decides both conditions;
        this controller only displays the appropriate completion screen.

        Parameter dt: the real seconds since the previous update
        Precondition: dt is nonnegative and _wave is a Wave
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
        """
        Freezes the wave and displays its controls in a readable panel.

        Custom controls are shown only for a wave with extra features.
        No Wave update occurs while this pause screen is displayed.
        """
        self._clear_messages()
        self._state = STATE_PAUSED
        self._make_panel(550)
        self._add_center_label('DISPATCH ON HOLD', 636, 34,
                               introcs.RGB(123, 231, 230), THEME_FONT)
        self._text = self._make_label('Press R to resume',
                                     self.width / 2, 576, 32, 'white')
        mode_name = self._wave.getModeName()
        self._add_center_label(mode_name, 684, 14,
                               introcs.RGB(254, 193, 123))
        self._add_center_label('ARROWS  aim    1 / 2 / 3  fire',
                               516, 20, 'white')
        if self._wave.getCustomEnabled():
            self._make_custom_help()
        else:
            self._make_standard_help()
        self._add_center_label('M  return to the menu', 220, 19,
                               introcs.RGB(123, 231, 230))

    def _update_paused(self):
        """
        Waits for R to resume the existing wave or M to leave it.

        Resuming first enters STATE_CONTINUE. It does not load another
        wave and does not advance the existing wave on this frame.
        """
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _continue_wave(self):
        """
        Clears the pause message and makes the existing wave active.

        This is the one-frame STATE_CONTINUE transition. Gameplay starts
        advancing again on the following call to update.
        """
        self._clear_messages()
        self._state = STATE_ACTIVE

    def _finish_wave(self, player_won):
        """
        Stops gameplay and displays the win or loss message.

        Parameter player_won: whether the wave was successfully cleared
        Precondition: player_won is a bool and _wave is a Wave
        """
        self._clear_messages()
        self._state = STATE_COMPLETE
        self._make_panel(410)
        if player_won:
            self._make_win_message()
        else:
            self._make_loss_message()
        mode_name = self._wave.getModeName()
        self._add_center_label(mode_name, 607, 14,
                               introcs.RGB(254, 193, 123))
        replay_text = 'R  play this wave again       M  return to menu'
        self._add_center_label(replay_text, 285, 20,
                               introcs.RGB(123, 231, 230))

    def _update_complete(self):
        """
        Restarts the selected file with R or returns to the menu with M.

        The same keys also work after a loading failure. A restart creates
        a new Wave, with fresh cities, ammunition, and feature resources.
        """
        if self.input.is_key_pressed('r'):
            self._begin_loading(self._selected_wave_file)
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _show_load_error(self):
        """
        Shows a recoverable loading failure with the selected filename.

        The technical exception is already in the Kivy log. The visible
        message tells the player how to retry or choose another wave.
        """
        self._clear_messages()
        self._wave = None
        self._state = STATE_COMPLETE
        self._make_panel(410)
        self._add_center_label('DELIVERY FAILED', 563, 36,
                               introcs.RGB(254, 193, 123), THEME_FONT)
        self._text = self._make_label('This wave could not be loaded.',
                                     self.width / 2, 493, 28, 'white')
        self._add_center_label(self._selected_wave_file, 442, 22,
                               introcs.RGB(123, 231, 230))
        detail = 'Check the JSON file and the terminal error message.'
        self._add_center_label(detail, 387, 18,
                               introcs.RGB(191, 207, 216))
        self._add_center_label('R  retry       M  return to menu',
                               300, 20, 'white')

    def _make_menu_decoration(self):
        """
        Adds the postal border, quiet stars, and two menu card backgrounds.

        These are cosmetic shapes only. They never appear in Wave's lists
        and cannot interact with bombs, rockets, cities, or ammunition.
        """
        stripe_colors = [introcs.RGB(123, 231, 230, 210),
                         introcs.RGB(254, 193, 123, 210)]
        for stripe_number in range(24):
            stripe_x = 60 + stripe_number * 44
            color_position = stripe_number % 2
            stripe = GRectangle(x=stripe_x, y=791, width=24, height=3,
                                fillcolor=stripe_colors[color_position])
            self._screen_shapes.append(stripe)
        self._add_menu_stars()
        self._add_card(309, 352, 498, 224, False)
        self._add_card(843, 352, 498, 224, True)
        self._add_rule(202)
        self._add_center_label('CIVIL DEFENSE / AFTER HOURS EDITION',
                               818, 14, introcs.RGB(221, 232, 236))

    def _add_menu_stars(self):
        """
        Places a fixed set of small decorative stars around the menu.

        The positions are deliberately fixed so the menu is stable and
        does not require a random module or another animation timer.
        """
        star_positions = [[93, 708], [174, 563], [1040, 706], [992, 565],
                          [66, 505], [1086, 512], [196, 746], [937, 750]]
        for current_position in star_positions:
            star_x = current_position[0]
            star_y = current_position[1]
            star_color = introcs.RGB(208, 235, 238, 155)
            current_star = GEllipse(x=star_x, y=star_y, width=3, height=3,
                                   fillcolor=star_color)
            self._screen_shapes.append(current_star)

    def _make_menu_heading(self):
        """
        Creates the title and the short premise above the two start cards.

        Magnetar is reserved for the title. The smaller instructions use
        the more readable Roboto font supplied with the assignment.
        """
        cyan_color = introcs.RGB(123, 231, 230)
        self._add_center_label('N I G H T   P O S T', 746, 22, cyan_color)
        self._title = self._make_label('MISSILE SHIELD', self.width / 2,
                                      661, 76, 'white', THEME_FONT)
        self._add_center_label('KEEP THE CITY LIGHTS ON.', 573, 28,
                               introcs.RGB(254, 193, 123))
        subtitle = 'One sky. Six cities. Every interception matters.'
        self._add_center_label(subtitle, 532, 18,
                               introcs.RGB(221, 232, 236))

    def _make_standard_card(self):
        """
        Labels the selected-file option and its command-line wave choice.

        A long filename is reduced to a smaller font so it stays inside
        the card. The selected filename itself is never changed.
        """
        self._add_card_label('S   SELECTED WAVE', 309, 420, 25, 'white')
        self._add_card_label('START THE SELECTED WAVE', 309, 381, 13,
                             introcs.RGB(254, 193, 123))
        filename_text = 'File: ' + DEFAULT_WAVE
        self._add_card_label(filename_text, 309, 346, 19,
                             introcs.RGB(213, 228, 233))
        self._add_card_label('Starts your default or command-line wave.',
                             309, 303, 19, 'white')
        self._add_card_label('Keep at least one city standing to finish.',
                             309, 272, 16, introcs.RGB(179, 201, 211))

    def _make_custom_card(self):
        """
        Labels the optional custom wave and its four extra tools.

        Each row gives a control or a clear automatic effect. These tools
        belong only to a custom wave; S still uses the chosen base file.
        """
        cyan_color = introcs.RGB(123, 231, 230)
        self._add_card_label('C   NIGHT POST', 843, 420, 25, cyan_color)
        self._add_card_label('CUSTOM WAVE / FOUR EXTRA TOOLS',
                             843, 381, 13, introcs.RGB(254, 193, 123))
        self._add_card_label('F  forecast 1.5 seconds ahead',
                             843, 350, 17, 'white')
        self._add_card_label('B / TAB / X  save, recall, clear aim',
                             843, 323, 17, 'white')
        self._add_card_label('SPACE  hold a limited slow-time bubble',
                             843, 296, 17, 'white')
        self._add_card_label('Every 3 interceptions recycle 1 rocket',
                             843, 269, 17, 'white')

    def _make_menu_controls(self):
        """
        Displays shared controls and the two start choices below the cards.
        """
        controls = 'ARROWS  aim       1 / 2 / 3  fire       P  pause'
        self._add_center_label(controls, 174, 19, 'white')
        self._text = self._make_label('Press S to start  /  C for Night Post',
                                     self.width / 2, 122, 23,
                                     introcs.RGB(123, 231, 230))
        self._add_center_label('R  resumes a pause or restarts a finished wave',
                               79, 17, introcs.RGB(213, 228, 233))
        self._add_center_label('Clear the sky. Keep at least one city alive.',
                               45, 15, introcs.RGB(179, 201, 211))

    def _make_custom_help(self):
        """
        Explains the four optional tools while a custom wave is paused.

        All tool behavior is implemented in Wave. These are instructions
        only; displaying them does not consume or refill a resource.
        """
        pale_color = introcs.RGB(221, 232, 236)
        self._add_center_label('F  toggle 1.5-second forecast ghosts',
                               461, 20, pale_color)
        self._add_center_label('B  bookmark aim    TAB  recall    X  clear',
                               420, 20, pale_color)
        self._add_center_label('SPACE  hold a slow-time bubble at your aim',
                               379, 20, pale_color)
        meter_help = 'Release SPACE to recharge. Only nearby bombs slow down.'
        self._add_center_label(meter_help,
                               350, 16, introcs.RGB(254, 193, 123))
        recycle_help = 'Every 3 interceptions: 1 rocket to a low silo'
        self._add_center_label(recycle_help,
                               307, 19, pale_color)
        self._add_center_label('Your interceptions leave a constellation.',
                               277, 16, introcs.RGB(123, 231, 230))

    def _make_standard_help(self):
        """
        Shows a short explanation of the normal game's goal and controls.
        """
        pale_color = introcs.RGB(221, 232, 236)
        self._add_center_label('Fire from the left, middle, or right silo.',
                               450, 21, pale_color)
        self._add_center_label('Rockets explode when they reach your aim.',
                               408, 20, pale_color)
        self._add_center_label('Catch falling bombs inside the growing blast.',
                               366, 20, pale_color)
        self._add_center_label('Keep at least one city standing to finish.',
                               324, 20, introcs.RGB(254, 193, 123))
        # ugh im so tired 😴

    def _make_win_message(self):
        """
        Displays a successful wave's final city and ammunition score.

        The score is read from Wave rather than recalculated here. The
        already-finished wave remains visible behind the completion panel.
        """
        self._add_center_label('DELIVERED', 550, 43,
                               introcs.RGB(123, 231, 230), THEME_FONT)
        score_number = self._wave.getScore()
        score_words = 'SCORE: ' + str(score_number)
        self._text = self._make_label(score_words, self.width / 2,
                                     463, 57, 'white', THEME_FONT)
        success_text = 'The sky is clear. The city lights are still on.'
        self._add_center_label(success_text,
                               389, 21, introcs.RGB(254, 193, 123))
        self._add_center_label('Surviving cities + remaining silo ammunition',
                               351, 17, introcs.RGB(191, 207, 216))

    def _make_loss_message(self):
        """
        Displays the immediate loss when no cities remain.

        It does not wait for the remaining rockets or bombs to finish.
        """
        self._add_center_label('LIGHTS OUT', 550, 43,
                               introcs.RGB(254, 193, 123), THEME_FONT)
        self._text = self._make_label('All six cities were destroyed.',
                                     self.width / 2, 463, 30, 'white')
        self._add_center_label('The night shift ends here.', 393, 23,
                               introcs.RGB(221, 232, 236))
        self._add_center_label('Take a breath. There is another sky to save.',
                               351, 18, introcs.RGB(191, 207, 216))

    def _make_panel(self, panel_height):
        """
        Adds a dark veil and a centered message panel over the current game.

        Parameter panel_height: the height of the readable center panel
        Precondition: panel_height is a positive number <= self.height
        """
        veil_color = introcs.RGB(5, 12, 24, 115)
        veil = GRectangle(x=self.width / 2, y=self.height / 2,
                          width=self.width, height=self.height,
                          fillcolor=veil_color)
        self._screen_shapes.append(veil)
        self._add_card(self.width / 2, self.height / 2,
                       self.width - 240, panel_height, True)

    def _add_card(self, center_x, center_y, width, height, highlighted):
        """
        Adds a dark rectangular card and a narrow colored top border.

        Parameter center_x: the card's horizontal center
        Parameter center_y: the card's vertical center
        Parameter width: the card width
        Parameter height: the card height
        Precondition: centers are numbers; width and height are positive

        Parameter highlighted: whether the border uses the cyan accent
        Precondition: highlighted is a bool
        """
        background_color = introcs.RGB(9, 23, 40, 239)
        if highlighted:
            border_color = introcs.RGB(123, 231, 230)
        else:
            border_color = introcs.RGB(254, 193, 123)
        card = GRectangle(x=center_x, y=center_y, width=width,
                          height=height, fillcolor=background_color)
        self._screen_shapes.append(card)
        border_y = center_y + height / 2
        border = GRectangle(x=center_x, y=border_y, width=width,
                            height=3, fillcolor=border_color)
        self._screen_shapes.append(border)

    def _add_rule(self, vertical_position):
        """
        Adds a thin horizontal divider to the menu.

        Parameter vertical_position: the divider's height on the screen
        Precondition: vertical_position is between 0 and self.height
        """
        divider_color = introcs.RGB(166, 201, 212, 100)
        divider = GRectangle(x=self.width / 2, y=vertical_position,
                             width=self.width - 120, height=1,
                             fillcolor=divider_color)
        self._screen_shapes.append(divider)

    def _add_center_label(self, words, y, size, color, font=BASIC_FONT):
        """
        Adds one centered label to the current screen's text list.

        Parameter words: the text to display; must be a string
        Parameter y: the vertical center; must be a number
        Parameter size: the desired font size; must be a positive number
        Parameter color: the text color; must be a valid game2d color
        Parameter font: the font file; must name a supplied .ttf font
        """
        current_label = self._make_label(words, self.width / 2, y,
                                         size, color, font)
        self._screen_labels.append(current_label)

    def _add_card_label(self, words, x, y, size, color):
        """
        Adds a label that fits inside a 498-pixel menu card.

        Parameter words: the displayed text; must be a string
        Parameter x: the horizontal center; must be a number
        Parameter y: the vertical center; must be a number
        Parameter size: the desired font size; must be a positive number
        Parameter color: the text color; must be a valid game2d color
        """
        current_label = self._make_label(words, x, y, size, color,
                                         BASIC_FONT, 450)
        self._screen_labels.append(current_label)

    def _make_label(self, words, x, y, size, color,
                    font=BASIC_FONT, limit=None):
        """
        Returns a label, reducing its font if a long line would not fit.

        A fresh label is made after each reduction because GLabel expands
        its rectangle for text but does not automatically shrink it.

        Parameter words: the displayed text; must be a string
        Parameter x: the horizontal center; must be a number
        Parameter y: the vertical center; must be a number
        Parameter size: the desired font size; must be a positive number
        Parameter color: the text color; must be a valid game2d color
        Parameter font: the font file; must name a supplied .ttf font
        Parameter limit: the maximum width, or None for the screen width
        Precondition: limit is None or a positive number
        """
        if limit is None:
            available_width = self.width - 120
        else:
            available_width = limit
        chosen_size = size
        current_label = GLabel(text=words, x=x, y=y, font_size=chosen_size,
                               font_name=font, linecolor=color)
        # make a new label because the old rectangle only grows 😭
        while current_label.width > available_width and chosen_size > 1:
            chosen_size = chosen_size - 1
            current_label = GLabel(text=words, x=x, y=y,
                                   font_size=chosen_size, font_name=font,
                                   linecolor=color)
        return current_label


# omg this took so long 😭