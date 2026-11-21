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
    # _data: the wave dict after checks + with speed and missiles in it
    # _bomb_speed: how fast bombs fall + in pixels/sec and finite and > 0
    # _silos: three Silo objects + lined up left to right
    # _cities: six City objects and destroyed ones still stay in this list
    # _targets: all nine starting City/Silo objects and slot order stays put
    # _target: a Target + all of it onscreen and above the silos
    # _pending_bombs: Bomb objects waiting for the scheduled launch times
    # _falling_bombs: Bomb objects that launched and are still around
    # _rockets: Rocket objects still flying or showing a blast
    # _elapsed_time: active game seconds so far and always >= 0
    # _lost: bool + True once we lose the last city
    # _won: bool + True once all bombs/rockets end and a city is still here
    # _features: a dict with four bools + one on/off switch per extra
    # _custom_enabled: bool + True if we switched on at least one extra
    # _forecast_visible: bool + True means show the optional forecasts
    # _bookmarks: at most three saved aim positions inside the bounds
    # _next_bookmark: next slot to recall (from 0 to len(_bookmarks))
    # _replacement_bookmark: saved slot we replace next + from 0 to 2
    # _bubble_seconds: charge we still have + from 0 to BUBBLE_CAPACITY
    # _bubble_requested: bool + True if the bubble key is held
    # _bubble_fraction: how much of the latest step had charge + as a fraction
    # _intercepted_count: bombs stopped so far and always >= 0
    # _recycled_count: rounds actually given back so far and always >= 0
    # _constellation_points: at most 18 positions of intercepted bombs
    # _notice: a short feedback string (or just an empty string)
    # _notice_seconds: seconds until the feedback goes away and always >= 0
    # _sounds: one SoundEffects object using the current sound setting
    # _hud_panel: the GRectangle behind the main top bar
    # _hud_rules: three skinny GRectangles between the main counters
    # _mode_label: lowercase GLabel for the rule name of this wave
    # _metric_labels: three GLabels with city + ammo + threat counts
    # _metric_titles: three GLabels naming those counts in that same order
    # _controls_label: a GLabel with the aim/fire keys shared by both modes
    # _audio_label: a GLabel with the sound setting or unavailable message
    # _tool_centers: maps the enabled feature names to horizontal centers
    # _tool_panels: one GRectangle per extra turned on + in menu order
    # _tool_labels: maps enabled feature names to lowercase value GLabels
    # _tool_hint_labels: maps enabled feature names to key reminder GLabels
    # _notice_parts: six shapes that make a rounded notice card
    # _notice_pulse: seconds left for the new-message text pulse (>= 0)
    # _notice_label: the GLabel for quick feedback below the status cards
    # _bubble_track: the GRectangle under the slow field charge bar
    # _bubble_fill: a GRectangle that stays inside the charge bar track
    # _slot_labels: three labels (one firing key for each silo)
    # _bookmark_labels: three GLabels reused as numbers for saved aim spots
    # _weather_labels: nine GLabels for the optional time to hit estimates
    # _surviving_slots: None at first (city slot number list in later rounds)
    # _split_flash: list of triples (x position + y position + seconds left)
    # _signal_echoes: up to 12 fading paths from a hit to a living city
    # _flyers: custom only aircraft objects that drop bombs during a wave
    # _hud_parts: rounded pieces making one dark top status card
    # _metric_previous: last displayed text for city ammo and threat counts
    # _metric_pulses: seconds left in each count animation (three values >= 0)
    # _metric_icons: three GImages beside the city ammo and threat counters

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLost(self):
        """
        returns True only after all six city objects have been destroyed
        """
        did_we_lose = self._lost
        return did_we_lose

    def getWon(self):
        """
        returns True after every bomb and rocket is gone and one city still
        survives
        """
        did_we_win = self._won
        return did_we_win

    def getCustomEnabled(self):
        """
        returns True when the current json enables at least one extra tool
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
        returns a new list containing the key instructions for enabled custom
        tools
        this is how the pause screen gets the controls (so the app can ask
        here instead of poking around in the hidden feature dictionary)
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
        returns a fresh list of three ammo totals (left then center then
        right)
        """
        remaining_ammunition = []
        for current_silo in self._silos:
            current_amount = current_silo.getAmmo()
            remaining_ammunition.append(current_amount)
        return remaining_ammunition

    def getScore(self):
        """
        returns five points per remaining rocket plus 100 points per living
        city
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
        returns True when sound is unmuted (even if a device is missing)
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
        plays the short scoring sound for the item counted just now
        parameter kind: 0 means one rocket (5 points)
        kind 1 means one city (100 points)
        precondition: kind is 0 or 1
        """
        if kind == 0:
            self._sounds.play('score_rocket')
        else:
            self._sounds.play('score_city')

    def showRoundStart(self):
        """shows the new round number for two seconds and pulses the counters

        this only appears for rounds that have a round_number in the custom
        json data. it never changes the bombs or the rocket counts
        """
        if 'round_number' not in self._data:
            return
        number = str(self._data['round_number'])
        self._show_notice('round ' + number + ' / protect the cities')
        self._notice_seconds = 2.0
        self._metric_pulses = [0.25, 0.25, 0.25]

    def __init__(self, data, surviving_slots=None):
        """
        validates the wave json and creates the target objects and scheduled
        bombs

        bad wave data raises ValueError (so the app can explain the loading
        problem instead of trying to play a broken wave)
        parameter data: the contents read from a wave file
        precondition: data is any value returned by GameApp.load_json
        parameter surviving_slots: None for all six cities or a list of
        surviving city slot numbers
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

        keys get read once per frame (but movement takes little steps because
        a slow frame could otherwise skip a blast. finished rockets go away
        before anything moves (so the biggest blast still gets one frame
        onscreen))
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
        self._pulse_metrics(dt)
        self._update_hud()

    # DRAW METHOD TO DRAW THE GAME OBJECTS
    def draw(self, view):
        """
        draws all current city objects and silos and airborne objects without
        moving them

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
        plays the start cue once after a wave is successfully loaded
        """
        self._sounds.play('start')

    def stopSounds(self):
        """
        stops all current game sound effects without changing the mute
        setting
        """
        self._sounds.stop()

    def finishSounds(self, player_won):
        """
        stops previous cues and plays the one result cue for winning or
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
        raises ValueError for invalid speed or missiles or extra feature
        settings
        bad data raises ValueError (so nothing tries to build a half loaded
        wave)
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
        returns True for an int or finite float (False for bool or infinity
        or nan)
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
        checks the start x and target slot and launch time of one bomb
        dictionary
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
        self._check_splinter_data(information)

    def _check_feature_data(self):
        """
        checks that every optional feature key is known and every flag is bool
        raises ValueError for bad feature data + like an unknown name or a
        value that is not a bool
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
        """checks one flyer type and position and its scheduled bomb drops

        parameter entry: one flyer entry from a custom json wave
        precondition: entry can be any json value
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
        """checks drop times and their fixed target slots for a flyer

        parameter entry: one previously checked flyer dictionary
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
        """makes only the bonus aircraft listed in the custom wave json"""
        self._flyers = []
        for flyer_data in self._data.get('flyers', []):
            self._flyers.append(SkyCourier(flyer_data))

    def _update_flyers(self, dt):
        """moves each aircraft and checks for rocket hits and bomb drops

        a rocket hit cancels the rest of that aircraft drop orders
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
        """checks the drop times and makes a bomb for each order that is due

        bombs start at the aircraft position and head toward a fixed target
        parameter flyer: the SkyCourier with the list of drop orders
        precondition: flyer is a SkyCourier that has started its flight
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
        """returns True if a rocket blast hits the body of this aircraft

        tests its center and four edge points so a wing can get hit too
        parameter flyer: the active plane or drone or satellite to check
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
        makes three silos and six cities at fixed slots (respecting surviving
        slots)
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
        creates all bombs from json and puts them in the pending list
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
        moves the aim marker with held arrows and clamps it inside the safe
        area
        the starter speeds 0.2 and 10 are for a nominal frame (so
        AIM_FRAME_SCALE turns them into movement over time using a nominal 60
        fps)
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
        returns the horizontal direction and vertical direction and arrow
        held flag
        for example + left and right cancel the horizontal movement (but the
        last value is still True because arrows are being held)
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
        fires once per new press of 1 or 2 or 3 (using the matching silo)
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
        launches one rocket toward a fixed aim point and subtracts one ammo
        the destination gets saved now (so moving the aim later leaves this
        rocket headed to the same spot)
        parameter silo_number: the index of the silo to fire from
        precondition: silo_number is 0 + 1 (or 2)
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
        deletes only explosions that were already drawn at full size
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
        repeats short time steps until dt has passed or the wave has ended
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
        advances the clocks and rockets and bombs before checking collisions
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
        advances each rocket and plays the explosion sound once on arrival
        a blast already growing had its sound (so it does not get another one
        here)
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
        moves every pending bomb whose scheduled drop time has arrived into
        flight
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
        moves released bombs only for elapsed time after their own drop times
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
        removes every bomb whose center is inside a growing rocket explosion
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
        empties a hit silo or destroys a hit city (without changing target
        slots)
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
        loses immediately at zero cities or wins only after every bomb and
        rocket ends
        a waiting bomb counts too (so a quiet moment between launches is not
        a win)
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
        sets the loss flag and removes airborne objects and all optional
        aiming guides
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
        handles f and b and tab and x and space only for enabled features
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
        saves the current aim location and replaces an old position after
        three saves
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
        basically + only the aim jumps back and launched rockets keep the
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
        spends charge during the slow field and restores charge after release
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
        returns normal speed outside the powered field (22 percent inside at
        full charge)
        only bombs in the bubble slow down (so the launch clock + rockets +
        blasts all keep the original timing)
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
        counts an intercepted bomb and optionally stores a star and awards ammo
        parameter current_bomb: the stopped bomb + before it is removed
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
        adds one rocket to the least stocked silo if it is below the starting
        limit
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
        saves a lowercase message for 2.8 seconds of active play
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
        """returns rectangles and four circles that make a borderless card

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
        creates the top count labels and optional tool cards for the current
        wave
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
        returns a lowercase GLabel with the supplied readable font
        parameter text: the words to show and must be a string
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
        sets aside top bar labels for living cities and ammo and incoming bombs
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
        places one card for each feature enabled in the current json
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
        parameter tool_name: the feature flag of this card
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
        prepares the small message card beneath the main status bar
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
        creates the slow field charge track and fill for the matching feature
        card
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
        creates firing key labels and future impact labels above each target
        slot
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
        recalculates city and ammo and threat counts for the visible status bar
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
        shows mute status or reports that no audio device or cue is available
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
        shows the earliest estimated impact for each threatened target slot
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
        draws only the optional forecast and bookmark and field and star guides
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
        draws harmless prediction rings at bomb positions 1.5 seconds ahead
        this uses the current speed for the next FORECAST_SECONDS (but moving
        the bubble can change that speed (so the rings are just an estimate))
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
        draws up to three labeled circles at saved aiming coordinates

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
        draws the harmless mint circle showing where bombs are being slowed

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
        draws a connected set of harmless points at recent interception
        locations
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
        replaces each triggered orange parent with two or three normal child
        bombs

        new children start at the parent position and use targets from the
        custom json
        the parent is removed after the children are added so it cannot split
        again
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
        sends a decorative gold signal from a stopped bomb to the nearest city

        only living cities can receive this little light message
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
        draws short gold messages from interceptions to living cities

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
        decreases the remaining lifetime of each split flash and deletes
        expired ones

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
        draws a harmless expanding circle at each recent split position

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