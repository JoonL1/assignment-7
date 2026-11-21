"""
the main controller for missile shield: night post.

this file handles the menu, loading, pausing, and the final messages, so
Wave can handle the actual game. the art and fonts came with the starter.

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

    this controller sends input and elapsed time to Wave while the game is
    active. it only uses public methods of Wave, because the hidden wave
    attributes and the model objects belong to the other files.

    STATE_LOADING makes a fresh wave on the next update. similarly,
    STATE_CONTINUE clears the pause screen on the next update, but keeps
    the existing wave. a loading error uses STATE_COMPLETE, so r can retry
    and m can return to the menu. the inherited view and input are GView
    and GInput objects.

    the title is only present in STATE_INACTIVE. the main message is None
    in STATE_ACTIVE, and every added instance attribute is hidden.
    """
    # _state: one of the six STATE constants imported from consts.
    # _wave: a Wave, or None before loading or after a loading failure.
    # _background: a GImage covering the entire game window.
    # _sky_tint: a GRectangle giving the background a dark, readable tint.
    # _title: a GLabel in STATE_INACTIVE, and None in every other state.
    # _text: a GLabel message, or None; always None in STATE_ACTIVE.
    # _screen_labels: GLabels for the current menu or message.
    # _screen_shapes: GRectangles that decorate the menu or message.
    # _selected_wave_file: a nonempty string naming the wave to load/retry.

    def start(self):
        """
        sets up the app once the window is ready.

        this takes the place of an initializer for this GameApp subclass, so
        it creates the background, gives every hidden attribute a starting
        value, and opens the menu. the wave waits until the player starts.
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
        handles one frame using the state at the start of this call.

        inactive waits for s or c, and loading makes a fresh wave. active
        updates Wave unless p pauses it, while paused waits for r or m.
        continue clears the pause screen, and complete waits for a retry
        or a return to the menu. only one of these branches runs each frame.

        parameter dt: real seconds since the previous update
        precondition: dt is a nonnegative int or float
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
        draws the background, then the wave, then the current screen text.

        Wave draws the game objects and the heads-up display. the menu and
        pause panels go on top, because the controls still need to be easy
        to read. drawing does not move a timer or change the game state.
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
        clears the title, messages, and shapes from the previous screen.

        the background and current Wave stay in place, so this helper can
        prepare a new screen without changing the application state.
        """
        self._title = None
        self._text = None
        self._screen_labels = []
        self._screen_shapes = []

    def _open_menu(self):
        """
        opens the welcome screen and lets go of the previous wave.

        s uses DEFAULT_WAVE, including a filename from the command line.
        c uses nightpost.json, so the custom wave has a separate start key.
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
        starts the selected file with s or the night post wave with c.

        the key has to be newly pressed, so holding a firing key while
        reading the menu does not accidentally start the game.
        """
        if self.input.is_key_pressed('s'):
            self._begin_loading(DEFAULT_WAVE)
        elif self.input.is_key_pressed('c'):
            self._begin_loading('nightpost.json')

    def _begin_loading(self, filename):
        """
        gets the screen ready to load a fresh wave on the next frame.

        parameter filename: the wave file to start or retry
        precondition: filename is a nonempty string
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
        loads the selected json file and makes its Wave.

        the screen says which step failed and shows the actual exception,
        because a setup error does not always mean the json file is bad.
        the full traceback also goes to the kivy log. a failure leaves
        _wave as None and lets r retry or m return to the menu.
        """
        loading_step = 'Could not read the wave file.'
        next_step = 'Check the selected file inside the Data folder.'
        try:
            wave_information = self._read_wave_file()
            loading_step = 'Could not create the wave.'
            next_step = 'Check the wave values and use '
            next_step = next_step + 'one complete shield folder.'
            next_wave = Wave(wave_information)
            self._wave = next_wave
            self._clear_messages()
            self._state = STATE_ACTIVE
        except Exception as e:
            error_details = type(e).__name__ + ': ' + str(e)
            Logger.exception('MissileShield: ' + error_details)
            self._show_load_error(loading_step, error_details, next_step)

    def _read_wave_file(self):
        """
        returns the selected wave data, or raises a clear loading error.

        is_json checks the Data folder of this app, so launching from a
        different folder does not change where the game looks. a missing
        file raises FileNotFoundError. load_json returns None for bad json,
        so that result raises ValueError instead. valid json with the wrong
        wave structure goes to Wave, which checks the contents separately.
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
        pauses on p, or advances the wave and checks how it ended.

        loss comes before victory because the last city might disappear on
        this frame. Wave decides both results, so this controller only picks
        the matching completion screen.

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
        """
        freezes the wave and puts the controls on a readable pause panel.

        the extra controls only appear for a custom wave. Wave does not
        update while paused, so its bombs and resource meters stay put.
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
        waits for r to resume the same wave or m to leave it.

        r first enters STATE_CONTINUE, so this frame does not advance the
        wave or load a replacement for it.
        """
        if self.input.is_key_pressed('r'):
            self._state = STATE_CONTINUE
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _continue_wave(self):
        """
        clears the pause message and makes the existing wave active again.

        this is the one-frame STATE_CONTINUE step, so the wave starts moving
        again on the following call to update.
        """
        self._clear_messages()
        self._state = STATE_ACTIVE

    def _finish_wave(self, player_won):
        """
        stops gameplay and puts up the matching win or loss message.

        parameter player_won: whether the player cleared the wave
        precondition: player_won is a bool and _wave is a Wave
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
        restarts the selected file with r or returns to the menu with m.

        these keys also work after a loading error. restarting makes a new
        Wave, so the cities, ammo, and extra resources all start fresh.
        """
        if self.input.is_key_pressed('r'):
            self._begin_loading(self._selected_wave_file)
        elif self.input.is_key_pressed('m'):
            self._open_menu()

    def _show_load_error(self, loading_step, error_details, next_step):
        """
        shows the failed step, filename, exception, and retry controls.

        long errors get three wrapped lines, while the log keeps the full
        traceback. this clears any unfinished Wave and uses STATE_COMPLETE,
        so r and m still work after either a file error or a setup error.

        parameter loading_step: a short description of what failed
        parameter error_details: the exception type and its message
        parameter next_step: a short suggestion for fixing the problem
        precondition: all three parameters are nonempty strings
        """
        self._clear_messages()
        self._wave = None
        self._state = STATE_COMPLETE
        self._make_panel(530)
        self._add_center_label('DELIVERY FAILED', 638, 36,
                               introcs.RGB(254, 193, 123), THEME_FONT)
        self._text = self._make_label(loading_step,
                                     self.width / 2, 579, 27, 'white')
        self._add_center_label(self._selected_wave_file, 535, 22,
                               introcs.RGB(123, 231, 230))
        self._add_error_details(error_details)
        self._add_center_label(next_step, 350, 18,
                               introcs.RGB(191, 207, 216))
        log_hint = 'The terminal log has the full error and its location.'
        self._add_center_label(log_hint, 317, 16,
                               introcs.RGB(191, 207, 216))
        self._add_center_label('R  retry       M  return to menu',
                               236, 20, 'white')

    def _add_error_details(self, error_details):
        """
        adds up to three lines of the actual loading error to the panel.

        each line has at most 48 characters before the final ellipsis.
        words stay together when possible, but a long path can split too.
        extra text stays in the log, so the retry controls remain visible.

        parameter error_details: the exception type and its message
        precondition: error_details is a nonempty string
        """
        remaining_text = error_details.replace('\n', ' ').strip()
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
            line_height = 476 - 29 * line_number
            self._add_center_label(current_line, line_height, 19,
                                   introcs.RGB(254, 193, 123))

    def _make_menu_decoration(self):
        """
        adds the postal border, small stars, and two menu card backgrounds.

        these are just decorations. they stay out of the lists of Wave, so
        they cannot change bombs, rockets, cities, or ammo.
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
        puts a fixed set of little stars around the menu.

        the positions stay the same, because a quiet menu does not need
        random numbers or another timer just to place a few stars.
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
        puts the title and short game description above the start cards.

        the title uses magnetar, but the smaller instructions use roboto
        because it is easier to read. both fonts came with the assignment.
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
        labels the selected-file card with the command-line wave choice.

        a long filename gets a smaller font so it fits in the card. this
        only changes the display, so the actual filename stays the same.
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
        labels the custom wave card and explains its four extra tools.

        each row gives a key or an automatic effect. these tools belong to
        custom waves, but s still starts whichever file was selected.
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
        puts the shared controls and both start choices below the cards.
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
        explains the four optional tools while a custom wave is paused.

        Wave handles what the tools do, so showing this help does not spend
        or refill any resource.
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
        shows the normal goal and controls in a few short lines.
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
        shows the final score from living cities and leftover ammo.

        the score comes from Wave, so this file does not calculate it again.
        the finished wave stays visible behind the completion panel.
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
        shows the loss as soon as no cities remain.

        remaining rockets and bombs do not delay this screen, because the
        player has already lost when the last city disappears.
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
        adds a dark veil and a centered message panel over the game.

        parameter panel_height: height of the readable center panel
        precondition: panel_height is a positive number <= self.height
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
        adds a dark rectangular card with a thin colored border on top.

        parameter center_x: horizontal center of the card
        parameter center_y: vertical center of the card
        parameter width: width of the card
        parameter height: height of the card
        precondition: centers are numbers; width and height are positive

        parameter highlighted: whether the top border uses the cyan accent
        precondition: highlighted is a bool
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
        adds a thin horizontal divider to the menu.

        parameter vertical_position: height of the divider on the screen
        precondition: vertical_position is between 0 and self.height
        """
        divider_color = introcs.RGB(166, 201, 212, 100)
        divider = GRectangle(x=self.width / 2, y=vertical_position,
                             width=self.width - 120, height=1,
                             fillcolor=divider_color)
        self._screen_shapes.append(divider)

    def _add_center_label(self, words, y, size, color, font=BASIC_FONT):
        """
        adds one centered label to the text list of the current screen.

        parameter words: text to display; must be a string
        parameter y: vertical center; must be a number
        parameter size: wanted font size; must be a positive number
        parameter color: text color; must be a valid game2d color
        parameter font: font file; must name a supplied .ttf font
        """
        current_label = self._make_label(words, self.width / 2, y,
                                         size, color, font)
        self._screen_labels.append(current_label)

    def _add_card_label(self, words, x, y, size, color):
        """
        adds a label that fits inside a menu card with a width of 498 pixels.

        parameter words: text to display; must be a string
        parameter x: horizontal center; must be a number
        parameter y: vertical center; must be a number
        parameter size: wanted font size; must be a positive number
        parameter color: text color; must be a valid game2d color
        """
        current_label = self._make_label(words, x, y, size, color,
                                         BASIC_FONT, 450)
        self._screen_labels.append(current_label)

    def _make_label(self, words, x, y, size, color,
                    font=BASIC_FONT, limit=None):
        """
        returns a label with a smaller font if the line is too wide.

        each size change makes a fresh label, because GLabel expands its
        rectangle for text but does not shrink that rectangle automatically.

        parameter words: text to display; must be a string
        parameter x: horizontal center; must be a number
        parameter y: vertical center; must be a number
        parameter size: wanted font size; must be a positive number
        parameter color: text color; must be a valid game2d color
        parameter font: font file; must name a supplied .ttf font
        parameter limit: maximum width, or None to use the screen width
        precondition: limit is None or a positive number
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