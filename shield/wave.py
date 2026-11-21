"""
Subcontroller module for Missile Shield

This module contains the subcontroller to manage a single wave in the Missile 
Shield game. Instances of Wave represent a single game, read from a JSON. 
Whenever you load a new wave, you are expected to make a new instance of this 
class.

The subcontroller Wave manages the silos, cities and all of the incoming
missiles. However, those classes are all defined in models.py. In general, this 
module should not contain any classes other than Wave. If you need a new 
class, it should go in the the models.py module.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026
"""
from game2d import GRectangle, GEllipse, GPath, GLabel
from consts import *
from models import Silo, City, Target, Bomb, Rocket, SoundEffects


# PRIMARY RULE: Wave can only access attributes in models.py using getters
# and setters. Wave is NOT allowed to access anything in app.py (Subcontrollers 
# are not permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level of Missile Command.
    
    This subcontroller has a reference to the silos, the cities, and the target
    reticule. It also generates the missile from the JSON file. Aside from the
    target reticule, all of these are classes defined in models.py.
    
    If you want to pause the game, tell this controller to draw, but do not 
    update. See subcontrollers.py from lecture for an example. This class will 
    be similar to that one in many ways.
    
    All attributes of this class are to be hidden. No attribute should be 
    accessed  without going through a getter/setter first. However, just 
    because you have an attribute does not mean that you have to have a getter 
    for it. For example, the MissileShielf app probably never needs to access 
    the attribute for the target reticule, so there is no need for a getter.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _data: the wave dict after checks, with speed and missiles in it.
    # _bomb_speed: how fast bombs fall, in pixels/sec; finite and > 0.
    # _silos: three Silo objects, lined up left to right.
    # _cities: six City objects; destroyed ones still stay in this list.
    # _targets: all nine starting City/Silo objects; slot order stays put.
    # _target: a Target, all of it onscreen and above the silos.
    # _pending_bombs: Bomb objects waiting for the scheduled launch times.
    # _falling_bombs: Bomb objects that launched and are still around.
    # _rockets: Rocket objects still flying or showing a blast.
    # _elapsed_time: active game seconds so far; always >= 0.
    # _lost: bool, True once we lose the last city.
    # _won: bool, True once all bombs/rockets end and a city is still here.
    # _features: a dict with four bools, one on/off switch per extra.
    # _custom_enabled: bool, True if we switched on at least one extra.
    # _forecast_visible: bool, True means show the optional forecasts.
    # _bookmarks: at most three saved (x, y) pairs inside the aim bounds.
    # _next_bookmark: next saved index to use, 0 through len(_bookmarks).
    # _replacement_bookmark: saved slot we replace next, from 0 to 2.
    # _bubble_seconds: charge we still have, from 0 to BUBBLE_CAPACITY.
    # _bubble_requested: bool, True while we hold the bubble key down.
    # _bubble_fraction: how much of the latest step had charge, as a fraction.
    # _intercepted_count: bombs stopped so far; always >= 0.
    # _recycled_count: rounds actually given back so far; always >= 0.
    # _constellation_points: at most 18 (x, y) pairs from bombs we stopped.
    # _notice: a short feedback string, or just an empty string.
    # _notice_seconds: seconds until the feedback goes away; always >= 0.
    # _sounds: one SoundEffects object using the current sound setting.
    # _hud_panel: the GRectangle behind the main top bar.
    # _hud_rules: three skinny GRectangles between the main counters.
    # _mode_label: lowercase GLabel for the rule name of this wave.
    # _metric_labels: three GLabels with city, ammo, and threat counts.
    # _metric_titles: three GLabels naming those counts in that same order.
    # _controls_label: a GLabel with the aim/fire keys shared by both modes.
    # _audio_label: a GLabel with the sound setting or unavailable message.
    # _tool_centers: maps the enabled feature names to horizontal centers.
    # _tool_panels: one GRectangle per extra turned on, in menu order.
    # _tool_labels: maps enabled feature names to lowercase value GLabels.
    # _tool_hint_labels: maps enabled feature names to key reminder GLabels.
    # _notice_panel: a GRectangle that only shows when we have a notice.
    # _notice_label: the GLabel for quick feedback below the status cards.
    # _bubble_track: the GRectangle under the slow field charge bar.
    # _bubble_fill: a GRectangle that stays inside the charge bar track.
    # _slot_labels: three GLabels, each with the fire key for one silo.
    # _bookmark_labels: three GLabels reused as numbers for saved aim spots.
    # _weather_labels: nine GLabels for the optional time-to-hit estimates.

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLost(self):
        """returns True once every city is gone, otherwise False."""
        return self._lost

    def getWon(self):
        """returns True if the wave is over and at least one city made it."""
        return self._won

    def getCustomEnabled(self):
        """returns True if any night post tool is on for this wave."""
        return self._custom_enabled

    def getModeName(self):
        """returns the short rule name shown in the top bar."""
        if self._custom_enabled:
            return 'night post'
        else:
            return 'standard defense'

    def getHelpRows(self):
        """
        returns lowercase help lines for the custom tools that are actually on.

        this is how the pause screen gets the controls, so the app can ask here
        instead of poking around in the hidden feature dictionary.
        """
        help_rows = []
        if self._features['forecast']:
            help_rows.append('f / preview bomb positions 1.5 seconds ahead')
        if self._features['bookmarks']:
            help_rows.append('b / save aim    tab / recall    x / clear')
        if self._features['time_bubble']:
            help_rows.append('space / hold to slow, release to recharge')
        if self._features['recycling']:
            help_rows.append('every 3 interceptions / 1 round returned')
        return help_rows

    def getCitiesLeft(self):
        """returns how many cities made it so far, as an int from 0 to 6."""
        living_city_count = 0
        for current_city in self._cities:
            if current_city.getAlive():
                living_city_count = living_city_count + 1
        return living_city_count

    def getAmmoCounts(self):
        """returns a new ammo list: left silo, then center, then right."""
        remaining_ammunition = []
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition.append(current_amount)
        return remaining_ammunition

    def getScore(self):
        """returns ammo * SCORE_AMMO + living cities * SCORE_CITY."""
        remaining_ammunition = 0
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition = remaining_ammunition + current_amount
        ammunition_score = remaining_ammunition * SCORE_AMMO
        surviving_city_score = self.getCitiesLeft() * SCORE_CITY
        total_score = ammunition_score + surviving_city_score
        return total_score

    def getSoundsEnabled(self):
        """returns True if sound is allowed, even when no audio can play."""
        return self._sounds.getEnabled()

    def getSoundsAvailable(self):
        """returns True if at least one of the supplied sounds loaded ok."""
        return self._sounds.getAvailable()

    def setSoundsEnabled(self, enabled):
        """
        switches the sound preference and updates the sound text to match.

        parameter enabled: whether future sounds may play
        precondition: enabled is a bool
        """
        self._sounds.setEnabled(enabled)
        self._update_audio_label()

    # INITIALIZER (standard form) TO LAYOUT THE MODELS
    def __init__(self, data):
        """
        sets up the defenses and every bomb that is due in this wave.

        bad wave data raises ValueError, so the app can explain the loading
        problem instead of trying to play a broken wave.

        parameter data: the contents read from a wave file
        precondition: data is any value returned by GameApp.load_json
        """
        self._data = data
        self._check_wave_data()
        self._bomb_speed = data['speed']
        self._elapsed_time = 0.0
        self._lost = False
        self._won = False
        self._notice = ''
        self._notice_seconds = 0.0
        self._make_defenses()
        self._make_bombs()
        self._rockets = []
        self._sounds = SoundEffects()
        self._make_bonus_state()
        self._make_hud()
        self._update_hud()

    # UPDATE METHOD TO MOVE THE TARGETS, BOMBS, AND ROCKETS
    def update(self, player_input, dt):
        """
        moves this wave along and checks if it is over yet.

        keys get read once per frame, but movement takes little steps because a
        slow frame could otherwise skip a blast. finished rockets go away
        before anything moves, so the biggest blast still gets one frame
        onscreen.

        parameter player_input: keyboard information passed in by the app
        precondition: player_input supports the key query methods of GInput

        parameter dt: seconds since the last frame
        precondition: dt is a finite nonnegative int or float
        """
        if self._lost:
            return
        elif self._won:
            return
        self._update_notice(dt)
        self._move_target(player_input, dt)
        self._read_bonus_keys(player_input)
        self._remove_finished_rockets()
        self._read_launch_keys(player_input)
        self._advance_world(dt)
        self._check_finished()
        self._update_hud()

    # DRAW METHOD TO DRAW THE GAME OBJECTS
    def draw(self, view):
        """
        puts the wave onscreen, but does not move it or read any new keys.

        parameter view: the place to draw the game objects
        precondition: view is the GView supplied by the app
        """
        if self._lost:
            for current_silo in self._silos:
                current_silo.draw(view)
            return
        if not self._won:
            self._draw_hud_surfaces(view)
        self._draw_bonus_guides(view)
        for current_city in self._cities:
            current_city.draw(view)
        for current_silo in self._silos:
            current_silo.draw(view)
        for current_bomb in self._falling_bombs:
            current_bomb.draw(view)
        for current_rocket in self._rockets:
            current_rocket.draw(view)
        if not self._won:
            self._draw_hud(view)
            self._draw_aim(view)

    def startSounds(self):
        """plays the quiet start sound once, after the app loads this wave."""
        self._sounds.play('start')

    def stopSounds(self):
        """stops current cues, like when pausing or leaving."""
        self._sounds.stop()

    def finishSounds(self, player_won):
        """
        stops the old sounds, then plays one for how the wave ended.

        parameter player_won: whether the player cleared the wave
        precondition: player_won is a bool
        """
        self._sounds.stop()
        if player_won:
            self._sounds.play('reward')
        else:
            self._sounds.play('impact')

    # ANY NECESSARY HELPERS (SHOULD BE HIDDEN)
    def _check_wave_data(self):
        """
        checks the wave dictionary before any game objects get made.

        bad data raises ValueError, so nothing tries to build a half-loaded
        wave.
        """
        if type(self._data) != dict:
            raise ValueError('The wave must contain a JSON object.')
        if 'speed' not in self._data:
            raise ValueError('The wave is missing its speed.')
        if 'missiles' not in self._data:
            raise ValueError('The wave is missing its missiles list.')
        wave_speed = self._data['speed']
        if not self._is_finite_number(wave_speed):
            raise ValueError('Wave speed must be a finite number.')
        if wave_speed <= 0:
            raise ValueError('Wave speed must be greater than zero.')
        if type(self._data['missiles']) != list:
            raise ValueError('The missiles value must be a list.')
        for missile_information in self._data['missiles']:
            self._check_missile_data(missile_information)
        self._check_feature_data()

    def _is_finite_number(self, value):
        """
        returns True for a finite int or float; a bool does not count.

        parameter value: the value to check
        precondition: value can be any python value
        """
        if type(value) == int:
            return True
        elif type(value) == float:
            if value > -float('inf'):
                if value < float('inf'):
                    return True
        return False

    def _check_missile_data(self, information):
        """
        raises ValueError if the missile position, target, or time is wrong.

        parameter information: one entry from the missiles list
        precondition: information can be any value read from the json file
        """
        if type(information) != dict:
            raise ValueError('Each missile must be a JSON object.')
        for required_key in ['x', 'target', 'time']:
            if required_key not in information:
                raise ValueError('A missile is missing ' + required_key + '.')
        horizontal_start = information['x']
        start_time = information['time']
        target_slot = information['target']
        if not self._is_finite_number(horizontal_start):
            raise ValueError('Missile x must be a finite number.')
        if horizontal_start < 0 or horizontal_start > GAME_WIDTH:
            raise ValueError('Missile x must be inside the window.')
        if not self._is_finite_number(start_time):
            raise ValueError('Missile time must be a finite number.')
        if start_time < 0:
            raise ValueError('Missile time cannot be negative.')
        if type(target_slot) != int:
            raise ValueError('Missile target must be an integer.')
        if target_slot < 0 or target_slot > 8:
            raise ValueError('Missile target must be from 0 through 8.')

    def _check_feature_data(self):
        """
        checks the extra switches, but original waves do not need any.

        raises ValueError for bad feature data, like an unknown name or a value
        that is not a bool.
        """
        if 'features' not in self._data:
            return
        feature_information = self._data['features']
        if type(feature_information) != dict:
            raise ValueError('The features value must be a JSON object.')
        feature_names = ['forecast', 'bookmarks', 'time_bubble', 'recycling']
        for current_name in feature_information:
            if current_name not in feature_names:
                raise ValueError('Unknown feature: ' + current_name)
            if type(feature_information[current_name]) != bool:
                raise ValueError('Feature flags must be true or false.')

    def _make_defenses(self):
        """puts the three silos and six cities in their nine fixed slots."""
        # ugh im so busy pls help 😭
        self._silos = []
        self._cities = []
        self._targets = []
        slot_width = GAME_WIDTH / 9
        for slot_number in range(9):
            slot_left_edge = slot_number * slot_width
            slot_center = slot_left_edge + slot_width / 2
            if slot_number == 0 or slot_number == 4 or slot_number == 8:
                new_defense = Silo(slot_center)
                self._silos.append(new_defense)
            else:
                new_defense = City(slot_center)
                self._cities.append(new_defense)
            self._targets.append(new_defense)
        self._target = Target(GAME_WIDTH / 2, GAME_HEIGHT / 2)

    def _make_bombs(self):
        """makes waiting bombs, even if the drop times are unsorted."""
        self._pending_bombs = []
        self._falling_bombs = []
        for missile_information in self._data['missiles']:
            starting_x = missile_information['x']
            starting_y = GAME_HEIGHT
            target_slot = missile_information['target']
            target_object = self._targets[target_slot]
            destination_x = target_object.x
            destination_y = target_object.top
            starting_time = missile_information['time']
            new_bomb = Bomb(starting_x, starting_y,
                            destination_x, destination_y,
                            starting_time, target_slot)
            self._pending_bombs.append(new_bomb)

    def _make_bonus_state(self):
        """sets up the extras, but keeps them off for starter waves."""
        self._features = {}
        self._custom_enabled = False
        feature_names = ['forecast', 'bookmarks', 'time_bubble', 'recycling']
        for current_name in feature_names:
            self._features[current_name] = False
            if 'features' in self._data:
                if current_name in self._data['features']:
                    enabled = self._data['features'][current_name]
                    self._features[current_name] = enabled
                    if enabled:
                        self._custom_enabled = True
        self._forecast_visible = self._features['forecast']
        self._bookmarks = []
        self._next_bookmark = 0
        self._replacement_bookmark = 0
        self._bubble_seconds = BUBBLE_CAPACITY
        self._bubble_requested = False
        self._bubble_fraction = 0.0
        self._intercepted_count = 0
        self._recycled_count = 0
        self._constellation_points = []

    def _move_target(self, player_input, dt):
        """
        speeds up the aim while arrows are held, then checks every edge.

        the starter speeds 0.2 and 10 are for a nominal frame, so
        AIM_FRAME_SCALE turns them into movement over time using a nominal 60
        fps.

        parameter player_input: current keyboard information
        precondition: player_input supports is_key_down
        parameter dt: seconds of active gameplay that have passed
        precondition: dt is a finite nonnegative number
        """
        directions = self._read_directions(player_input)
        horizontal_direction = directions[0]
        vertical_direction = directions[1]
        arrows_are_down = directions[2]
        if arrows_are_down:
            old_speed = self._target.getSpeed()
            additional_speed = AIM_SPEED_STEP * dt * AIM_FRAME_SCALE
            new_speed = old_speed + additional_speed
            if new_speed > AIM_SPEED_LIMIT:
                new_speed = AIM_SPEED_LIMIT
            self._target.setSpeed(new_speed)
        else:
            self._target.setSpeed(0)
        movement_distance = self._target.getSpeed() * dt * AIM_FRAME_SCALE
        horizontal_step = horizontal_direction * movement_distance
        vertical_step = vertical_direction * movement_distance
        self._target.x = self._target.x + horizontal_step
        self._target.y = self._target.y + vertical_step
        self._keep_target_inside()

    def _read_directions(self, player_input):
        """
        returns horizontal direction, vertical direction, and whether any arrow
        is held.

        for example, left and right cancel the horizontal movement, but the
        last value is still True because arrows are being held.

        parameter player_input: current keyboard information
        precondition: player_input supports is_key_down
        """
        horizontal_direction = 0
        vertical_direction = 0
        arrows_are_down = False
        if player_input.is_key_down('left'):
            horizontal_direction = horizontal_direction - 1
            arrows_are_down = True
        if player_input.is_key_down('right'):
            horizontal_direction = horizontal_direction + 1
            arrows_are_down = True
        if player_input.is_key_down('up'):
            vertical_direction = vertical_direction + 1
            arrows_are_down = True
        if player_input.is_key_down('down'):
            vertical_direction = vertical_direction - 1
            arrows_are_down = True
        return (horizontal_direction, vertical_direction, arrows_are_down)

    def _keep_target_inside(self):
        """keeps the whole aim marker onscreen and above the silo tops."""
        if self._target.left < 0:
            self._target.left = 0
        elif self._target.right > GAME_WIDTH:
            self._target.right = GAME_WIDTH
        if self._target.bottom < SILO_HEIGHT:
            self._target.bottom = SILO_HEIGHT
        elif self._target.top > GAME_HEIGHT:
            self._target.top = GAME_HEIGHT

    def _read_launch_keys(self, player_input):
        """
        fires at most one rocket per silo for each new press of that key.

        parameter player_input: current keyboard information
        precondition: player_input supports is_key_pressed
        """
        if player_input.is_key_pressed('1'):
            self._launch_from_silo(0)
        if player_input.is_key_pressed('2'):
            self._launch_from_silo(1)
        if player_input.is_key_pressed('3'):
            self._launch_from_silo(2)

    def _launch_from_silo(self, silo_number):
        """
        fires at the current aim point if that silo still has ammo.

        the destination gets saved now, so moving the aim later leaves this
        rocket headed to the same spot.

        parameter silo_number: the index of the silo to fire from
        precondition: silo_number is 0, 1, or 2
        """
        chosen_silo = self._silos[silo_number]
        previous_ammunition = chosen_silo.getAmmo()
        if previous_ammunition == 0:
            silo_key = str(silo_number + 1)
            self._show_notice('silo ' + silo_key + ' is empty. try another.')
            self._sounds.play('empty')
            return
        starting_x = chosen_silo.x
        starting_y = chosen_silo.top
        destination_x = self._target.x
        destination_y = self._target.y
        new_rocket = Rocket(starting_x, starting_y,
                            destination_x, destination_y)
        self._rockets.append(new_rocket)
        chosen_silo.setAmmo(previous_ammunition - 1)
        self._sounds.play('launch')

    def _remove_finished_rockets(self):
        """clears finished rockets after the full blast was drawn once."""
        rocket_position = 0
        while rocket_position < len(self._rockets):
            current_rocket = self._rockets[rocket_position]
            if current_rocket.getFinished():
                del self._rockets[rocket_position]
            else:
                rocket_position = rocket_position + 1

    def _advance_world(self, dt):
        """
        runs the game in little time steps, but does not reread key presses.

        parameter dt: seconds of active gameplay to run
        precondition: dt is a finite nonnegative number
        """
        seconds_remaining = dt
        while seconds_remaining > 0:
            if self._lost or self._won:
                return
            step_seconds = seconds_remaining
            if step_seconds > PHYSICS_STEP:
                step_seconds = PHYSICS_STEP
            if self._bubble_requested:
                if 0 < self._bubble_seconds < step_seconds:
                    step_seconds = self._bubble_seconds
            self._step_world(step_seconds)
            seconds_remaining = seconds_remaining - step_seconds

    def _step_world(self, step_seconds):
        """
        runs one little movement step, checks hits, then checks if we are done.

        parameter step_seconds: time for this small movement step
        precondition: step_seconds is positive and at most PHYSICS_STEP
        """
        self._elapsed_time = self._elapsed_time + step_seconds
        self._update_bubble_charge(step_seconds)
        self._release_bombs()
        self._resolve_interceptions()
        self._move_rockets(step_seconds)
        self._move_bombs(step_seconds)
        self._resolve_interceptions()
        self._resolve_impacts()
        self._check_finished()

    def _move_rockets(self, step_seconds):
        """
        moves the rockets and plays one sound as each blast starts.

        a blast already growing had its sound, so it does not get another one
        here.

        parameter step_seconds: seconds for this movement step
        precondition: step_seconds is positive and at most PHYSICS_STEP
        """
        for current_rocket in self._rockets:
            was_exploding = current_rocket.getExploding()
            current_rocket.update(step_seconds)
            if not was_exploding:
                if current_rocket.getExploding():
                    self._sounds.play('explode')

    def _release_bombs(self):
        """lets every bomb due now fall, even if the list is out of order."""
        pending_position = 0
        while pending_position < len(self._pending_bombs):
            current_bomb = self._pending_bombs[pending_position]
            # tiny wiggle room bc adding little time steps can round them
            comparison_time = self._elapsed_time + 0.000000001
            if current_bomb.getStartTime() <= comparison_time:
                self._falling_bombs.append(current_bomb)
                del self._pending_bombs[pending_position]
            else:
                pending_position = pending_position + 1

    def _move_bombs(self, step_seconds):
        """
        moves each bomb for only the time since it was actually released.

        parameter step_seconds: time for this movement step
        precondition: step_seconds is a finite nonnegative number
        """
        for current_bomb in self._falling_bombs:
            seconds_since_release = self._elapsed_time
            seconds_since_release -= current_bomb.getStartTime()
            movement_seconds = step_seconds
            if seconds_since_release < movement_seconds:
                movement_seconds = seconds_since_release
            if movement_seconds < 0:
                movement_seconds = 0
            current_speed = self._get_bomb_speed(current_bomb)
            current_bomb.update(movement_seconds, current_speed)

    def _resolve_interceptions(self):
        """takes a bomb out if the center of it is inside a rocket blast."""
        bomb_position = 0
        while bomb_position < len(self._falling_bombs):
            current_bomb = self._falling_bombs[bomb_position]
            intercepted = self._is_inside_explosion(current_bomb)
            if intercepted:
                self._record_interception(current_bomb)
                del self._falling_bombs[bomb_position]
            else:
                bomb_position = bomb_position + 1

    def _is_inside_explosion(self, current_bomb):
        """
        returns whether any rocket blast contains the center of this bomb.

        parameter current_bomb: the bomb to check
        precondition: current_bomb is a Bomb
        """
        bomb_center = (current_bomb.x, current_bomb.y)
        for current_rocket in self._rockets:
            if current_rocket.getExploding():
                if current_rocket.contains(bomb_center):
                    return True
        return False

    def _resolve_impacts(self):
        """handles hits, but leaves all targets in the original slots."""
        bomb_position = 0
        while bomb_position < len(self._falling_bombs):
            current_bomb = self._falling_bombs[bomb_position]
            if current_bomb.getArrived():
                target_slot = current_bomb.getTargetSlot()
                target_object = self._targets[target_slot]
                if isinstance(target_object, Silo):
                    target_object.setAmmo(0)
                else:
                    target_object.destroy()
                self._sounds.play('impact')
                del self._falling_bombs[bomb_position]
                if self.getCitiesLeft() == 0:
                    self._finish_loss()
                    return
            else:
                bomb_position = bomb_position + 1

    def _check_finished(self):
        """
        checks for a loss first, then waits for all bombs and rockets to end.

        a waiting bomb counts too, so a quiet moment between launches is not a
        win.
        """
        if self.getCitiesLeft() == 0:
            self._finish_loss()
            return
        if len(self._pending_bombs) != 0:
            return
        if len(self._falling_bombs) != 0:
            return
        if len(self._rockets) != 0:
            return
        self._won = True
        self._bubble_fraction = 0.0

    def _finish_loss(self):
        """ends the wave right away and leaves only the silos onscreen."""
        self._lost = True
        self._won = False
        self._pending_bombs = []
        self._falling_bombs = []
        self._rockets = []
        self._bookmarks = []
        self._next_bookmark = 0
        self._constellation_points = []
        self._bubble_fraction = 0.0
        self._bubble_requested = False

    def _read_bonus_keys(self, player_input):
        """
        checks the extra keys only if the wave file turned those tools on.

        parameter player_input: current keyboard information
        precondition: player_input supports the key query methods of GInput
        """
        if not self._custom_enabled:
            return
        if self._features['forecast']:
            if player_input.is_key_pressed('f'):
                self._forecast_visible = not self._forecast_visible
        if self._features['bookmarks']:
            if player_input.is_key_pressed('b'):
                self._save_bookmark()
            if player_input.is_key_pressed('tab'):
                self._recall_bookmark()
            if player_input.is_key_pressed('x'):
                self._bookmarks = []
                self._next_bookmark = 0
                self._replacement_bookmark = 0
                self._show_notice('Sky bookmarks cleared.')
        self._bubble_requested = False
        if self._features['time_bubble']:
            self._bubble_requested = player_input.is_key_down('spacebar')
            if player_input.is_key_down('space'):
                self._bubble_requested = True

    def _save_bookmark(self):
        """saves the aim point; after three saves, replaces the oldest slot."""
        saved_position = (self._target.x, self._target.y)
        if len(self._bookmarks) < 3:
            self._bookmarks.append(saved_position)
            saved_number = len(self._bookmarks)
        else:
            saved_slot = self._replacement_bookmark
            self._bookmarks[saved_slot] = saved_position
            saved_number = saved_slot + 1
            self._replacement_bookmark = self._replacement_bookmark + 1
            if self._replacement_bookmark == 3:
                self._replacement_bookmark = 0
        message = 'Sky bookmark ' + str(saved_number) + ' saved.'
        self._show_notice(message + ' Tab recalls saved positions.')

    def _recall_bookmark(self):
        """
        cycles through saved aim points without redirecting any rockets.

        basically, only the aim jumps back; launched rockets keep the saved
        destinations.
        """
        # im so tired bro 😴
        if len(self._bookmarks) == 0:
            self._show_notice('Aim somewhere useful, then press B to save it.')
            return
        if self._next_bookmark >= len(self._bookmarks):
            self._next_bookmark = 0
        saved_position = self._bookmarks[self._next_bookmark]
        self._target.x = saved_position[0]
        self._target.y = saved_position[1]
        self._target.setSpeed(0)
        self._keep_target_inside()
        bookmark_number = self._next_bookmark + 1
        self._show_notice('Recalled sky bookmark ' + str(bookmark_number) + '.')
        self._next_bookmark = self._next_bookmark + 1

    def _update_bubble_charge(self, step_seconds):
        """
        uses charge while the key is held, then refills when it is let go.

        parameter step_seconds: real active time for this movement step
        precondition: step_seconds is positive
        """
        self._bubble_fraction = 0.0
        if not self._features['time_bubble']:
            return
        if self._bubble_requested:
            powered_seconds = step_seconds
            if powered_seconds > self._bubble_seconds:
                powered_seconds = self._bubble_seconds
            self._bubble_fraction = powered_seconds / step_seconds
            self._bubble_seconds = self._bubble_seconds - powered_seconds
        else:
            recovered_seconds = step_seconds * BUBBLE_RECHARGE
            self._bubble_seconds = self._bubble_seconds + recovered_seconds
            if self._bubble_seconds > BUBBLE_CAPACITY:
                self._bubble_seconds = BUBBLE_CAPACITY

    def _get_bomb_speed(self, current_bomb):
        """
        returns normal speed, or a slower speed inside an active bubble.

        only bombs in the bubble slow down, so the launch clock, rockets, and
        blasts all keep the original timing.

        parameter current_bomb: the bomb that needs a speed
        precondition: current_bomb is a Bomb
        """
        normal_speed = self._bomb_speed
        if self._bubble_fraction <= 0:
            return normal_speed
        horizontal_gap = current_bomb.x - self._target.x
        vertical_gap = current_bomb.y - self._target.y
        distance_squared = horizontal_gap ** 2 + vertical_gap ** 2
        bubble_radius_squared = BUBBLE_RADIUS ** 2
        if distance_squared > bubble_radius_squared:
            return normal_speed
        removed_fraction = self._bubble_fraction * (1 - BUBBLE_SPEED_FACTOR)
        remaining_fraction = 1 - removed_fraction
        slower_speed = normal_speed * remaining_fraction
        return slower_speed

    def _record_interception(self, current_bomb):
        """
        counts the bomb we stopped and checks for the optional ammo reward.

        parameter current_bomb: the stopped bomb, before it is removed
        precondition: current_bomb is a Bomb
        """
        self._sounds.play('intercept')
        self._intercepted_count = self._intercepted_count + 1
        if not self._features['recycling']:
            return
        saved_position = (current_bomb.x, current_bomb.y)
        self._constellation_points.append(saved_position)
        if len(self._constellation_points) > 18:
            del self._constellation_points[0]
        # ok so the bad mail gets to be a little star now ✨
        completed_group = self._intercepted_count % RECYCLE_GROUP_SIZE
        if completed_group == 0:
            self._recycle_ammunition()

    def _recycle_ammunition(self):
        """
        gives one round to the silo with the least ammo, but never past ten.
        """
        chosen_silo_number = 0
        for silo_number in range(len(self._silos)):
            candidate_count = self._silos[silo_number].getAmmo()
            chosen_count = self._silos[chosen_silo_number].getAmmo()
            if candidate_count < chosen_count:
                chosen_silo_number = silo_number
        chosen_silo = self._silos[chosen_silo_number]
        previous_ammunition = chosen_silo.getAmmo()
        if previous_ammunition < AMMO_COUNT:
            chosen_silo.setAmmo(previous_ammunition + 1)
            self._recycled_count = self._recycled_count + 1
            self._sounds.play('reward')
            silo_name = str(chosen_silo_number + 1)
            self._show_notice('Comet compost: +1 rocket returned to silo '
                              + silo_name + '.')
        else:
            self._show_notice('Comet compost: all silos are already full.')

    def _show_notice(self, message):
        """
        puts up a quick message while the game carries on.

        parameter message: the feedback to show
        precondition: message is a string that fits on one display line
        """
        self._notice = message.lower()
        self._notice_seconds = 2.8

    def _update_notice(self, dt):
        """
        clears the feedback once enough active game time has gone by.

        parameter dt: seconds of active gameplay that have passed
        precondition: dt is a finite nonnegative number
        """
        self._notice_seconds = self._notice_seconds - dt
        if self._notice_seconds <= 0:
            self._notice_seconds = 0.0
            self._notice = ''

    def _make_hud(self):
        """makes the simple top bar, any tool cards, and the little notices."""
        self._hud_panel = GRectangle(x=GAME_WIDTH / 2, y=807,
                                    width=GAME_WIDTH - 48, height=70,
                                    fillcolor=UI_SURFACE,
                                    linecolor=UI_BORDER, linewidth=0.7)
        self._mode_label = self._make_label(self.getModeName(), 56,
                                           820, 22, UI_TEXT)
        self._mode_label.font_name = THEME_FONT
        self._mode_label.left = 56
        controls = 'arrows aim   1 / 2 / 3 fire   p pause'
        self._controls_label = self._make_label(controls, 56,
                                               789, 12, UI_MUTED)
        self._controls_label.left = 56
        self._audio_label = self._make_label('', 456, 820, 11, UI_MUTED)
        self._make_metric_labels()
        self._make_tool_cards()
        self._make_bubble_meter()
        self._make_notice_label()
        self._make_slot_labels()

    def _make_label(self, text, x, y, size, color):
        """
        returns a lowercase label with the readable font from the starter.

        parameter text: the words to show; must be a string
        parameter x: horizontal center; must be a number
        parameter y: vertical center; must be a number
        parameter size: font size; must be a positive number
        parameter color: text color; must be a valid game2d color
        """
        new_label = GLabel(text=text.lower(), x=x, y=y,
                           font_name=BASIC_FONT, font_size=size,
                           linecolor=color)
        return new_label

    def _make_metric_labels(self):
        """
        gives cities, ammo, and incoming bombs separate spots in the top bar.
        """
        self._metric_labels = []
        self._metric_titles = []
        self._hud_rules = []
        metric_names = ['cities', 'ammo', 'incoming']
        for metric_number in range(3):
            metric_x = 658 + 172 * metric_number
            value_label = self._make_label('', metric_x, 819, 26, UI_TEXT)
            value_label.font_name = THEME_FONT
            self._metric_labels.append(value_label)
            metric_name = metric_names[metric_number]
            title_label = self._make_label(metric_name, metric_x,
                                           789, 11, UI_MUTED)
            self._metric_titles.append(title_label)
            rule = GRectangle(x=metric_x - 86, y=807, width=1, height=38,
                              fillcolor=UI_BORDER)
            self._hud_rules.append(rule)

    def _make_tool_cards(self):
        """makes room for just the tool cards that this wave turns on."""
        self._tool_centers = {}
        self._tool_panels = []
        self._tool_labels = {}
        self._tool_hint_labels = {}
        tool_names = ['forecast', 'bookmarks', 'time_bubble', 'recycling']
        enabled_count = 0
        for tool_name in tool_names:
            if self._features[tool_name]:
                enabled_count = enabled_count + 1
        if enabled_count == 0:
            return
        slot_width = (GAME_WIDTH - 36) / enabled_count
        current_slot = 0
        for tool_name in tool_names:
            if self._features[tool_name]:
                center_x = 24 + current_slot * slot_width
                center_x = center_x + (slot_width - 12) / 2
                self._tool_centers[tool_name] = center_x
                self._make_tool_card(tool_name, center_x, slot_width - 12)
                current_slot = current_slot + 1

    def _make_tool_card(self, tool_name, center_x, width):
        """
        makes one little card showing a value and a quick key reminder.

        parameter tool_name: the feature flag of this card
        precondition: tool_name is an enabled key in _features
        parameter center_x: the horizontal center; must be a number
        parameter width: the card width; must be a positive number
        """
        panel = GRectangle(x=center_x, y=733, width=width, height=54,
                           fillcolor=UI_SURFACE_SOFT,
                           linecolor=UI_BORDER, linewidth=0.5)
        self._tool_panels.append(panel)
        label = self._make_label('', center_x, 745, 16, UI_ACCENT)
        self._tool_labels[tool_name] = label
        hint = self._make_label('', center_x, 721, 11, UI_MUTED)
        self._tool_hint_labels[tool_name] = hint

    def _make_notice_label(self):
        """puts the quick feedback below the top bar and any tool cards."""
        notice_y = 741
        if self._custom_enabled:
            notice_y = 678
        self._notice_panel = GRectangle(x=GAME_WIDTH / 2, y=notice_y,
                                        width=610, height=30,
                                        fillcolor=UI_SURFACE,
                                        linecolor=UI_BORDER, linewidth=0.5)
        self._notice_label = self._make_label('', GAME_WIDTH / 2,
                                             notice_y, 14, UI_AMBER)

    def _make_bubble_meter(self):
        """
        gets the charge bar ready; it only shows with the slow field card.
        """
        center_x = GAME_WIDTH / 2
        if self._features['time_bubble']:
            center_x = self._tool_centers['time_bubble']
            self._tool_hint_labels['time_bubble'].x = center_x - 67
        self._bubble_track = GRectangle(x=center_x + 26, y=721,
                                        width=96, height=3,
                                        fillcolor=UI_BORDER)
        self._bubble_fill = GRectangle(x=center_x + 26, y=721,
                                       width=96, height=3,
                                       fillcolor=UI_ACCENT)

    def _make_slot_labels(self):
        """makes the silo key tags and time-to-hit labels above the targets."""
        self._slot_labels = []
        for silo_number in range(len(self._silos)):
            silo_x = self._silos[silo_number].x
            key_text = str(silo_number + 1)
            key_label = self._make_label(key_text, silo_x, 143, 12, UI_TEXT)
            key_label.width = 26
            key_label.height = 19
            key_label.fillcolor = UI_SURFACE
            self._slot_labels.append(key_label)
        self._weather_labels = []
        for target_object in self._targets:
            label_height = target_object.top + 35
            weather_label = self._make_label('', target_object.x,
                                             label_height, 13, UI_AMBER)
            self._weather_labels.append(weather_label)
        self._make_bookmark_labels()

    def _make_bookmark_labels(self):
        """
        keeps aim labels around because kivy needs time to make the textures.
        """
        self._bookmark_labels = []
        for bookmark_number in range(3):
            label_text = str(bookmark_number + 1)
            bookmark_label = self._make_label(label_text, 0, 0, 13, HUD_MINT)
            self._bookmark_labels.append(bookmark_label)

    def _update_hud(self):
        """refreshes the numbers onscreen, but leaves the game rules alone."""
        total_ammunition = 0
        for current_silo in self._silos:
            total_ammunition = total_ammunition + current_silo.getAmmo()
        remaining_threats = len(self._pending_bombs) + len(self._falling_bombs)
        self._metric_labels[0].text = str(self.getCitiesLeft()) + ' / 6'
        self._metric_labels[1].text = str(total_ammunition)
        self._metric_labels[2].text = str(remaining_threats)
        self._notice_label.text = self._notice.lower()
        self._update_audio_label()
        self._update_bonus_hud()

    def _update_audio_label(self):
        """shows the sound setting, or says if audio could not load."""
        if not self._sounds.getAvailable():
            self._audio_label.text = 'audio unavailable'
        elif self._sounds.getEnabled():
            self._audio_label.text = 'v  sound on'
        else:
            self._audio_label.text = 'v  sound off'

    def _update_bonus_hud(self):
        """refreshes only the tool cards switched on by this wave file."""
        if self._features['forecast']:
            forecast_text = 'forecast off'
            if self._forecast_visible:
                forecast_text = 'forecast on'
            self._tool_labels['forecast'].text = forecast_text
            self._tool_hint_labels['forecast'].text = 'f toggle  /  1.5s ahead'
        if self._features['bookmarks']:
            bookmark_text = 'bookmarks ' + str(len(self._bookmarks)) + ' / 3'
            self._tool_labels['bookmarks'].text = bookmark_text
            bookmark_hint = 'b save  /  tab recall  /  x clear'
            self._tool_hint_labels['bookmarks'].text = bookmark_hint
        if self._features['time_bubble']:
            self._update_bubble_meter()
        if self._features['recycling']:
            self._update_recycling_meter()
        if self._forecast_visible:
            self._update_weather_reports()

    def _update_bubble_meter(self):
        """shows charge left and keeps the colored fill inside the bar."""
        remaining_tenths = int(self._bubble_seconds * 10) / 10
        bubble_text = 'slow field ' + str(remaining_tenths) + 's'
        self._tool_labels['time_bubble'].text = bubble_text
        self._tool_hint_labels['time_bubble'].text = 'space'
        charge_fraction = self._bubble_seconds / BUBBLE_CAPACITY
        filled_width = self._bubble_track.width * charge_fraction
        if filled_width < 0.1:
            filled_width = 0.1
        self._bubble_fill.width = filled_width
        self._bubble_fill.left = self._bubble_track.left

    def _update_recycling_meter(self):
        """
        shows progress to the next refund plus the ammo actually given back.
        """
        group_progress = self._intercepted_count % RECYCLE_GROUP_SIZE
        recycling_text = 'recycle ' + str(group_progress) + ' / 3'
        self._tool_labels['recycling'].text = recycling_text
        refund_text = '+' + str(self._recycled_count) + ' ammo returned'
        self._tool_hint_labels['recycling'].text = refund_text

    def _update_weather_reports(self):
        """shows the soonest active hit estimate above each living target."""
        for slot_number in range(len(self._targets)):
            smallest_time = None
            for current_bomb in self._falling_bombs:
                if current_bomb.getTargetSlot() == slot_number:
                    current_speed = self._get_bomb_speed(current_bomb)
                    remaining_time = current_bomb.getRemainingTime(
                        current_speed)
                    if smallest_time is None or remaining_time < smallest_time:
                        smallest_time = remaining_time
            report_label = self._weather_labels[slot_number]
            report_label.text = ''
            if smallest_time is not None:
                rounded_up_time = int(smallest_time + 0.999999)
                report_label.text = '~' + str(rounded_up_time) + 's'
            target_object = self._targets[slot_number]
            if isinstance(target_object, City):
                if not target_object.getAlive():
                    report_label.text = ''

    def _draw_bonus_guides(self, view):
        """
        puts the extra guides behind the actual bombs and defenses.

        parameter view: the place to draw the guides
        precondition: view is a GView
        """
        if not self._custom_enabled:
            return
        self._draw_constellations(view)
        if self._won:
            return
        if self._forecast_visible:
            self._draw_forecasts(view)
        if self._features['bookmarks']:
            self._draw_bookmarks(view)
        if self._bubble_fraction > 0:
            self._draw_bubble(view)

    def _draw_forecasts(self, view):
        """
        draws hollow rings where bombs might be later; these never hit
        anything.

        this uses the current speed for the next FORECAST_SECONDS, but moving
        the bubble can change that speed, so the rings are just an estimate.

        parameter view: the place to draw the forecasts
        precondition: view is a GView
        """
        for current_bomb in self._falling_bombs:
            current_speed = self._get_bomb_speed(current_bomb)
            future_point = current_bomb.getFuturePosition(FORECAST_SECONDS,
                                                         current_speed)
            guide_points = [current_bomb.x, current_bomb.y,
                            future_point[0], future_point[1]]
            guide_line = GPath(points=guide_points, linewidth=0.7,
                               linecolor=(0.96, 0.78, 0.47, 0.33))
            future_ring = GEllipse(x=future_point[0], y=future_point[1],
                                   width=12, height=12, linewidth=1.2,
                                   fillcolor=(0, 0, 0, 0), linecolor=HUD_AMBER)
            guide_line.draw(view)
            future_ring.draw(view)

    def _draw_bookmarks(self, view):
        """
        draws up to three numbered aim markers, but they never affect hits.

        parameter view: the place to draw the markers
        precondition: view is a GView
        """
        for bookmark_number in range(len(self._bookmarks)):
            saved_point = self._bookmarks[bookmark_number]
            bookmark_ring = GEllipse(x=saved_point[0], y=saved_point[1],
                                     width=28, height=28, linewidth=1,
                                     fillcolor=(0, 0, 0, 0),
                                     linecolor=(0.58, 0.88, 0.85, 0.48))
            label_y = saved_point[1] + 25
            if label_y > GAME_HEIGHT - 90:
                label_y = saved_point[1] - 25
            bookmark_label = self._bookmark_labels[bookmark_number]
            bookmark_label.x = saved_point[0]
            bookmark_label.y = label_y
            bookmark_ring.draw(view)
            bookmark_label.draw(view)

    def _draw_bubble(self, view):
        """
        draws the mint slow field so it is easy to tell from a blue blast.

        parameter view: the place to draw the ring
        precondition: view is a GView
        """
        diameter = 2 * BUBBLE_RADIUS
        bubble = GEllipse(x=self._target.x, y=self._target.y,
                          width=diameter, height=diameter, linewidth=1.5,
                          fillcolor=(0.53, 0.93, 0.88, 0.06),
                          linecolor=(0.53, 0.93, 0.88, 0.68))
        inner_bubble = GEllipse(x=self._target.x, y=self._target.y,
                                width=diameter - 12, height=diameter - 12,
                                linewidth=0.5, fillcolor=(0, 0, 0, 0),
                                linecolor=(0.53, 0.93, 0.88, 0.24))
        bubble.draw(view)
        inner_bubble.draw(view)

    def _draw_constellations(self, view):
        """
        draws little stars for stopped bombs; the stars never count as hits.

        parameter view: the place to draw the stars
        precondition: view is a GView
        """
        previous_point = None
        for star_position in range(len(self._constellation_points)):
            current_point = self._constellation_points[star_position]
            if previous_point is not None:
                points = [previous_point[0], previous_point[1],
                          current_point[0], current_point[1]]
                connection = GPath(points=points, linewidth=0.55,
                                    linecolor=(0.63, 0.94, 0.89, 0.16))
                connection.draw(view)
            tiny_star = GEllipse(x=current_point[0], y=current_point[1],
                                 width=4, height=4,
                                 fillcolor=(0.63, 0.94, 0.89, 0.58))
            tiny_star.draw(view)
            previous_point = current_point

    def _draw_aim(self, view):
        """
        draws the original aim marker with an outline so it stands out.

        parameter view: the place to draw the reticule
        precondition: view is a GView
        """
        target_outline = GEllipse(x=self._target.x, y=self._target.y,
                                  width=AIM_WIDTH, height=AIM_HEIGHT,
                                  fillcolor=(0, 0, 0, 0), linewidth=0.8,
                                  linecolor=UI_ACCENT)
        target_outline.draw(view)
        self._target.draw(view)

    def _draw_hud(self, view):
        """
        draws the labels over the game, so the status text stays readable.

        parameter view: the place to draw the displays
        precondition: view is a GView
        """
        self._mode_label.draw(view)
        self._controls_label.draw(view)
        self._audio_label.draw(view)
        for current_label in self._metric_labels:
            current_label.draw(view)
        for current_label in self._metric_titles:
            current_label.draw(view)
        self._draw_tool_labels(view)
        for current_label in self._slot_labels:
            current_label.draw(view)
        if self._notice != '':
            self._notice_panel.draw(view)
            self._notice_label.draw(view)
        if self._forecast_visible:
            for weather_label in self._weather_labels:
                weather_label.draw(view)

    def _draw_hud_surfaces(self, view):
        """
        draws card backgrounds first so falling bombs do not get covered.

        parameter view: the place to draw the surfaces
        precondition: view is a GView
        """
        self._hud_panel.draw(view)
        for current_rule in self._hud_rules:
            current_rule.draw(view)
        for current_panel in self._tool_panels:
            current_panel.draw(view)

    def _draw_tool_labels(self, view):
        """
        draws the enabled tool values, key reminders, and optional charge bar.

        parameter view: the place to draw the tools
        precondition: view is a GView
        """
        for tool_name in self._tool_labels:
            self._tool_labels[tool_name].draw(view)
            self._tool_hint_labels[tool_name].draw(view)
        if self._features['time_bubble']:
            self._bubble_track.draw(view)
            self._bubble_fill.draw(view)

# omg this took so long 😭