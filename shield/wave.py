"""
Subcontroller for a single wave of Missile Shield.

The Wave owns the nine places on the ground, the targeting crosshair,
all falling bombs, and all defensive rockets. The main app only tells
this class to update or draw; it does not reach inside the models.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
"""
from game2d import *
from consts import *
from models import *
import introcs
import math


class Wave(object):
    """Manages one complete wave and reports a win or a loss.

    Attribute _data: The dictionary loaded from a wave JSON file.
    Attribute _silos: List of exactly three Silo objects, left to right.
    Attribute _cities: List of still-alive City objects.
    Attribute _ground_targets: Nine starting City/Silo objects in slot order.
    Attribute _target: A Target object for the aiming crosshair.
    Attribute _pending: Bomb objects that have not been released yet.
    Attribute _bombs: List of released Bomb objects still in the air.
    Attribute _rockets: List of live defensive Rocket objects.
    Attribute _lanterns: List of temporary visual MemoryLantern objects.
    Attribute _time: Elapsed wave time in seconds, a number >= 0.
    Attribute _bomb_speed: Speed given by the wave file, a positive number.
    Attribute _finished: Whether the wave has ended, a bool.
    Attribute _won: True if the last bomb is cleared and a city survives.
    Attribute _future_visible: Whether prediction lines are shown, a bool.
    Attribute _contrast_mode: True for a larger, easier-to-see aim ring.
    Attribute _contrast_ring: GEllipse for this optional larger ring.
    Attribute _time_mirror: True for a wave specially permitting slow time.
    Attribute _focus: Amount of slow-time energy remaining, 0..FOCUS_MAX.
    Attribute _focus_active: True while slow time is being used, a bool.
    Attribute _focus_exhausted: Whether Space must be released to recharge.
    Attribute _hud_back: The background GRectangle behind information.
    Attribute _hud_text: The information GLabel at the screen's top.
    Attribute _hint_text: The second line of controls and warnings.
    Attribute _scope: A visual target halo in time-mirror waves.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _data: The dictionary loaded from a wave JSON file.
    # Attribute _silos: List of exactly three Silo objects, left to right.
    # Attribute _cities: List of still-alive City objects.
    # Attribute _ground_targets: Nine starting City/Silo objects in slot order.
    # Attribute _target: A Target object for the aiming crosshair.
    # Attribute _pending: Bomb objects that have not been released yet.
    # Attribute _bombs: List of released Bomb objects still in the air.
    # Attribute _rockets: List of live defensive Rocket objects.
    # Attribute _lanterns: List of temporary visual MemoryLantern objects.
    # Attribute _time: Elapsed wave time in seconds, a number >= 0.
    # Attribute _bomb_speed: Speed given by the wave file, a positive number.
    # Attribute _finished: Whether the wave has ended, a bool.
    # Attribute _won: True if the last bomb is cleared and a city survives.
    # Attribute _future_visible: Whether prediction lines are shown, a bool.
    # Attribute _contrast_mode: True for a larger, easier-to-see aim ring.
    # Attribute _contrast_ring: GEllipse for this optional larger ring.
    # Attribute _time_mirror: True for a wave specially permitting slow time.
    # Attribute _focus: Amount of slow-time energy remaining, 0..FOCUS_MAX.
    # Attribute _focus_active: True while slow time is being used, a bool.
    # Attribute _hud_back: The background GRectangle behind information.
    # Attribute _hud_text: The information GLabel at the screen's top.
    # Attribute _hint_text: The second line of controls and warnings.
    # Attribute _scope: A visual target halo in time-mirror waves.
    # end of invariant notes


    # GETTERS (THIS IS ALL APP.PY NEEDS)
    def isFinished(self):
        """Returns True when this wave has finished in a win or a loss."""
        return self._finished

    def isWon(self):
        """Returns True if at least one city survived the cleared bombs."""
        return self._finished and self._won

    def getCityCount(self):
        """Returns the number of cities still standing."""
        return len(self._cities)

    def getScore(self):
        """Returns the score from surviving cities and unspent ammunition."""
        city_points = len(self._cities) * SCORE_CITY
        remaining_ammunition = 0
        for each_silo in self._silos:
            remaining_ammunition += each_silo.getAmmo()
        remaining_ammo_points = remaining_ammunition * SCORE_AMMO
        return city_points + remaining_ammo_points

    # INITIALIZER
    def __init__(self, data):
        """Creates a wave from the dictionary in a supplied wave JSON file.

        Parameter data: A dictionary with speed and missile data.
        Precondition: data is a valid wave dictionary.
        """
        self._data = data
        self._time = 0.0
        self._bomb_speed = float(data['speed'])
        self._finished = False
        self._won = False
        self._future_visible = False
        self._contrast_mode = False
        self._time_mirror = data.get('time_mirror', False)
        self._focus = FOCUS_MAX
        self._focus_active = False
        self._focus_exhausted = False
        self._silos = []
        self._cities = []
        self._ground_targets = []
        self._pending = []
        self._bombs = []
        self._rockets = []
        self._lanterns = []
        self._target = Target(GAME_WIDTH/2, GAME_HEIGHT/2)
        self._set_up_ground()
        self._set_up_incoming_bombs()
        self._set_up_hud()

    # GAMEPLAY METHODS
    def update(self, controls, dt):
        """Processes the next game frame and reports results through getters.

        Parameter controls: The input object provided by MissileShield.
        Parameter dt: Number of seconds since the previous frame.
        """
        if self._finished:
            return
        self._move_target(controls)
        self._check_prediction_toggle(controls)
        self._fire_rockets(controls)
        world_seconds = self._calculate_world_seconds(controls, dt)
        self._time += world_seconds
        self._release_incoming_bombs()
        self._move_incoming_bombs(world_seconds)
        self._remove_expired_rockets()
        self._move_defensive_rockets(dt)
        self._destroy_bombs_inside_explosions()
        self._check_bombs_hitting_ground()
        self._advance_lanterns(dt)
        self._check_for_finish()
        self._refresh_hud()

    def draw(self, view):
        """Draws the silos, surviving cities, projectiles, and crosshair."""
        if self._finished and not self._won:
            for surviving_silo in self._silos:
                surviving_silo.draw(view)
            return
        for lantern in self._lanterns:
            lantern.draw(view)
        for city in self._cities:
            city.draw(view)
        for silo in self._silos:
            silo.draw(view)
        if self._future_visible:
            self._draw_possible_futures(view)
        for bomb in self._bombs:
            bomb.draw(view)
        for rocket in self._rockets:
            rocket.draw(view)
        if self._time_mirror:
            self._scope.draw(view)
        if self._contrast_mode:
            self._contrast_ring.draw(view)
        self._target.draw(view)
        self._hud_back.draw(view)
        self._hud_text.draw(view)
        self._hint_text.draw(view)

    # HELPERS FOR SETTING UP
    def _set_up_ground(self):
        """Fills nine equally spaced positions with silos or cities."""
        slot_width = GAME_WIDTH / 9.0
        for ground_slot in range(9):
            middle_of_slot = (ground_slot + 0.5) * slot_width
            if ground_slot == 0 or ground_slot == 4 or ground_slot == 8:
                new_silo = Silo(middle_of_slot)
                self._silos.append(new_silo)
                self._ground_targets.append(new_silo)
            else:
                new_city = City(middle_of_slot)
                self._cities.append(new_city)
                self._ground_targets.append(new_city)

    def _set_up_incoming_bombs(self):
        """Makes the bombs waiting for their release times."""
        incoming_specs = self._data['missiles']
        for bomb_specification in incoming_specs:
            starting_x = bomb_specification['x']
            target_slot = bomb_specification['target']
            scheduled_time = bomb_specification['time']
            target_object = self._ground_targets[target_slot]
            new_bomb = Bomb(starting_x, target_object, target_slot,
                            scheduled_time)
            self._pending.append(new_bomb)

    def _set_up_hud(self):
        """Creates the quiet strip of information above the game field."""
        self._hud_back = GRectangle(x=GAME_WIDTH/2, y=GAME_HEIGHT-35,
                                    width=GAME_WIDTH, height=70,
                                    fillcolor=introcs.RGB(22,14,43,205),
                                    linecolor=None)
        self._hud_text = GLabel(text='', x=GAME_WIDTH/2, y=GAME_HEIGHT-20,
                                font_size=20, font_name=BASIC_FONT,
                                linecolor=introcs.RGB(255,245,220))
        self._hint_text = GLabel(text='', x=GAME_WIDTH/2, y=GAME_HEIGHT-52,
                                 font_size=15, font_name=BASIC_FONT,
                                 linecolor=introcs.RGB(158,216,246))
        self._scope = GEllipse(x=self._target.x,y=self._target.y,
                               width=50,height=50,fillcolor=None,
                               linecolor=introcs.RGB(123,205,255,140),
                               linewidth=2)
        self._contrast_ring = GEllipse(x=self._target.x,y=self._target.y,
                                       width=76,height=76,fillcolor=None,
                                       linecolor=introcs.RGB(255,239,132,240),
                                       linewidth=4)
        self._refresh_hud()

    # HELPERS FOR TARGETING
    def _move_target(self, controls):
        """Moves the crosshair, accelerating but staying on screen."""
        horizontal_direction = 0
        vertical_direction = 0
        if controls.is_key_down('left'):
            horizontal_direction -= 1
        if controls.is_key_down('right'):
            horizontal_direction += 1
        if controls.is_key_down('down'):
            vertical_direction -= 1
        if controls.is_key_down('up'):
            vertical_direction += 1
        self._adjust_aim_speed(horizontal_direction, vertical_direction)
        self._apply_aim_movement(horizontal_direction, vertical_direction)

    def _adjust_aim_speed(self, horizontal_direction, vertical_direction):
        """Accelerates while any direction is held; resets upon release."""
        if horizontal_direction == 0 and vertical_direction == 0:
            self._target.setSpeed(0)
        else:
            next_speed = self._target.getSpeed() + AIM_SPEED_STEP
            self._target.setSpeed(next_speed)

    def _apply_aim_movement(self, horizontal_direction, vertical_direction):
        """Keeps every pixel of the target above silos and inside the window."""
        current_speed = self._target.getSpeed()
        new_x = self._target.x + horizontal_direction * current_speed
        new_y = self._target.y + vertical_direction * current_speed
        left_limit = AIM_WIDTH / 2
        right_limit = GAME_WIDTH - AIM_WIDTH / 2
        bottom_limit = SILO_HEIGHT + AIM_HEIGHT / 2
        top_limit = GAME_HEIGHT - 70 - AIM_HEIGHT / 2
        self._target.x = max(left_limit,min(right_limit,new_x))
        self._target.y = max(bottom_limit,min(top_limit,new_y))
        self._scope.x = self._target.x
        self._scope.y = self._target.y
        self._contrast_ring.x = self._target.x
        self._contrast_ring.y = self._target.y

    def _check_prediction_toggle(self, controls):
        """V toggles harmless visual forecasts without affecting gameplay."""
        if controls.is_key_pressed('v'):
            self._future_visible = not self._future_visible
        if controls.is_key_pressed('c'):
            self._contrast_mode = not self._contrast_mode

    # HELPERS FOR ROCKETS
    def _fire_rockets(self, controls):
        """Checks fire buttons 1, 2, 3 and launches from the matching silo."""
        for silo_number in range(3):
            corresponding_key = str(silo_number + 1)
            if controls.is_key_pressed(corresponding_key):
                chosen_silo = self._silos[silo_number]
                if chosen_silo.getAmmo() > 0:
                    self._launch_from_silo(chosen_silo)

    def _launch_from_silo(self, chosen_silo):
        """Spends one rocket and saves its target at launch time."""
        starting_x = chosen_silo.x
        starting_y = chosen_silo.top
        aimed_x = self._target.x
        aimed_y = self._target.y
        new_rocket = Rocket(starting_x, starting_y, aimed_x, aimed_y)
        self._rockets.append(new_rocket)
        ammunition_left = chosen_silo.getAmmo() - 1
        chosen_silo.setAmmo(ammunition_left)

    def _remove_expired_rockets(self):
        """Deletes explosions that already spent a frame at maximum radius."""
        rocket_index = 0
        while rocket_index < len(self._rockets):
            current_rocket = self._rockets[rocket_index]
            if current_rocket.isFinished():
                del self._rockets[rocket_index]
            else:
                rocket_index += 1

    def _move_defensive_rockets(self, dt):
        """Moves flying rockets and grows existing explosions."""
        for rocket in self._rockets:
            rocket.advance(dt)

    # HELPERS FOR BOMBS
    def _release_incoming_bombs(self):
        """Moves scheduled missiles from pending into the falling list."""
        waiting_bomb_number = 0
        while waiting_bomb_number < len(self._pending):
            waiting_bomb = self._pending[waiting_bomb_number]
            if waiting_bomb.getDropTime() <= self._time:
                waiting_bomb.activate()
                self._bombs.append(waiting_bomb)
                del self._pending[waiting_bomb_number]
            else:
                waiting_bomb_number += 1

    def _move_incoming_bombs(self, dt):
        """Moves only bombs which have already started falling."""
        for falling_bomb in self._bombs:
            falling_bomb.advance(dt, self._bomb_speed)

    def _destroy_bombs_inside_explosions(self):
        """Deletes bombs whose centers are inside any defensive explosion."""
        for falling_bomb in self._bombs[:]:
            for rocket in self._rockets:
                if rocket.isExploding():
                    bomb_center = (falling_bomb.x, falling_bomb.y)
                    inside_blast = rocket.contains(bomb_center)
                    if inside_blast:
                        self._bombs.remove(falling_bomb)
                        break

    def _check_bombs_hitting_ground(self):
        """Damages each bomb's original destination after reaching its top."""
        for falling_bomb in self._bombs[:]:
            if falling_bomb.hasArrived():
                target_number = falling_bomb.getTargetSlot()
                damaged_object = self._ground_targets[target_number]
                self._damage_ground_object(damaged_object)
                self._bombs.remove(falling_bomb)

    def _damage_ground_object(self, damaged_object):
        """Removes a city, or empties the ammunition of a silo."""
        if isinstance(damaged_object, Silo):
            damaged_object.setAmmo(0)
        elif isinstance(damaged_object, City):
            if damaged_object in self._cities:
                # ugh the skyline is getting sad 😭
                self._cities.remove(damaged_object)
                self._lanterns.append(MemoryLantern(
                    damaged_object.x, damaged_object.y))

    def _advance_lanterns(self, dt):
        """Expands each harmless fading memory ring and removes old rings."""
        for lantern in self._lanterns[:]:
            lantern.advance(dt)
            if lantern.isFinished():
                self._lanterns.remove(lantern)

    # HELPERS FOR THE GAME'S END
    def _check_for_finish(self):
        """Loses with no cities; wins when all threats disappear."""
        if len(self._cities) == 0:
            self._finished = True
            self._won = False
            self._bombs = []
            self._pending = []
            self._rockets = []
            self._lanterns = []
        elif len(self._bombs) == 0 and len(self._pending) == 0:
            if len(self._rockets) == 0:
                self._finished = True
                self._won = True

    # OPTIONAL FEATURE 1: BORROWED SECONDS (ONLY CUSTOM JSON FILES)
    def _calculate_world_seconds(self, controls, dt):
        """Temporarily slows falling bombs in waves with time_mirror enabled."""
        self._focus_active = False
        if self._time_mirror:
            using_spacebar = controls.is_key_down('spacebar')
            using_space_key = controls.is_key_down('space')
            holding_space = using_spacebar or using_space_key
            if holding_space and not self._focus_exhausted:
                if self._focus > 0:
                    self._focus_active = True
                    self._focus = max(0,self._focus-dt)
                    if self._focus == 0:
                        self._focus_exhausted = True
                    return dt * FOCUS_SLOW_FACTOR
            if not holding_space:
                self._focus_exhausted = False
                self._focus = min(FOCUS_MAX,self._focus+FOCUS_RECHARGE*dt)
        return dt

    # OPTIONAL FEATURE 2: SEE TOMORROW (VISUAL, DOES NOT CHANGE GAMEPLAY)
    def _draw_possible_futures(self, view):
        """Draws thin translucent lines to the original target of each bomb."""
        for falling_bomb in self._bombs:
            landing_x, landing_y = falling_bomb.getDestination()
            future_line = GPath(points=[falling_bomb.x,falling_bomb.y,
                                        landing_x,landing_y],
                                linecolor=introcs.RGB(255,218,137,85),
                                linewidth=1.3)
            future_line.draw(view)

    def _closest_threat(self):
        """Returns the target slot and ETA of the next expected impact."""
        smallest_eta = None
        next_target_number = None
        for falling_bomb in self._bombs + self._pending:
            target_x, target_y = falling_bomb.getDestination()
            horizontal_gap = target_x - falling_bomb.x
            vertical_gap = target_y - falling_bomb.y
            distance_left = math.sqrt(horizontal_gap**2 + vertical_gap**2)
            estimated_seconds = distance_left / self._bomb_speed
            if not falling_bomb.isActive():
                seconds_until_release = falling_bomb.getDropTime()-self._time
                estimated_seconds += max(0, seconds_until_release)
            if smallest_eta is None or estimated_seconds < smallest_eta:
                smallest_eta = estimated_seconds
                next_target_number = falling_bomb.getTargetSlot()
        return (next_target_number, smallest_eta)

    def _refresh_hud(self):
        """Makes the two HUD lines reflect ammunition and the next danger."""
        remaining_ammo = 0
        for silo in self._silos:
            remaining_ammo += silo.getAmmo()
        minutes = int(self._time) // 60
        seconds = int(self._time) % 60
        clock = str(minutes).zfill(2) + ':' + str(seconds).zfill(2)
        headline = ('TIME '+clock+'   /   CITIES '+str(len(self._cities))+
                    '/6   /   ROCKETS '+str(remaining_ammo))
        self._hud_text.text = headline
        self._update_hud_hint()

    def _update_hud_hint(self):
        """Shows simple controls, forecast, and optional time-lens charge."""
        threat_slot, seconds_left = self._closest_threat()
        guidance = 'ARROWS aim | 1 2 3 fire | P pause | V futures | C beacon'
        if self._future_visible and seconds_left is not None:
            guidance = ('NEXT IMPACT: slot '+str(threat_slot+1)+
                        ' in '+str(round(seconds_left,1))+'s   |   V hide')
        if self._time_mirror:
            focus_percent = round(100*self._focus/FOCUS_MAX)
            guidance += '   |   SPACE borrow time '+str(focus_percent)+'%'
        self._hint_text.text = guidance


# omg this took so long 😭