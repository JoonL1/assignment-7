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
from game2d import GRectangle, GEllipse, GPath, GLabel, GImage
from consts import *
from models import Silo, City, Target, Bomb, Rocket
from models import SoundEffects, SplinterBomb, SkyCourier


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
    # _data: validated wave dictionary with speed and missiles keys
    # _bomb_speed: finite positive bomb speed in pixels per second
    # _silos: three Silo objects in left-to-right order
    # _cities: six City objects; destroyed cities remain in the list
    # _targets: nine fixed City/Silo objects, ordered from left to right
    # _target: Target object that stays onscreen and above silo tops
    # _pending_bombs: list of Bomb objects waiting for scheduled drops
    # _falling_bombs: list of Bomb objects released and not yet removed
    # _rockets: list of Rocket objects still flying or exploding
    # _elapsed_time: active game seconds so far and always >= 0
    # _lost: bool that becomes True when the last city is destroyed
    # _won: bool set when no threats or rockets remain and a city is alive
    # _features: dictionary with a bool for each of four bonus tools
    # _custom_enabled: bool that is True if any bonus tool is enabled
    # _forecast_visible: bool that controls whether forecast rings show
    # _bookmarks: at most three saved aim positions inside the bounds
    # _next_bookmark: int index (0 to len(_bookmarks)) for next recall
    # _replacement_bookmark: index (0 to 2) of the next bookmark to replace
    # _bubble_seconds: charge in seconds from 0 to BUBBLE_CAPACITY
    # _bubble_requested: bool; True while Space is held for slow field
    # _bubble_fraction: number from 0 to 1 for step with charge
    # _intercepted_count: bombs stopped so far and always >= 0
    # _recycled_count: nonnegative int counting rockets returned to silos
    # _constellation_points: at most 18 positions of intercepted bombs
    # _notice: a short feedback string (or just an empty string)
    # _notice_seconds: nonnegative seconds before feedback disappears
    # _sounds: one SoundEffects object using the current sound setting
    # _hud_panel: GRectangle forming the center of the top status bar
    # _hud_rules: three skinny GRectangles between the main counters
    # _mode_label: GLabel showing the wave mode or round number
    # _metric_labels: three GLabels for cities, ammunition, and threats
    # _metric_titles: three GLabels naming those counts in that same order
    # _controls_label: a GLabel with the aim/fire keys shared by both modes
    # _audio_label: a GLabel with the sound setting or unavailable message
    # _tool_centers: dict mapping enabled tool names to x positions
    # _tool_panels: list of shapes making the rounded bonus cards
    # _tool_labels: dict mapping enabled tool names to value GLabels
    # _tool_hint_labels: dict mapping enabled tool names to help GLabels
    # _notice_parts: six shapes that make a rounded notice card
    # _notice_pulse: nonnegative seconds left in feedback text animation
    # _notice_label: the GLabel for quick feedback below the status cards
    # _bubble_track: the GRectangle under the slow field charge bar
    # _bubble_fill: a GRectangle that stays inside the charge bar track
    # _slot_labels: list of three GLabels showing silo firing keys
    # _bookmark_labels: three GLabels reused as numbers for saved aim spots
    # _weather_labels: list of nine GLabels with estimated impact times
    # _surviving_slots: None or list of saved city slot numbers
    # _split_flash: list of [x, y, seconds left] for each split effect
    # _signal_echoes: list of up to 12 fading hit-to-city effects
    # _flyers: list of custom SkyCourier aircraft that can drop bombs
    # _hud_parts: rounded pieces making one dark top status card
    # _metric_previous: list of last city, ammo, and threat label texts
    # _metric_pulses: list of three nonnegative count animation timers
    # _metric_icons: list of three GImages for city, ammo, threat counts

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLost(self):
        """
        returns True if all six city objects are destroyed
        """
        did_we_lose = self._lost
        return did_we_lose

    def getWon(self):
        """
        returns True when all bombs, aircraft, and rockets are gone
        and at least one city is still alive
        """
        did_we_win = self._won
        return did_we_win

    def getCustomEnabled(self):
        """
        returns True if the current json enables at least one extra tool
        """
        has_extra_tools = self._custom_enabled
        return has_extra_tools

    def getModeName(self):
        """
        returns the lowercase mode name for the status bar
        """
        if 'round_number' in self._data:
            return 'round ' + str(self._data['round_number'])
        if self._custom_enabled:
            return 'night post'
        return 'classic'

    def getHelpRows(self):
        """
        returns a new list of keyboard instructions for enabled bonus tools
        the list includes only tools enabled in the current wave
        the pause screen calls this method instead of directly accessing
        Wave's hidden _features dictionary
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
        """
        returns the number of living cities (an int from 0 through 6)
        """
        living_city_count = 0
        for current_city in self._cities:
            if current_city.getAlive():
                living_city_count = living_city_count + 1
        return living_city_count

    def getAmmoCounts(self):
        """
        returns a new list of remaining rocket counts for the three silos
        the order is left, center, then right
        """
        remaining_ammunition = []
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition.append(current_amount)
        return remaining_ammunition

    def getScore(self):
        """
        returns 5 points for each unused silo rocket and 100 points for
        each surviving city
        """
        remaining_ammunition = 0
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition = remaining_ammunition + current_amount
        ammunition_score = remaining_ammunition * SCORE_AMMO
        surviving_city_score = self.getCitiesLeft() * SCORE_CITY
        total_score = ammunition_score + surviving_city_score
        return total_score

    def getSoundsEnabled(self):
        """
        returns True if sound is unmuted (even if a device is missing)
        """
        can_the_sounds_play = self._sounds.getEnabled()
        return can_the_sounds_play

    def getSoundsAvailable(self):
        """
        returns True if the sound bank loaded at least one cue
        """
        did_the_sounds_load = self._sounds.getAvailable()
        return did_the_sounds_load

    def setSoundsEnabled(self, enabled):
        """
        changes the wave mute preference and refreshes the audio label
        parameter enabled: whether future sounds may play
        precondition: enabled is a bool
        """
        self._sounds.setEnabled(enabled)
        self._update_audio_label()

    # INITIALIZER (standard form) TO LAYOUT THE MODELS
    def getSurvivingSlots(self):
        """
        returns a new list of the original slot numbers of cities still alive
        """
        still_here = []
        for position in [1, 2, 3, 5, 6, 7]:
            if self._targets[position].getAlive():
                still_here.append(position)
        return still_here

    def playScoreTick(self, kind=0):
        """
        plays the score sound for one rocket or city being counted
        parameter kind: 0 plays the rocket sound (5 points)
        kind 1 plays the city sound (100 points)
        precondition: kind is 0 or 1
        """
        if kind == 0:
            self._sounds.play('score_rocket')
        else:
            self._sounds.play('score_city')

    def showRoundStart(self):
        """shows the round number for two seconds and pulses the counters

        only runs when the wave data includes a round_number
        does not change the bombs, cities, or rockets
        """
        if 'round_number' not in self._data:
            return
        number = str(self._data['round_number'])
        self._show_notice('round ' + number + ' / protect the cities')
        self._notice_seconds = 2.0
        self._metric_pulses = [0.25, 0.25, 0.25]

    def __init__(self, data, surviving_slots=None):
        """
        checks the wave JSON and creates the defenses and scheduled bombs
        along with any aircraft included in a custom wave

        invalid wave data raises ValueError so the main app can show
        a loading error instead of starting a broken wave
        parameter data: the JSON data for one wave
        precondition: data is any value returned by GameApp.load_json
        parameter surviving_slots: None to start with all six cities
        or a list of city slots that survived the previous round
        """
        self._data = data
        self._surviving_slots = surviving_slots
        self._split_flash = []
        self._signal_echoes = []
        self._check_wave_data()
        self._bomb_speed = data['speed']
        self._elapsed_time = 0.0
        self._lost = False
        self._won = False
        self._notice = ''
        self._notice_seconds = 0.0
        self._make_defenses()
        self._make_bombs()
        self._make_flyers()
        self._rockets = []
        self._sounds = SoundEffects()
        self._make_bonus_state()
        self._make_hud()
        self._update_hud()

    # UPDATE METHOD TO MOVE THE TARGETS, BOMBS, AND ROCKETS
    def update(self, player_input, dt):
        """
        reads one frame of input and advances the game in smaller physics
        steps

        reads keyboard input once, then moves objects in short steps
        to avoid skipping collisions when a frame takes too long
        finished rocket explosions are removed before new movement
        so a full-size explosion remains visible for one frame
        parameter player_input: keyboard information passed in by the app
        precondition: player_input supports the key query methods of GInput
        parameter dt: seconds since the previous update (at least zero)
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
        self._pulse_metrics(dt)
        self._update_hud()

    # DRAW METHOD TO DRAW THE GAME OBJECTS
    def draw(self, view):
        """
        draws the cities, silos, airborne objects, and game interface
        after a loss, only the silos are drawn

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
        self._draw_split_flash(view)
        for current_city in self._cities:
            current_city.draw(view)
        for current_silo in self._silos:
            current_silo.draw(view)
        for current_bomb in self._falling_bombs:
            current_bomb.draw(view)
        for current_flyer in self._flyers:
            current_flyer.draw(view)
        for current_rocket in self._rockets:
            current_rocket.draw(view)
        if not self._won:
            self._draw_hud(view)
            self._draw_aim(view)

    def startSounds(self):
        """
        plays the start cue after a wave is successfully loaded
        """
        self._sounds.play('start')

    def stopSounds(self):
        """
        stops all current sound effects in the game without changing the mute
        setting
        """
        self._sounds.stop()

    def finishSounds(self, player_won):
        """
        stops previous cues and plays the result cue for winning or
        losing
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
        raises ValueError for invalid speed, missiles, or extra feature
        settings
        the JSON calls its bomb list "missiles", not "bombs"
        so a missing missiles key is a loading error
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
        self._check_flyer_data()

    def _is_finite_number(self, value):
        """
        returns True for an integer or a finite floating-point number
        returns False for booleans, infinity, NaN, and other types
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
        checks the starting x, target slot, and drop time of one
        scheduled bomb from the JSON missiles list
        parameter information: one entry from the JSON missiles list
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
        self._check_splinter_data(information)

    def _check_feature_data(self):
        """
        checks that each bonus tool has a recognized name and bool value
        raises ValueError if a feature name is unknown or its value
        is not True or False
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

    def _check_flyer_data(self):
        """checks every custom aircraft and its planned drop orders"""
        if 'flyers' not in self._data:
            return
        if type(self._data['flyers']) != list:
            raise ValueError('flyers must be a list')
        for entry in self._data['flyers']:
            self._check_one_flyer(entry)

    def _check_one_flyer(self, entry):
        """checks the aircraft type, position, speed, start time, and drops

        parameter entry: one aircraft entry from a custom wave JSON
        precondition: entry can be any JSON value
        """
        if type(entry) != dict:
            raise ValueError('each flyer must be a dictionary')
        if entry.get('kind') not in ['plane', 'drone', 'satellite']:
            raise ValueError('flyer kind must be plane drone or satellite')
        for name in ['x', 'y', 'speed', 'start']:
            if not self._is_finite_number(entry.get(name)):
                raise ValueError('flyer ' + name + ' must be a number')
        if entry['start'] < 0 or entry['speed'] == 0:
            raise ValueError('flyer start or speed is not valid')
        if entry['y'] < 170 or entry['y'] > GAME_HEIGHT - 100:
            raise ValueError('flyer height is outside the flight zone')
        self._check_flyer_drops(entry)

    def _check_flyer_drops(self, entry):
        """checks the scheduled bomb drops for one aircraft

        parameter entry: one previously checked aircraft dictionary
        precondition: entry contains a valid start time
        """
        drops = entry.get('drops')
        if type(drops) != list or len(drops) == 0:
            raise ValueError('each flyer needs a nonempty drops list')
        for item in drops:
            if type(item) != dict:
                raise ValueError('each flyer drop must be a dictionary')
            if not self._is_finite_number(item.get('time')):
                raise ValueError('flyer drop time must be a number')
            if item['time'] < entry['start']:
                raise ValueError('flyer drops cannot predate its start')
            if type(item.get('target')) != int:
                raise ValueError('flyer target must be an integer')
            if item['target'] < 0 or item['target'] > 8:
                raise ValueError('flyer target must be from 0 through 8')

    def _make_flyers(self):
        """creates aircraft only when listed in the custom wave JSON"""
        self._flyers = []
        for flyer_data in self._data.get('flyers', []):
            self._flyers.append(SkyCourier(flyer_data))

    def _update_flyers(self, dt):
        """moves aircraft and checks for rocket hits and scheduled drops

        a rocket hit cancels any remaining drops from that aircraft
        parameter dt: seconds in the current physics step
        precondition: dt is positive and no greater than PHYSICS_STEP
        """
        position = 0
        while position < len(self._flyers):
            flyer = self._flyers[position]
            flyer.update(dt, self._elapsed_time)
            if flyer.getActive() and self._flyer_hit(flyer):
                flyer.destroy()
                self._split_flash.append([flyer.x, flyer.y, 0.55])
                # omg it finally got hit 😭
                self._sounds.play('intercept')
            if flyer.getAlive():
                self._drop_from_flyer(flyer)
            if flyer.getFinished():
                del self._flyers[position]
            else:
                position = position + 1

    def _drop_from_flyer(self, flyer):
        """creates bombs for any aircraft drop orders due at this time

        each bomb starts at the aircraft and targets a fixed city or silo
        parameter flyer: an active SkyCourier with scheduled drop orders
        precondition: flyer is a SkyCourier that has started flying
        """
        for order in flyer.takeDueDrops(self._elapsed_time):
            slot = order['target']
            destination = self._targets[slot]
            bomb = Bomb(flyer.x, flyer.y, destination.x,
                        destination.top, self._elapsed_time, slot)
            self._falling_bombs.append(bomb)
            if flyer.getKind() == 'drone':
                self._sounds.play('drone')
            elif flyer.getKind() == 'plane':
                self._sounds.play('plane')
            else:
                self._sounds.play('satellite')

    def _flyer_hit(self, flyer):
        """returns True if a rocket explosion overlaps an aircraft

        checks the aircraft center and four edge points
        parameter flyer: the visible aircraft to check for a hit
        precondition: flyer is a SkyCourier that is visible in the game
        """
        spots = [(flyer.x, flyer.y), (flyer.left, flyer.y),
                 (flyer.right, flyer.y), (flyer.x, flyer.top),
                 (flyer.x, flyer.bottom)]
        for rocket in self._rockets:
            if rocket.getExploding():
                for point in spots:
                    if rocket.contains(point):
                        return True
        return False

    def _make_defenses(self):
        """
        creates three silos and six city objects in their respective slots
        cities not in _surviving_slots start destroyed in later rounds
        """
        self._silos = []
        self._cities = []
        self._targets = []
        slot_width = GAME_WIDTH / 9
        for slot_number in range(9):
            center = slot_number * slot_width + slot_width / 2
            if slot_number in [0, 4, 8]:
                new_defense = Silo(center)
                self._silos.append(new_defense)
            else:
                new_defense = City(center)
                if self._surviving_slots is not None:
                    if slot_number not in self._surviving_slots:
                        new_defense.destroy()
                self._cities.append(new_defense)
            self._targets.append(new_defense)
        self._target = Target(GAME_WIDTH / 2, GAME_HEIGHT / 2)

    def _make_bombs(self):
        """
        creates bombs from the JSON missiles list and schedules their drops
        """
        self._pending_bombs = []
        self._falling_bombs = []
        for information in self._data['missiles']:
            target_slot = information['target']
            target_object = self._targets[target_slot]
            arguments = [information['x'], GAME_HEIGHT,
                         target_object.x, target_object.top,
                         information['time'], target_slot]
            if 'split_y' in information:
                new_bomb = SplinterBomb(*arguments, information['split_y'],
                                        information['children'])
            else:
                new_bomb = Bomb(*arguments)
            self._pending_bombs.append(new_bomb)

    def _make_bonus_state(self):
        """
        initializes four optional feature flags and their counters
        """
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
        moves the aim target using arrow keys and keeps it on the screen
        the target cannot move below the top of the silos
        AIM_SPEED_STEP and AIM_SPEED_LIMIT are in frame-based units
        AIM_FRAME_SCALE converts dt into equivalent 60-fps frames
        so movement speed does not depend on the actual frame rate
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
        returns the horizontal and vertical directions of movement and whether
        any arrow key is being held down
        pressing opposite arrows cancels movement in that direction, but
        the last value remains True because arrow keys are still held down
        parameter player_input: the current keyboard input
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
        what_i_got = (horizontal_direction, vertical_direction, arrows_are_down)
        return what_i_got

    def _keep_target_inside(self):
        """
        keeps all four edges of the aim marker inside the screen above the
        silos
        """
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
        fires one rocket for each new press of 1, 2, or 3
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
        fires one rocket from the chosen silo and uses one of its ammo
        the rocket keeps the aim position recorded when it was fired
        moving the aim target later does not change its destination
        parameter silo_number: index of the silo to fire (0, 1, or 2)
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
        """
        removes rocket explosions that reached maximum size last frame
        """
        rocket_position = 0
        while rocket_position < len(self._rockets):
            current_rocket = self._rockets[rocket_position]
            if current_rocket.getFinished():
                del self._rockets[rocket_position]
            else:
                rocket_position = rocket_position + 1

    def _advance_world(self, dt):
        """
        advances the wave in small steps until dt passes or the game ends
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
        advances time, moves aircraft and projectiles, and checks collisions
        parameter step_seconds: time for this small movement step
        precondition: step_seconds is positive and at most PHYSICS_STEP
        """
        self._elapsed_time = self._elapsed_time + step_seconds
        self._update_split_flash(step_seconds)
        self._update_signal_echoes(step_seconds)
        self._update_bubble_charge(step_seconds)
        self._release_bombs()
        self._update_flyers(step_seconds)
        self._resolve_interceptions()
        self._move_rockets(step_seconds)
        self._move_bombs(step_seconds)
        self._resolve_interceptions()
        self._split_bombs()
        self._resolve_impacts()
        self._check_finished()

    def _move_rockets(self, step_seconds):
        """
        moves rockets and plays the explosion sound when a rocket first bursts
        rockets that were already exploding do not play the sound again
        each rocket plays this sound only once
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
        """
        moves bombs from the pending list into the falling list when
        their scheduled drop times have passed
        """
        pending_position = 0
        while pending_position < len(self._pending_bombs):
            current_bomb = self._pending_bombs[pending_position]
            
            comparison_time = self._elapsed_time + 0.000000001
            if current_bomb.getStartTime() <= comparison_time:
                self._falling_bombs.append(current_bomb)
                del self._pending_bombs[pending_position]
            else:
                pending_position = pending_position + 1

    def _move_bombs(self, step_seconds):
        """
        moves each released bomb only for time after its scheduled drop
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
        """
        removes bombs caught inside a rocket's growing explosion
        """
        # ugh why do these bombs keep coming back 😭
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
        returns True if any exploding rocket contains the bomb center
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
        """
        sets a silo's ammunition to zero or destroys a city on impact
        the target's original slot number does not change
        """
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
        loses immediately if all cities are destroyed
        wins when no bombs, aircraft, or rockets remain
        bombs waiting for their drop times also prevent a win
        at least one city must still be alive
        """
        if self.getCitiesLeft() == 0:
            self._finish_loss()
            return
        if len(self._pending_bombs) != 0:
            return
        if len(self._falling_bombs) != 0:
            return
        if len(self._flyers) != 0:
            return
        if len(self._rockets) != 0:
            return
        self._won = True
        self._bubble_fraction = 0.0

    def _finish_loss(self):
        """
        marks the wave as lost and removes all airborne threats, rockets,
        and optional aiming effects
        """
        self._lost = True
        self._won = False
        self._pending_bombs = []
        self._falling_bombs = []
        self._rockets = []
        self._flyers = []
        self._bookmarks = []
        self._next_bookmark = 0
        self._constellation_points = []
        self._split_flash = []
        self._signal_echoes = []
        self._bubble_fraction = 0.0
        self._bubble_requested = False

    def _read_bonus_keys(self, player_input):
        """
        reads the optional control keys only when their features are enabled
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
        """
        saves the aim position and stores up to three bookmarks
        after three saves, each new bookmark replaces an older one
        """
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
        moves the aim marker to the next saved location (not any flying
        rockets)
        only the reticule moves; rockets in flight keep their original
        saved destinations
        """
        
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
        uses slow-field charge while Space is held and refills after release
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
        returns the speed for this bomb during the current step
        bombs inside an active slow field can move at 22% of normal speed
        bombs outside the field always move at the wave's normal speed
        the field does not change rocket movement or scheduled drop times
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
        records an intercepted bomb and updates any enabled bonus effects
        parameter current_bomb: the Bomb intercepted by a rocket blast
        precondition: current_bomb is a Bomb
        """
        self._sounds.play('intercept')
        self._intercepted_count = self._intercepted_count + 1
        if self._custom_enabled:
            self._save_signal_echo(current_bomb)
        if not self._features['recycling']:
            return
        saved_position = (current_bomb.x, current_bomb.y)
        self._constellation_points.append(saved_position)
        if len(self._constellation_points) > 18:
            del self._constellation_points[0]
        
        completed_group = self._intercepted_count % RECYCLE_GROUP_SIZE
        if completed_group == 0:
            self._recycle_ammunition()

    def _recycle_ammunition(self):
        """
        returns one rocket to the silo with the fewest rockets left
        the silo cannot exceed its starting ammunition limit
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
        shows a lowercase feedback message for 2.8 seconds of active play
        parameter message: the feedback to show
        precondition: message is a string that fits on one display line
        """
        self._notice = message.lower()
        self._notice_seconds = 2.8
        self._notice_pulse = 0.25

    def _update_notice(self, dt):
        """
        subtracts elapsed play time from the notice timer and clears expired
        text
        parameter dt: seconds of active gameplay that have passed
        precondition: dt is a finite nonnegative number
        """
        self._notice_seconds = self._notice_seconds - dt
        if self._notice_seconds <= 0:
            self._notice_seconds = 0.0
            self._notice = ''

    def _rounded_parts(self, x, y, width, height, radius, color):
        """returns six shapes that form a rectangle with rounded corners

        parameter x: horizontal center in pixels
        parameter y: vertical center in pixels
        parameter width: positive total width
        parameter height: positive total height
        parameter radius: positive corner radius
        parameter color: one valid game2d color
        """
        parts = [GRectangle(x=x, y=y, width=width-2*radius,
                            height=height, fillcolor=color),
                 GRectangle(x=x, y=y, width=width,
                            height=height-2*radius, fillcolor=color)]
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                px = x + dx * (width / 2 - radius)
                py = y + dy * (height / 2 - radius)
                parts.append(GEllipse(x=px, y=py, width=2*radius,
                                      height=2*radius, fillcolor=color))
        return parts

    def _make_hud(self):
        """
        creates the main status bar and optional bonus tool panels
        for the current wave
        """
        self._hud_parts = self._rounded_parts(GAME_WIDTH / 2, 804,
                                               GAME_WIDTH - 48, 100, 18, UI_SURFACE)
        self._hud_panel = self._hud_parts[0]
        self._mode_label = self._make_label(self.getModeName(), 56,
                                           817, 22, UI_TEXT)
        self._mode_label.font_name = THEME_FONT
        self._mode_label.left = 56
        controls = 'arrows aim   1 / 2 / 3 fire   p pause'
        self._controls_label = self._make_label(controls, 56,
                                               789, 12, UI_MUTED)
        self._controls_label.left = 56
        self._audio_label = self._make_label('', 451, 789, 12, UI_ACCENT)
        self._make_metric_labels()
        self._make_tool_cards()
        self._make_bubble_meter()
        self._make_notice_label()
        self._make_slot_labels()

    def _make_label(self, text, x, y, size, color):
        """
        returns a lowercase GLabel using BASIC_FONT
        parameter text: the text to display in the label
        parameter x: horizontal center and must be a number
        parameter y: vertical center and must be a number
        parameter size: font size and must be a positive number
        parameter color: text color and must be a valid game2d color
        precondition: y is a number
        """
        new_label = GLabel(text=text.lower(), x=x, y=y,
                           font_name=BASIC_FONT, font_size=size,
                           linecolor=color)
        return new_label

    def _make_metric_labels(self):
        """
        creates labels for living cities, remaining ammo, and threats
        """
        self._metric_labels = []
        self._metric_titles = []
        self._metric_icons = []
        self._hud_rules = []
        self._metric_previous = ['', '', '']
        self._metric_pulses = [0.16, 0.16, 0.16]
        metric_names = ['cities', 'ammo', 'incoming']
        for metric_number in range(3):
            metric_x = 658 + 172 * metric_number
            value_label = self._make_label('', metric_x, 816, 26, UI_TEXT)
            value_label.font_name = THEME_FONT
            self._metric_labels.append(value_label)
            icon_files = ['city@2x.png', 'missile-small@2x.png',
                          'target@2x.png']
            icon = GImage(source=icon_files[metric_number],
                          x=metric_x - 54, y=791, width=20, height=20)
            self._metric_icons.append(icon)
            metric_name = metric_names[metric_number]
            title_label = self._make_label(metric_name, metric_x,
                                           791, 11, UI_MUTED)
            self._metric_titles.append(title_label)
            rule = GRectangle(x=metric_x - 86, y=804, width=1, height=49,
                              fillcolor=UI_BORDER)
            self._hud_rules.append(rule)

    def _make_tool_cards(self):
        """
        creates a card for each enabled bonus tool in this wave
        """
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
        creates one value label and one key hint for an enabled bonus feature
        parameter tool_name: the name of the enabled bonus feature
        precondition: tool_name is an enabled key in _features
        parameter center_x: the horizontal center and must be a number
        parameter width: the card width and must be a positive number
        """
        panels = self._rounded_parts(center_x, 714, width, 66, 14, UI_SURFACE_SOFT)
        for panel in panels:
            self._tool_panels.append(panel)
        label = self._make_label('', center_x, 729, 16, UI_ACCENT)
        self._tool_labels[tool_name] = label
        hint = self._make_label('', center_x, 699, 11, UI_MUTED)
        self._tool_hint_labels[tool_name] = hint

    def _make_notice_label(self):
        """
        prepares the feedback label and card below the main status bar
        """
        notice_y = 723
        if self._custom_enabled:
            notice_y = 645
        self._notice_parts = self._rounded_parts(GAME_WIDTH / 2,
                                                  notice_y, 610, 36, 12, UI_SURFACE)
        self._notice_label = self._make_label('', GAME_WIDTH / 2,
                                             notice_y, 14, UI_AMBER)
        self._notice_pulse = 0

    def _make_bubble_meter(self):
        """
        creates the charge meter used by the slow-field bonus tool
        the meter is drawn only when that feature is enabled
        """
        center_x = GAME_WIDTH / 2
        if self._features['time_bubble']:
            center_x = self._tool_centers['time_bubble']
            self._tool_hint_labels['time_bubble'].x = center_x - 67
        self._bubble_track = GRectangle(x=center_x + 26, y=699,
                                        width=96, height=3,
                                        fillcolor=UI_BORDER)
        self._bubble_fill = GRectangle(x=center_x + 26, y=699,
                                       width=96, height=3,
                                       fillcolor=UI_ACCENT)

    def _make_slot_labels(self):
        """
        creates silo firing-key labels and estimated impact-time labels
        one impact-time label is stored for each of the nine target slots
        """
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
        creates three reusable number labels for saved aim markers
        """
        self._bookmark_labels = []
        for bookmark_number in range(3):
            label_text = str(bookmark_number + 1)
            bookmark_label = self._make_label(label_text, 0, 0, 13, HUD_MINT)
            self._bookmark_labels.append(bookmark_label)

    def _update_hud(self):
        """
        updates the city, ammunition, and threat counts in the top bar
        """
        total_ammunition = 0
        for current_silo in self._silos:
            total_ammunition = total_ammunition + current_silo.getAmmo()
        remaining_threats = len(self._pending_bombs) + len(self._falling_bombs)
        remaining_threats = remaining_threats + len(self._flyers)
        words = [str(self.getCitiesLeft()) + ' / 6',
                 str(total_ammunition), str(remaining_threats)]
        for pos in range(3):
            if self._metric_previous[pos] != words[pos]:
                if self._metric_previous[pos] != '':
                    self._metric_pulses[pos] = 0.23
                self._metric_previous[pos] = words[pos]
            self._metric_labels[pos].text = words[pos]
        self._notice_label.text = self._notice.lower()
        self._update_audio_label()
        self._update_bonus_hud()

    def _pulse_metrics(self, dt):
        """shrinks a count back to normal size after the value changes

        parameter dt: seconds since the previous frame (at least zero)
        precondition: dt is a finite number greater than or equal to zero
        """
        for pos in range(3):
            time_left = self._metric_pulses[pos] - dt
            if time_left < 0:
                time_left = 0
            self._metric_pulses[pos] = time_left
            size = 26 + int(time_left * 35)
            self._metric_labels[pos].font_size = size
        self._notice_pulse = max(0, self._notice_pulse - dt)
        self._notice_label.font_size = 14 + int(self._notice_pulse * 14)

    def _update_audio_label(self):
        """
        shows the mute setting or reports if sound effects are unavailable
        """
        words = 'v sound on'
        if not self._sounds.getAvailable():
            words = 'audio unavailable'
        elif not self._sounds.getEnabled():
            words = 'v sound off'
        self._controls_label.text = (
            'arrows aim   1 / 2 / 3 fire   p pause   ' + words)
        self._audio_label.text = ''

    def _update_bonus_hud(self):
        """
        updates the text on only the optional tools switched on in this wave
        """
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
        """
        sets the slow field charge fill to the remaining fraction
        """
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
        shows the number of interceptions toward the next ammo refund
        """
        group_progress = self._intercepted_count % RECYCLE_GROUP_SIZE
        recycling_text = 'recycle ' + str(group_progress) + ' / 3'
        self._tool_labels['recycling'].text = recycling_text
        refund_text = '+' + str(self._recycled_count) + ' ammo returned'
        self._tool_hint_labels['recycling'].text = refund_text

    def _update_weather_reports(self):
        """
        shows the shortest estimated time until a bomb hits each target slot
        """
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
        draws only the optional aiming guides enabled for this wave
        parameter view: the place to draw the guides
        precondition: view is a GView
        """
        if not self._custom_enabled:
            return
        self._draw_constellations(view)
        self._draw_signal_echoes(view)
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
        draws a ring where each falling bomb may be in 1.5 seconds
        the estimate assumes the bomb keeps moving at its current speed
        moving the slow field can change that speed later
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
        draws numbered circles at up to three saved aim positions

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
        draws a mint circle around the aim target while bombs are slowed

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
        draws small points at recent bomb interception positions
        and lines connecting those points
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
        draws the original target marker and a contrasting outline

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
        draws values and control hints on the front of the playfield

        parameter view: the place to draw the displays
        precondition: view is a GView
        """
        self._mode_label.draw(view)
        self._controls_label.draw(view)
        self._audio_label.draw(view)
        for icon in self._metric_icons:
            icon.draw(view)
        for current_label in self._metric_labels:
            current_label.draw(view)
        for current_label in self._metric_titles:
            current_label.draw(view)
        self._draw_tool_labels(view)
        for current_label in self._slot_labels:
            current_label.draw(view)
        if self._notice != '':
            for piece in self._notice_parts:
                piece.draw(view)
            self._notice_label.draw(view)
        if self._forecast_visible:
            for weather_label in self._weather_labels:
                weather_label.draw(view)

    def _draw_hud_surfaces(self, view):
        """
        draws the dark backgrounds behind status bar labels

        parameter view: the place to draw the surfaces
        precondition: view is a GView
        """
        for piece in self._hud_parts:
            piece.draw(view)
        for current_rule in self._hud_rules:
            current_rule.draw(view)
        for current_panel in self._tool_panels:
            current_panel.draw(view)

    def _draw_tool_labels(self, view):
        """
        draws each enabled feature label and hint and the optional charge bar

        parameter view: the place to draw the tools
        precondition: view is a GView
        """
        for tool_name in self._tool_labels:
            self._tool_labels[tool_name].draw(view)
            self._tool_hint_labels[tool_name].draw(view)
        if self._features['time_bubble']:
            self._bubble_track.draw(view)
            self._bubble_fill.draw(view)

    def _check_splinter_data(self, information):
        """
        checks that a custom splitting bomb has a valid height and child slots

        parameter information: dictionary describing one scheduled bomb
        precondition: information is a dictionary already checked for x and
        target and time
        both split_y and children must be present together or both absent
        split_y must be at least 150 and below GAME_HEIGHT
        children must contain two or three ints from 0 through 8
        """
        has_height = 'split_y' in information
        has_children = 'children' in information
        if has_height != has_children:
            raise ValueError('a split bomb needs split_y + children')
        if not has_height:
            return
        height = information['split_y']
        if not self._is_finite_number(height):
            raise ValueError('split_y must be a number')
        if height < 150 or height >= GAME_HEIGHT:
            raise ValueError('split_y must be between 150 and window top')
        children = information['children']
        if type(children) != list or len(children) not in [2, 3]:
            raise ValueError('split bombs need two or three targets')
        for slot in children:
            if type(slot) != int or slot < 0 or slot > 8:
                raise ValueError('split target must be a slot from 0 to 8')

    def _split_bombs(self):
        """
        replaces each orange bomb that reached its split height with
        two or three regular bombs

        each new bomb starts where the parent split and uses a target
        from the custom JSON data
        the original bomb is removed after the children are created
        so it cannot split more than once
        """
        position = 0
        while position < len(self._falling_bombs):
            parent = self._falling_bombs[position]
            if isinstance(parent, SplinterBomb) and parent.shouldSplit():
                parent.markSplit()
                for slot in parent.getChildSlots():
                    destination = self._targets[slot]
                    child = Bomb(parent.x, parent.y,
                                 destination.x, destination.top,
                                 self._elapsed_time, slot)
                    self._falling_bombs.append(child)
                self._split_flash.append([parent.x, parent.y, 0.55])
                self._show_notice('split bomb! more targets incoming.')
                del self._falling_bombs[position]
            else:
                position = position + 1

    def _save_signal_echo(self, bomb):
        """
        records a fading gold signal from an intercepted bomb to a living city

        the line ends at the closest surviving city
        parameter bomb: the bomb stopped by an actual rocket blast
        precondition: bomb is a Bomb
        """
        closest = None
        closest_gap = None
        for city in self._cities:
            if city.getAlive():
                gap = abs(city.x - bomb.x)
                if closest_gap is None or gap < closest_gap:
                    closest = city
                    closest_gap = gap
        if closest is not None:
            echo = [bomb.x, bomb.y, closest.x, closest.top, 0.8]
            self._signal_echoes.append(echo)
            if len(self._signal_echoes) > 12:
                del self._signal_echoes[0]

    def _update_signal_echoes(self, dt):
        """
        fades each city signal for 0.8 seconds of active gameplay

        parameter dt: active game time in seconds
        precondition: dt is nonnegative
        """
        position = 0
        while position < len(self._signal_echoes):
            echo = self._signal_echoes[position]
            echo[4] = echo[4] - dt
            if echo[4] <= 0:
                del self._signal_echoes[position]
            else:
                position = position + 1

    def _draw_signal_echoes(self, view):
        """
        draws fading gold lines and rings from hits to living cities

        these glowing paths and rings are decoration and cannot stop bombs
        parameter view: the GView that draws the current wave
        precondition: view is a GView
        """
        for x, y, city_x, city_y, seconds_left in self._signal_echoes:
            ring_size = 18 + (0.8 - seconds_left) * 145
            fade = seconds_left / 0.8
            gold = (0.98, 0.80, 0.43, fade * 0.48)
            route = GPath(points=[x, y, city_x, city_y],
                          linewidth=1.5, linecolor=gold)
            echo_ring = GEllipse(x=x, y=y, width=ring_size,
                                 height=ring_size, linewidth=1.5,
                                 fillcolor=(0, 0, 0, 0), linecolor=gold)
            city_light = GEllipse(x=city_x, y=city_y, width=9,
                                  height=9, fillcolor=gold)
            route.draw(view)
            echo_ring.draw(view)
            city_light.draw(view)

    def _update_split_flash(self, dt):
        """
        reduces the remaining time for each split effect and removes
        effects when their timers reach zero

        parameter dt: seconds since the previous update (a finite number at
        least zero)
        precondition: dt is a finite number at least zero
        """
        position = 0
        while position < len(self._split_flash):
            flash = self._split_flash[position]
            flash[2] = flash[2] - dt
            if flash[2] <= 0:
                del self._split_flash[position]
            else:
                position = position + 1

    def _draw_split_flash(self, view):
        """
        draws a harmless expanding circle where a bomb recently split

        parameter view: the GView where the object should be drawn
        precondition: view is a GView
        """
        for x, y, seconds in self._split_flash:
            size = 24 + (0.55 - seconds) * 180
            ring = GEllipse(x=x, y=y, width=size, height=size,
                            linewidth=2, fillcolor=(0, 0, 0, 0),
                            linecolor=UI_ACCENT)
            ring.draw(view)

# i seriously cannot look at another missile rn 😭

# ugh every time i think its done theres another bug 😭