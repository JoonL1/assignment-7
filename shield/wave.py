"""
The controller for one complete wave of Missile Shield.

Standard waves use the original rules. A wave with a features dictionary can
also use the four Night Post features documented in README.txt. Every threat
still comes from the wave file, and the original win and loss rules apply.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
Framework and original assets: the supplied CS 1110 assignment package.
"""
from game2d import GRectangle, GEllipse, GPath, GLabel
from consts import *
from models import Silo, City, Target, Bomb, Rocket


class Wave(object):
    """
    A controller for one wave, its defenses, and its optional Night Post tools.

    All new attributes are hidden. The main application asks this controller
    for results through getters and passes input, elapsed time, and the view
    through public methods. Models never need a reference to this controller.
    """
    # _data: the validated wave dictionary; contains speed and missiles.
    # _bomb_speed: the finite positive bomb speed, in pixels per second.
    # _silos: the three Silo objects, ordered left to right.
    # _cities: the six City objects, including any destroyed cities.
    # _targets: the nine original City/Silo objects in fixed slot order.
    # _target: the Target object, fully in bounds and above the silos.
    # _pending_bombs: Bomb objects whose launch times have not arrived.
    # _falling_bombs: Bomb objects that have launched and still exist.
    # _rockets: Rocket objects in flight or displaying an explosion.
    # _elapsed_time: the nonnegative number of active wave seconds.
    # _lost: a bool; True once the last city is destroyed.
    # _won: a bool; True once all bombs and rockets are gone with cities left.
    # _features: a dictionary of the four optional feature booleans.
    # _custom_enabled: a bool; True if at least one optional feature is on.
    # _forecast_visible: a bool; controls optional future-position guides.
    # _bookmarks: at most three pairs of legal aiming coordinates.
    # _next_bookmark: the next recall index, from 0 through len(_bookmarks).
    # _replacement_bookmark: the next bookmark slot to replace, from 0 to 2.
    # _bubble_seconds: remaining charge, from 0 to BUBBLE_CAPACITY.
    # _bubble_requested: a bool; the player is holding the bubble control.
    # _bubble_fraction: the fraction of the latest step with bubble power.
    # _intercepted_count: the nonnegative number of bombs intercepted.
    # _recycled_count: the nonnegative number of rockets actually refunded.
    # _constellation_points: at most 18 (x, y) pairs from intercepted bombs.
    # _notice: the temporary feedback string, possibly empty.
    # _notice_seconds: the nonnegative remaining life of the feedback string.
    # _hud_panel: the GRectangle behind the active game's controls.
    # _mode_label: the GLabel naming the wave mode.
    # _numbers_label: the GLabel showing cities, ammo, and threats.
    # _controls_label: the GLabel showing the current control keys.
    # _notice_label: the GLabel for brief feedback above the playing field.
    # _bubble_label: the GLabel showing the remaining bubble charge.
    # _bubble_track: the GRectangle behind the charge bar.
    # _bubble_fill: the GRectangle showing the filled portion of the bar.
    # _slot_labels: three GLabels identifying the silo launch keys.
    # _bookmark_labels: three persistent GLabels numbering saved aim points.
    # _weather_labels: nine GLabels for optional impact-time reports.
    # _recycling_label: the GLabel showing progress toward an ammo refund.

    def getLost(self):
        """Returns True if every city has been destroyed; otherwise False."""
        return self._lost

    def getWon(self):
        """Returns True if the wave ended with at least one surviving city."""
        return self._won

    def getCustomEnabled(self):
        """Returns True if the wave file enabled any Night Post features."""
        return self._custom_enabled

    def getModeName(self):
        """Returns the short display name for this wave's rule set."""
        if self._custom_enabled:
            return 'NIGHT POST'
        else:
            return 'STANDARD DEFENSE'

    def getCitiesLeft(self):
        """Returns the number of living cities, an integer from 0 to 6."""
        living_city_count = 0
        for current_city in self._cities:
            if current_city.getAlive():
                living_city_count = living_city_count + 1
        return living_city_count

    def getAmmoCounts(self):
        """Returns a new list with the left, center, and right ammo counts."""
        remaining_ammunition = []
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition.append(current_amount)
        return remaining_ammunition

    def getScore(self):
        """Returns ammo times SCORE_AMMO plus living cities times SCORE_CITY."""
        remaining_ammunition = 0
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition = remaining_ammunition + current_amount
        ammunition_score = remaining_ammunition * SCORE_AMMO
        surviving_city_score = self.getCitiesLeft() * SCORE_CITY
        total_score = ammunition_score + surviving_city_score
        return total_score

    def __init__(self, data):
        """
        Initializes the defenses and every scheduled bomb in a wave.

        Raises ValueError for malformed wave data. The app handles that error.

        Parameter data: the decoded contents of a wave file
        Precondition: data is any value returned by GameApp.load_json
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
        self._make_bonus_state()
        self._make_hud()
        self._update_hud()

    def update(self, player_input, dt):
        """
        Advances a wave and checks its win or loss conditions.

        Input is read once per animation frame. Small physics steps keep a
        slow frame from skipping ordinary blasts. Finished rockets are removed
        before movement, leaving their maximum radius visible for one frame.

        Parameter player_input: keyboard information supplied by the app
        Precondition: player_input supports GInput's key query methods

        Parameter dt: seconds since the last animation frame
        Precondition: dt is a finite nonnegative int or float
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

    def draw(self, view):
        """
        Draws the wave without advancing gameplay or consuming input.

        Parameter view: the destination for the graphics
        Precondition: view is the GView supplied by the app
        """
        if self._lost:
            for current_silo in self._silos:
                current_silo.draw(view)
            return
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

    def _check_wave_data(self):
        """Rejects an invalid wave dictionary before creating any models."""
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
        Returns True for a finite int or float, excluding booleans.

        Parameter value: the value being checked
        Precondition: value can be any Python value
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
        Rejects a missile without a legal position, target slot, or time.

        Parameter information: one entry in the missiles list
        Precondition: information can be any decoded JSON value
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
        """Checks optional feature flags while accepting all original waves."""
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
        """Places three silos and six cities in nine permanent target slots."""
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
        """Creates pending bombs without assuming their file order is sorted."""
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
        """Initializes all four extras, leaving them off for original files."""
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
        Moves the reticule with accelerating arrows and clamps all four edges.

        The starter's 0.2 and 10 are nominal-frame speeds. AIM_FRAME_SCALE
        converts them to time-based, usable movement at a nominal 60 fps.

        Parameter player_input: current keyboard information
        Precondition: player_input supports is_key_down
        Parameter dt: elapsed active time
        Precondition: dt is a finite nonnegative number
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
        Returns horizontal direction, vertical direction, and any-arrow status.

        Parameter player_input: current keyboard information
        Precondition: player_input supports is_key_down
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
        """Keeps the entire reticule onscreen and above the silo tops."""
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
        Launches at most one rocket per silo for each new key press.

        Parameter player_input: current keyboard information
        Precondition: player_input supports is_key_pressed
        """
        if player_input.is_key_pressed('1'):
            self._launch_from_silo(0)
        if player_input.is_key_pressed('2'):
            self._launch_from_silo(1)
        if player_input.is_key_pressed('3'):
            self._launch_from_silo(2)

    def _launch_from_silo(self, silo_number):
        """
        Launches toward a snapshot of the target if the silo has ammunition.

        Parameter silo_number: the index of the firing silo
        Precondition: silo_number is 0, 1, or 2
        """
        chosen_silo = self._silos[silo_number]
        previous_ammunition = chosen_silo.getAmmo()
        if previous_ammunition == 0:
            silo_key = str(silo_number + 1)
            self._show_notice('Silo ' + silo_key + ' is empty. Try another.')
            return
        starting_x = chosen_silo.x
        starting_y = chosen_silo.top
        destination_x = self._target.x
        destination_y = self._target.y
        new_rocket = Rocket(starting_x, starting_y,
                            destination_x, destination_y)
        self._rockets.append(new_rocket)
        chosen_silo.setAmmo(previous_ammunition - 1)

    def _remove_finished_rockets(self):
        """Removes rockets that already displayed their full-sized explosion."""
        rocket_position = 0
        while rocket_position < len(self._rockets):
            current_rocket = self._rockets[rocket_position]
            if current_rocket.getFinished():
                del self._rockets[rocket_position]
            else:
                rocket_position = rocket_position + 1

    def _advance_world(self, dt):
        """
        Advances physics in small steps without repeating keyboard presses.

        Parameter dt: active time to simulate
        Precondition: dt is a finite nonnegative number
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
        Moves the world once, resolves damage, and checks completion.

        Parameter step_seconds: time for this small physics step
        Precondition: step_seconds is positive and at most PHYSICS_STEP
        """
        self._elapsed_time = self._elapsed_time + step_seconds
        self._update_bubble_charge(step_seconds)
        self._release_bombs()
        self._resolve_interceptions()
        for current_rocket in self._rockets:
            current_rocket.update(step_seconds)
        self._move_bombs(step_seconds)
        self._resolve_interceptions()
        self._resolve_impacts()
        self._check_finished()

    def _release_bombs(self):
        """Releases every due bomb, even if the pending list is not sorted."""
        pending_position = 0
        while pending_position < len(self._pending_bombs):
            current_bomb = self._pending_bombs[pending_position]
            # adding small time steps can leave a tiny rounding error
            comparison_time = self._elapsed_time + 0.000000001
            if current_bomb.getStartTime() <= comparison_time:
                self._falling_bombs.append(current_bomb)
                del self._pending_bombs[pending_position]
            else:
                pending_position = pending_position + 1

    def _move_bombs(self, step_seconds):
        """
        Moves bombs only for the part of the step after their release.

        Parameter step_seconds: time for this physics step
        Precondition: step_seconds is a finite nonnegative number
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
        """Removes bombs whose centers are inside a rocket explosion."""
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
        Returns whether an exploding rocket contains the bomb's center.

        Parameter current_bomb: the bomb being checked
        Precondition: current_bomb is a Bomb
        """
        bomb_center = (current_bomb.x, current_bomb.y)
        for current_rocket in self._rockets:
            if current_rocket.getExploding():
                if current_rocket.contains(bomb_center):
                    return True
        return False

    def _resolve_impacts(self):
        """Destroys reached targets while preserving the target slot list."""
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
                del self._falling_bombs[bomb_position]
                if self.getCitiesLeft() == 0:
                    self._finish_loss()
                    return
            else:
                bomb_position = bomb_position + 1

    def _check_finished(self):
        """Gives loss priority and waits for future bombs and every rocket."""
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
        """Ends the game immediately and clears everything except the silos."""
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
        Reads optional tools only when the wave explicitly enables them.

        Parameter player_input: current keyboard information
        Precondition: player_input supports GInput's key query methods
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
        """Saves the aim point, replacing the oldest slot after three saves."""
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
        """Cycles saved positions without moving any launched rocket."""
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
        Spends charge while held or gently recharges it when released.

        Parameter step_seconds: real active time for this physics step
        Precondition: step_seconds is positive
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
        Returns ordinary speed, or slowed speed inside a powered bubble.

        The launch clock, rockets, and explosions keep their original timing.
        Only bombs physically inside the custom bubble move more slowly.

        Parameter current_bomb: the bomb whose speed is needed
        Precondition: current_bomb is a Bomb
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
        Records an interception and applies the custom recycling reward.

        Parameter current_bomb: the intercepted bomb, before it is removed
        Precondition: current_bomb is a Bomb
        """
        self._intercepted_count = self._intercepted_count + 1
        if not self._features['recycling']:
            return
        saved_position = (current_bomb.x, current_bomb.y)
        self._constellation_points.append(saved_position)
        if len(self._constellation_points) > 18:
            del self._constellation_points[0]
        # the bad mail gets a second job as a tiny star ✨
        completed_group = self._intercepted_count % RECYCLE_GROUP_SIZE
        if completed_group == 0:
            self._recycle_ammunition()

    def _recycle_ammunition(self):
        """Returns one round to the least-stocked silo, never exceeding ten."""
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
            silo_name = str(chosen_silo_number + 1)
            self._show_notice('Comet compost: +1 rocket returned to silo '
                              + silo_name + '.')
        else:
            self._show_notice('Comet compost: all silos are already full.')

    def _show_notice(self, message):
        """
        Shows short feedback that does not pause or block the game.

        Parameter message: the message to show
        Precondition: message is a string short enough for one display line
        """
        self._notice = message
        self._notice_seconds = 2.8

    def _update_notice(self, dt):
        """
        Expires a feedback message using active time only.

        Parameter dt: elapsed active time
        Precondition: dt is a finite nonnegative number
        """
        self._notice_seconds = self._notice_seconds - dt
        if self._notice_seconds <= 0:
            self._notice_seconds = 0.0
            self._notice = ''

    def _make_hud(self):
        """Creates ordinary controls and the optional instrument labels."""
        panel_color = (0.035, 0.055, 0.10, 0.94)
        self._hud_panel = GRectangle(x=GAME_WIDTH / 2, y=GAME_HEIGHT - 37,
                                    width=GAME_WIDTH, height=74,
                                    fillcolor=panel_color, linewidth=0)
        self._mode_label = self._make_label(self.getModeName(), 170,
                                           GAME_HEIGHT - 24, 23, HUD_MINT)
        self._numbers_label = self._make_label('', GAME_WIDTH - 240,
                                              GAME_HEIGHT - 24, 18, HUD_PAPER)
        self._controls_label = self._make_label('', GAME_WIDTH / 2,
                                               GAME_HEIGHT - 55, 14, HUD_PAPER)
        self._notice_label = self._make_label('', GAME_WIDTH / 2,
                                             GAME_HEIGHT - 121, 17, HUD_AMBER)
        self._make_bubble_meter()
        self._make_slot_labels()
        self._recycling_label = self._make_label('', GAME_WIDTH - 216,
                                                GAME_HEIGHT - 92, 14, HUD_MINT)

    def _make_label(self, text, x, y, size, color):
        """
        Returns a centered label using the supplied readable font.

        Parameter text: the label contents
        Precondition: text is a string
        Parameter x: horizontal center
        Precondition: x is a number
        Parameter y: vertical center
        Precondition: y is a number
        Parameter size: font size
        Precondition: size is a positive number
        Parameter color: text color
        Precondition: color is a game2d color name or RGBA tuple
        """
        new_label = GLabel(text=text, x=x, y=y, font_name=BASIC_FONT,
                           font_size=size, linecolor=color)
        return new_label

    def _make_bubble_meter(self):
        """Creates the custom charge bar, hidden in ordinary waves."""
        meter_y = GAME_HEIGHT - 92
        self._bubble_label = self._make_label('', 130, meter_y, 14, HUD_MINT)
        self._bubble_track = GRectangle(x=330, y=meter_y, width=175, height=5,
                                       fillcolor=(0.75, 0.90, 0.92, 0.22))
        self._bubble_fill = GRectangle(x=330, y=meter_y, width=175, height=5,
                                      fillcolor=HUD_MINT)

    def _make_slot_labels(self):
        """Creates silo key labels and one forecast label per fixed slot."""
        self._slot_labels = []
        for silo_number in range(len(self._silos)):
            silo_x = self._silos[silo_number].x
            key_text = '[' + str(silo_number + 1) + ']'
            key_label = self._make_label(key_text, silo_x, 143, 16, HUD_PAPER)
            self._slot_labels.append(key_label)
        self._weather_labels = []
        for target_object in self._targets:
            label_height = target_object.top + 35
            weather_label = self._make_label('', target_object.x,
                                             label_height, 13, HUD_AMBER)
            self._weather_labels.append(weather_label)
        self._make_bookmark_labels()

    def _make_bookmark_labels(self):
        """Keeps saved-point labels alive so Kivy can finish their textures."""
        self._bookmark_labels = []
        for bookmark_number in range(3):
            label_text = str(bookmark_number + 1)
            bookmark_label = self._make_label(label_text, 0, 0, 13, HUD_MINT)
            self._bookmark_labels.append(bookmark_label)

    def _update_hud(self):
        """Updates readable counts without changing any game rules."""
        total_ammunition = 0
        for current_silo in self._silos:
            total_ammunition = total_ammunition + current_silo.getAmmo()
        remaining_threats = len(self._pending_bombs) + len(self._falling_bombs)
        counter_text = 'CITIES ' + str(self.getCitiesLeft()) + '/6'
        counter_text = counter_text + '    AMMO ' + str(total_ammunition)
        counter_text = counter_text + '    THREATS ' + str(remaining_threats)
        self._numbers_label.text = counter_text
        self._controls_label.text = 'ARROWS aim     1 / 2 / 3 fire     P pause'
        if self._custom_enabled:
            self._controls_label.text = 'ARROWS aim   1 / 2 / 3 fire   P pause'
            extra_controls = self._get_bonus_controls()
            self._controls_label.text += extra_controls
        self._notice_label.text = self._notice
        self._update_bonus_hud()

    def _get_bonus_controls(self):
        """Returns controls only for extras enabled by the current wave."""
        extra_controls = ''
        if self._features['forecast']:
            extra_controls = extra_controls + '   F forecast'
        if self._features['bookmarks']:
            extra_controls += '   B save / TAB recall / X clear'
        if self._features['time_bubble']:
            extra_controls = extra_controls + '   SPACE slow bubble'
        return extra_controls

    def _update_bonus_hud(self):
        """Updates charge, recycling, and city-weather readouts."""
        remaining_tenths = int(self._bubble_seconds * 10) / 10
        self._bubble_label.text = 'BORROWED SKY  ' + str(remaining_tenths) + 's'
        charge_fraction = self._bubble_seconds / BUBBLE_CAPACITY
        filled_width = 175 * charge_fraction
        if filled_width < 0.1:
            filled_width = 0.1
        self._bubble_fill.width = filled_width
        self._bubble_fill.left = self._bubble_track.left
        group_progress = self._intercepted_count % RECYCLE_GROUP_SIZE
        recycling_text = 'COMET COMPOST  ' + str(group_progress) + '/3'
        recycling_text += '    RETURNED ' + str(self._recycled_count)
        self._recycling_label.text = recycling_text
        if self._forecast_visible:
            self._update_weather_reports()

    def _update_weather_reports(self):
        """Shows the soonest active impact estimate above each living target."""
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
        Draws optional guides behind the real threats and defenses.

        Parameter view: the destination for graphics
        Precondition: view is a GView
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
        Draws hollow future heads that never participate in collision checks.

        Forecasts assume the current speed persists for FORECAST_SECONDS.
        Moving the bubble can change the result, so these are estimates.

        Parameter view: the destination for graphics
        Precondition: view is a GView
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
        Draws up to three numbered, noninteractive aiming bookmarks.

        Parameter view: the destination for graphics
        Precondition: view is a GView
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
        Draws the mint slow-time ring, distinct from blue damaging explosions.

        Parameter view: the destination for graphics
        Precondition: view is a GView
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
        Draws a quiet record of interceptions, with no collision behavior.

        Parameter view: the destination for graphics
        Precondition: view is a GView
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
        Draws the original aiming target with a cosmetic contrast outline.

        Parameter view: the destination for graphics
        Precondition: view is a GView
        """
        target_outline = GEllipse(x=self._target.x, y=self._target.y,
                                  width=AIM_WIDTH, height=AIM_HEIGHT,
                                  fillcolor=(0, 0, 0, 0), linewidth=0.8,
                                  linecolor=(1, 1, 1, 0.62))
        target_outline.draw(view)
        self._target.draw(view)

    def _draw_hud(self, view):
        """
        Draws controls, counts, and relevant optional instruments.

        Parameter view: the destination for graphics
        Precondition: view is a GView
        """
        self._hud_panel.draw(view)
        self._mode_label.draw(view)
        self._numbers_label.draw(view)
        self._controls_label.draw(view)
        self._notice_label.draw(view)
        for current_label in self._slot_labels:
            current_label.draw(view)
        if self._features['time_bubble']:
            self._bubble_label.draw(view)
            self._bubble_track.draw(view)
            self._bubble_fill.draw(view)
        if self._features['recycling']:
            self._recycling_label.draw(view)
        if self._forecast_visible:
            for weather_label in self._weather_labels:
                weather_label.draw(view)


# omg this took so long 😭