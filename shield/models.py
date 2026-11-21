"""
Models module for MissileShield

This module contains the model classes for the Missile Shield game. Anything 
that you interact with on the screen is model: the silos, the cities, the 
missiles, and so on.

The classes provided in this module are sufficient for the core game. You only
need to add classes to this module if you are adding extensions to the game.
You are qlwo free to make any changes to these classes if you want. 

If you are unsure about  whether to make a new class or not, please ask on 
Ed Discussions. We will answer.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026.
"""
from consts import *
from game2d import *


# PRIMARY RULE: Models are not allowed to access anything in any module other 
# than consts.py. If you need extra information from a wave object, then it 
# should be a parameter in your method.

class Silo(GImage):
    """
    A class representing a silo
    
    Silos contain the ammunition for the missile shield. Every time you fire
    a defensive strike, it must consume ammo from one of your silos. One a
    silo runs out of ammo it can no longer be used this wave. Hence ammunition
    is the primary attribute this class must add to GImage.
    
    If a missile collides with a silo, it does not destroy it. However, it does
    immediately destroy all ammunition, making the silo useless.
    
    NOTE: The attributes x and y in GImage are NOT hidden (they are properties
    and do not need getters/setters). You do not need getters and setters for
    attributes you inherit from GImage. You only need them for new attributes
    that you create.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _ammunition: the rockets left here + basically the ammo counter
    # invariant: _ammunition is an int greater than or equal to zero
    # _ammunition_label: the ammo number sitting over the silo picture
    # invariant: _ammunition_label is a GLabel with text str(_ammunition)
    # _ammunition_badge: a dark GRectangle so the number stands out
    # _ammunition_track: a GRectangle for the whole length of the bar
    # _ammunition_fill: a GRectangle for the part of the ammo bar left

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getAmmo(self):
        """
        returns the number of rockets left in this silo (an int at least
        zero)
        """
        remaining_ammunition = self._ammunition
        return remaining_ammunition

    def setAmmo(self, amount):
        """
        sets the rocket count and refreshes the number shown above this silo

        parameter amount: how many rockets this silo should have now
        precondition: amount is an int greater than or equal to zero
        """
        assert type(amount) == int
        assert amount >= 0
        self._ammunition = amount
        number_to_display = str(amount)
        self._ammunition_label.text = number_to_display

    # INITIALIZER TO SET THE ATTRIBUTES
    
    def __init__(self, x):
        """
        makes a full silo centered at x with its bottom at screen height zero

        parameter x: where the center of the silo goes horizontally
        precondition: x is a number (int or float)
        """
        silo_center_height = SILO_HEIGHT / 2
        super().__init__(x=x, y=silo_center_height, width=SILO_WIDTH,
                         height=SILO_HEIGHT, source=SILO_IMAGE)
        self._ammunition = AMMO_COUNT
        self._make_ammo_display(x)

    # ADDITIONAL METHODS AS NEEDED
    
    def draw(self, view):
        """
        draws the silo picture and then its ammunition number and progress
        bar

        parameter view: where to draw this silo
        precondition: view is a GView
        """
        super().draw(view)
        self._draw_ammo_display(view)

    def _make_ammo_display(self, x):
        """
        creates the number label and dark badge and ammunition bar for this
        silo

        parameter x: where the center of this silo goes horizontally
        precondition: x is a number (int or float)
        """
        starting_number = str(self._ammunition)
        self._ammunition_badge = GRectangle(
            x=x, y=32, width=68, height=52, fillcolor=UI_SURFACE,
            linecolor=UI_BORDER, linewidth=1)
        self._ammunition_label = GLabel(
            x=x, y=35, text=starting_number, font_name=THEME_FONT,
            font_size=32, linecolor=UI_TEXT)
        self._ammunition_track = GRectangle(
            x=x, y=12, width=48, height=3, fillcolor=UI_BORDER,
            linewidth=0)
        self._ammunition_fill = GRectangle(
            x=x, y=12, width=48, height=3, fillcolor=UI_ACCENT,
            linewidth=0)

    def _draw_ammo_display(self, view):
        """
        moves the ammo graphics to follow the silo and draws the filled
        fraction

        parameter view: where to draw this ammo display
        precondition: view is a GView
        """
        self._ammunition_badge.x = self.x
        self._ammunition_badge.y = self.bottom + 32
        self._ammunition_badge.draw(view)
        self._ammunition_label.x = self.x
        self._ammunition_label.y = self.bottom + 35
        self._ammunition_label.draw(view)
        self._ammunition_track.x = self.x
        self._ammunition_track.y = self.bottom + 12
        self._ammunition_track.draw(view)
        if self._ammunition > 0:
            ammo_fraction = min(self._ammunition / AMMO_COUNT, 1)
            self._ammunition_fill.width = 48 * ammo_fraction
            self._ammunition_fill.left = self.x - 24
            self._ammunition_fill.y = self.bottom + 12
            self._ammunition_fill.draw(view)


class City(GImage):
    """
    A class representing a city that can be blown up.
    
    For the most part, citiess are just drawn to the screen. There is no need 
    for a lot of custom methods in this class. Indeed, the primary reason the 
    class exists is so we can keep the image source and size all in one place.
    With that said, you are unlikely to need any methods here other than the 
    initializer.
    
    NOTE: The attributes x and y in GImage are NOT hidden (they are properties
    and do not need getters/setters). You do not need getters and setters for
    attributes you inherit from GImage. You only need them for new attributes
    that you create.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _alive: whether this city is still around
    # invariant: _alive is a bool and a destroyed city never comes back

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getAlive(self):
        """
        returns True if the city has not been hit (False after it is
        destroyed)
        """
        is_this_city_alive = self._alive
        return is_this_city_alive

    # INITIALIZER TO SET THE ATTRIBUTES
    
    def __init__(self, x):
        """
        creates a living city centered at x with its bottom at CITY_OFFSET

        parameter x: where the center of the city goes horizontally
        precondition: x is a number (int or float)
        """
        half_city_height = CITY_HEIGHT / 2
        city_center_height = CITY_OFFSET + half_city_height
        super().__init__(x=x, y=city_center_height, width=CITY_WIDTH,
                         height=CITY_HEIGHT, source=CITY_IMAGE)
        self._alive = True

    # ADDITIONAL METHODS AS NEEDED
    
    def destroy(self):
        """
        sets the city alive flag to False (a later hit cannot restore it)
        """
        
        self._alive = False

    def draw(self, view):
        """
        draws the city image only if its alive flag is still True

        parameter view: where to draw this city
        precondition: view is a GView
        """
        if self._alive:
            super().draw(view)


class Target(GImage):
    """
    A class representing the target reticule
    
    The target reticule is what you use to aim your rockets. Per the 
    instructions, it has a variable speed. When it moves, it starts at
    AIM_SPEED_STEP pixels per second, and increases until it reaches
    AIM_SPEED_LIMIT
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _movement_speed: how fast the arrow keys move the reticule rn
    # invariant: _movement_speed is a number from 0 to AIM_SPEED_LIMIT

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getSpeed(self):
        """
        returns the current aim acceleration speed in nominal frame units
        """
        speed_right_now = self._movement_speed
        return speed_right_now

    def setSpeed(self, speed):
        """
        sets the current aim speed to a value from zero to AIM_SPEED_LIMIT

        parameter speed: how fast the reticule should move now
        precondition: speed is a number from 0 to AIM_SPEED_LIMIT + inclusive
        """
        assert type(speed) == int or type(speed) == float
        assert speed >= 0
        assert speed <= AIM_SPEED_LIMIT
        self._movement_speed = speed

    # INITIALIZER TO SET THE ATTRIBUTES
    
    def __init__(self, x, y):
        """
        creates the aiming reticule at x and y with movement speed zero

        parameter x: where the center of the reticule goes horizontally
        precondition: x is a number (int or float)
        parameter y: where the center of the reticule goes vertically
        precondition: y is a number (int or float)
        """
        super().__init__(x=x, y=y, width=AIM_WIDTH, height=AIM_HEIGHT,
                         source=AIM_IMAGE)
        self._movement_speed = 0
        

    # ADDITIONAL METHODS AS NEEDED


class Bomb(GEllipse):
    """
    A class representing a dropping bomb
    
    Bombs are defined in the wave JSON file. Each bomb has a start time and
    it should not appear on the screen until its time has past.  A bomb drops
    until it collides with a silo or city (or where a city should be). At
    that point it is destroyed.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _starting_x: where the tail starts horizontally and keep it there
    # invariant: _starting_x is a number and does not change
    # _starting_y: where the tail starts vertically and keep it there
    # invariant: _starting_y is a number and does not change
    # _destination_x: where this bomb is headed horizontally
    # invariant: _destination_x is a number and does not change
    # _destination_y: where this bomb is headed vertically
    # invariant: _destination_y is a number and does not change
    # _drop_time: how many seconds into the wave this bomb should drop
    # invariant: _drop_time is a nonnegative number and does not change
    # _target_slot: where the target started in the row of nine slots
    # invariant: _target_slot is an int from 0 through 8 and does not change
    # _arrived: whether this bomb got all the way to the hit location
    # invariant: _arrived is a bool and True means (x + y) is the destination
    # _tail: a line from the original start to where the bomb is now
    # invariant: _tail is a GPath with four coordinates and BOMB_TAIL color

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getStartTime(self):
        """
        returns the scheduled drop time as seconds from the start of a wave
        """
        time_when_it_drops = self._drop_time
        return time_when_it_drops

    def getTargetSlot(self):
        """
        returns the fixed target slot number (an int from 0 to 8)
        """
        slot_that_gets_hit = self._target_slot
        return slot_that_gets_hit

    def getArrived(self):
        """
        returns True after the bomb reaches the top of its target
        """
        did_the_bomb_arrive = self._arrived
        return did_the_bomb_arrive

    def getRemainingTime(self, speed):
        """
        returns distance to the fixed target divided by the supplied speed

        so this is an estimate + because a later speed change changes the
        timing
        parameter speed: the speed to assume + in pixels per second
        precondition: speed is a number greater than zero
        """
        remaining_distance = self._distance_to_destination()
        remaining_seconds = remaining_distance / speed
        return remaining_seconds

    def getFuturePosition(self, seconds, speed):
        """
        returns a predicted x and y position after the given number of
        seconds

        the prediction stops at the destination because going past it would
        make no sense here. it assumes a constant speed (so changing that
        speed later means the estimate changes too)
        parameter seconds: how many seconds ahead to look
        precondition: seconds is a nonnegative number
        parameter speed: the speed to assume + in pixels per second
        precondition: speed is a nonnegative number
        """
        horizontal_difference = self._destination_x - self.x
        vertical_difference = self._destination_y - self.y
        remaining_distance = self._distance_to_destination()
        requested_distance = seconds * speed
        if remaining_distance == 0:
            future_place = (self._destination_x, self._destination_y)
            return future_place
        elif requested_distance >= remaining_distance:
            return (self._destination_x, self._destination_y)
        else:
            horizontal_direction = horizontal_difference / remaining_distance
            vertical_direction = vertical_difference / remaining_distance
            horizontal_movement = horizontal_direction * requested_distance
            vertical_movement = vertical_direction * requested_distance
            future_x = self.x + horizontal_movement
            future_y = self.y + vertical_movement
            return (future_x, future_y)

    # INITIALIZER TO SET THE ATTRIBUTES
    
    def __init__(self, start_x, start_y, target_x, target_y,
                 drop_time, target_slot):
        """
        creates a bomb traveling from a start point to one fixed target point

        parameter start_x: where the bomb starts horizontally
        precondition: start_x is a number (int or float)
        parameter start_y: where the bomb starts vertically
        precondition: start_y is a number (int or float)
        parameter target_x: the horizontal destination that stays fixed
        precondition: target_x is a number (int or float)
        parameter target_y: the vertical destination that stays fixed
        precondition: target_y is a number (int or float)
        parameter drop_time: how many seconds after the wave starts to drop
        precondition: drop_time is a nonnegative number
        parameter target_slot: the original slot of the target in the row
        precondition: target_slot is an int from 0 through 8
        """
        bomb_diameter = 2 * BOMB_RADIUS
        super().__init__(x=start_x, y=start_y, width=bomb_diameter,
                         height=bomb_diameter, fillcolor=BOMB_COLOR)
        self._starting_x = start_x
        self._starting_y = start_y
        self._destination_x = target_x
        self._destination_y = target_y
        self._drop_time = drop_time
        self._target_slot = target_slot
        self._arrived = False
        initial_tail_points = [start_x, start_y, start_x, start_y]
        self._tail = GPath(points=initial_tail_points,
                           linewidth=BOMB_RADIUS, linecolor=BOMB_TAIL)
        self._speed_scale = 1.0
        self._acceleration = 0.0

    # _speed_scale: positive multiplier used only by new custom wave entries
    # _acceleration: change in pixels per second after each second of flight

    # ADDITIONAL METHODS AS NEEDED
    def setMotion(self, scale, acceleration):
        """sets custom speed settings for this bomb (defaults are unchanged)

        parameter scale: positive speed multiplier from the custom json
        precondition: scale is a positive number
        parameter acceleration: speed change per second of flight
        precondition: acceleration is a finite number
        """
        self._speed_scale = scale
        self._acceleration = acceleration

    def getMotionSpeed(self, normal_speed, seconds):
        """returns speed after adjusting for this bomb age (at least 8 px/s)

        parameter normal_speed: positive pixels per second of the wave
        parameter seconds: nonnegative seconds since this bomb dropped
        """
        age = max(0, seconds)
        new_speed = normal_speed * self._speed_scale
        new_speed = new_speed + age * self._acceleration
        return max(8, new_speed)

    def getMotionSettings(self):
        """returns the custom speed scale and acceleration for split children"""
        return (self._speed_scale, self._acceleration)

    
    def update(self, dt, speed):
        """
        moves the bomb by speed times dt toward its target without
        overshooting

        the controller calls this only after the drop time. if the bomb
        already arrived + it just waits there for the controller to remove it
        parameter dt: how many seconds to move this bomb
        precondition: dt is a nonnegative number
        parameter speed: the speed of this step + in pixels per second
        precondition: speed is a nonnegative number
        """
        if self._arrived:
            return
        next_position = self.getFuturePosition(dt, speed)
        self.x = next_position[0]
        self.y = next_position[1]
        if self.x == self._destination_x:
            if self.y == self._destination_y:
                self._arrived = True
        new_tail_points = [self._starting_x, self._starting_y, self.x, self.y]
        self._tail.points = new_tail_points

    def draw(self, view):
        """
        draws the line from its start to its current point and then the bomb
        dot

        parameter view: where to draw this bomb
        precondition: view is a GView
        """
        self._tail.draw(view)
        super().draw(view)

    def _distance_to_destination(self):
        """
        returns the nonnegative straight line distance to its fixed target
        """
        horizontal_difference = self._destination_x - self.x
        vertical_difference = self._destination_y - self.y
        horizontal_distance_squared = horizontal_difference ** 2
        vertical_distance_squared = vertical_difference ** 2
        total_distance_squared = horizontal_distance_squared
        total_distance_squared = (total_distance_squared +
                                  vertical_distance_squared)
        remaining_distance = total_distance_squared ** 0.5
        return remaining_distance


class Rocket(GEllipse):
    """
    A class representing a defensive rocket
    
    Unlike bombs, rockets are created by player input. The player presses a
    key to fire at the target. The trajectory of the rocket should be from
    the top center of the appropriate silo to current position of the Target
    object. When the rocket reaches that position it explodes.
    
    Rocket explosions are not instantaneous. The rocket ellipse will grow
    slowly until it reaches ROCKET_MAX_RADIUS, at which point it is removed.
    Any Bomb object that comes in contact with that explosion is destroyed.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # _starting_x: where the rocket took off horizontally
    # invariant: _starting_x is a number and does not change
    # _starting_y: where the rocket took off vertically
    # invariant: _starting_y is a number and does not change
    # _destination_x: the horizontal aim position saved at launch
    # invariant: _destination_x is a number and does not change
    # _destination_y: the vertical aim position saved at launch
    # invariant: _destination_y is a number and does not change
    # _exploding: whether the rocket got there and turned into a blast
    # invariant: _exploding is a bool and True means (x + y) is the destination
    # _tail: a line from the silo to where the rocket is now
    # invariant: _tail is a GPath + drawn only when _exploding is False
    # invariant: width == height and the radius stays from ROCKET_MIN_RADIUS
    

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getExploding(self):
        """
        returns True after this rocket reaches its saved aim point
        """
        did_it_explode = self._exploding
        return did_it_explode

    def getFinished(self):
        """
        returns True after its growing explosion reaches maximum radius

        so True means remove it at the start of the next update + because the
        full size blast still needs one frame on screen
        """
        current_radius = self.width / 2
        if self._exploding:
            if current_radius >= ROCKET_MAX_RADIUS:
                return True
        return False

    # INITIALIZER TO SET THE ATTRIBUTES
    
    def __init__(self, start_x, start_y, target_x, target_y):
        """
        creates a rocket from the silo position to one fixed aim position

        parameter start_x: where the rocket starts horizontally + at the silo
        precondition: start_x is a number (int or float)
        parameter start_y: where the rocket starts vertically + at the silo
        precondition: start_y is a number (int or float)
        parameter target_x: the horizontal aim position copied at launch
        precondition: target_x is a number (int or float)
        parameter target_y: the vertical aim position copied at launch
        precondition: target_y is a number (int or float)
        """
        rocket_diameter = 2 * ROCKET_MIN_RADIUS
        super().__init__(x=start_x, y=start_y, width=rocket_diameter,
                         height=rocket_diameter, fillcolor=ROCKET_COLOR)
        self._starting_x = start_x
        self._starting_y = start_y
        self._destination_x = target_x
        self._destination_y = target_y
        self._exploding = False
        initial_tail_points = [start_x, start_y, start_x, start_y]
        self._tail = GPath(points=initial_tail_points,
                           linewidth=ROCKET_MIN_RADIUS,
                           linecolor=ROCKET_TAIL)

    # ADDITIONAL METHODS AS NEEDED
    
    def update(self, dt):
        """
        moves the rocket toward its fixed aim point or grows its blast

        if it arrives partway through + the leftover time grows the blast.
        even with a big dt + it stops at the destination and the radius stays
        at or below ROCKET_MAX_RADIUS
        parameter dt: how many seconds to move or grow this rocket
        precondition: dt is a nonnegative number
        """
        if self._exploding:
            self._grow_explosion(dt)
        else:
            self._move_toward_destination(dt)

    def draw(self, view):
        """
        draws the moving rocket and tail or the explosion without its tail

        parameter view: where to draw this rocket
        precondition: view is a GView
        """
        if not self._exploding:
            self._tail.draw(view)
        super().draw(view)

    def _move_toward_destination(self, dt):
        """
        moves toward the aim point and begins the explosion on arrival

        parameter dt: how many seconds this move gets
        precondition: dt is a nonnegative number and this is not exploding
        """
        horizontal_difference = self._destination_x - self.x
        vertical_difference = self._destination_y - self.y
        remaining_distance = self._distance_to_destination()
        requested_distance = ROCKET_SPEED * dt
        if requested_distance >= remaining_distance:
            seconds_until_arrival = remaining_distance / ROCKET_SPEED
            seconds_left_to_grow = dt - seconds_until_arrival
            self._start_explosion(seconds_left_to_grow)
        else:
            horizontal_direction = horizontal_difference / remaining_distance
            vertical_direction = vertical_difference / remaining_distance
            horizontal_movement = horizontal_direction * requested_distance
            vertical_movement = vertical_direction * requested_distance
            self.x = self.x + horizontal_movement
            self.y = self.y + vertical_movement
            tail_points = [self._starting_x, self._starting_y, self.x, self.y]
            self._tail.points = tail_points

    def _start_explosion(self, remaining_seconds):
        """
        moves the rocket to the saved point and changes it into a blast

        parameter remaining_seconds: seconds left in this step after arrival
        precondition: remaining_seconds is a nonnegative number
        """
        
        self.x = self._destination_x
        self.y = self._destination_y
        self._exploding = True
        self.fillcolor = ROCKET_TAIL
        self._grow_explosion(remaining_seconds)

    def _grow_explosion(self, dt):
        """
        adds ROCKET_STEP_RADIUS times dt to the blast radius (up to the max)

        parameter dt: how many seconds this blast gets to grow
        precondition: dt is a nonnegative number and this is exploding
        """
        old_radius = self.width / 2
        added_radius = ROCKET_STEP_RADIUS * dt
        new_radius = old_radius + added_radius
        if new_radius > ROCKET_MAX_RADIUS:
            new_radius = ROCKET_MAX_RADIUS
        new_diameter = new_radius * 2
        self.width = new_diameter
        self.height = new_diameter

    def _distance_to_destination(self):
        """
        returns the nonnegative distance from the rocket to its saved aim
        point
        """
        horizontal_difference = self._destination_x - self.x
        vertical_difference = self._destination_y - self.y
        horizontal_distance_squared = horizontal_difference ** 2
        vertical_distance_squared = vertical_difference ** 2
        total_distance_squared = horizontal_distance_squared
        total_distance_squared = (total_distance_squared +
                                  vertical_distance_squared)
        remaining_distance = total_distance_squared ** 0.5
        return remaining_distance


class SoundEffects(object):
    """
    a little bank of game sounds, kept separate from the game rules

    each cue gets three voices, so quick launches can overlap. stop a voice
    before replaying it because game2d cannot restart a Sound already playing
    all these wav files come from the approved assignment package. if a file
    or audio device fails, skip that cue so the game can still keep going
    """
    # _sounds: a dictionary mapping each cue to a list of three Sound objects
    # _next_voice: a dictionary picking the next index + 0 through 2 per cue
    # _enabled: a bool and False stops every sound and makes play stay quiet

    def getEnabled(self):
        """
        returns True when the sound bank is unmuted
        """
        do_we_play_audio = self._enabled
        return do_we_play_audio

    def getAvailable(self):
        """
        returns True when at least one sound cue loaded correctly
        """
        do_any_sounds_work = len(self._sounds) > 0
        return do_any_sounds_work

    def setEnabled(self, enabled):
        """
        switches future sound on or off and stops current cues on mute

        parameter enabled: whether later cues should make sound
        precondition: enabled is a bool
        """
        assert type(enabled) == bool
        self._enabled = enabled
        if not enabled:
            self.stop()

    def __init__(self):
        """
        loads three voices for each supplied wav cue without playing them yet
        """
        self._sounds = {}
        self._next_voice = {}
        self._enabled = True
        self._load_cue('start', 'air-raid.wav', 0.18)
        self._load_cue('launch', 'blast3.wav', 0.20)
        self._load_cue('explode', 'blast1.wav', 0.32)
        self._load_cue('intercept', 'ping.wav', 0.15)
        self._load_cue('impact', 'blast2.wav', 0.42)
        self._load_cue('empty', 'sizzle.wav', 0.18)
        self._load_cue('reward', 'ping.wav', 0.40)
        self._load_cue('drone', 'drone.wav', 0.16)
        self._load_cue('satellite', 'satellite.wav', 0.16)

    def play(self, cue):
        """
        plays the next available voice for the requested named cue

        up to three calls for one cue can overlap. if audio fails + just
        disable that cue so the other sounds and the wave can keep going
        parameter cue: the name of an event + like 'launch' or 'impact'
        precondition: cue is a string and an unknown cue does nothing
        """
        if not self._enabled or cue not in self._sounds:
            return
        voices = self._sounds[cue]
        voice_number = self._next_voice[cue]
        current_sound = voices[voice_number]
        try:
            current_sound.stop()
            current_sound.play()
        except Exception as problem:
            self._disable_cue(cue, problem)
            return
        self._next_voice[cue] = (voice_number + 1) % len(voices)

    def stop(self):
        """
        stops all currently playing sound cues
        """
        cue_names = list(self._sounds)
        for cue in cue_names:
            try:
                for current_sound in self._sounds[cue]:
                    current_sound.stop()
            except Exception as problem:
                self._disable_cue(cue, problem)

    def _load_cue(self, cue, filename, volume):
        """
        loads three voices of one wav file and stores them under the given
        name

        parameter cue: the name that play uses to find this sound
        precondition: cue is a nonempty string not already in _sounds
        parameter filename: which supplied wav file to load
        precondition: filename is a nonempty string naming a sound asset
        parameter volume: how loud this cue should be
        precondition: volume is a number from 0 through 1
        """
        voices = []
        try:
            for voice_number in range(3):
                current_sound = Sound(filename)
                current_sound.volume = volume
                voices.append(current_sound)
        except Exception as problem:
            self._report_audio_problem(cue, problem)
            return
        self._sounds[cue] = voices
        self._next_voice[cue] = 0

    def _disable_cue(self, cue, problem):
        """
        removes a broken sound cue and reports the original error

        parameter cue: the sound event that failed
        precondition: cue is a key in _sounds and _next_voice
        parameter problem: the error that came back from the audio provider
        precondition: problem is an Exception
        """
        for current_sound in self._sounds[cue]:
            try:
                current_sound.stop()
            except Exception:
                pass
        del self._sounds[cue]
        del self._next_voice[cue]
        self._report_audio_problem(cue, problem)

    def _report_audio_problem(self, cue, problem):
        """
        prints the cue name and reason audio could not be used

        parameter cue: the sound event that could not be used
        precondition: cue is a string
        parameter problem: the error that came back from the audio provider
        precondition: problem is an Exception
        """
        print('sound unavailable: ' + cue + '. the game can still run.')
        print(str(problem))




class SplinterBomb(Bomb):
    """
    an orange incoming bomb that splits into a few normal bombs

    it moves just like Bomb until it reaches the split height. then the wave
    asks it for its child target slots and replaces it with smaller bombs
    the class never needs to know anything about the wave controller
    """
    # _split_y: a number above the top of the target + below GAME_HEIGHT
    # _child_slots: a list of two or three valid target slot integers
    # _split_done: bool and True after this bomb has split

    def __init__(self, x, y, target_x, target_y, time, slot,
                 split_y, children):
        """
        makes an orange bomb with a split height and two or three saved child
        target slots

        parameter x: x position where the parent starts
        parameter y: y position where the parent starts
        parameter target_x: x position of the parent target
        parameter target_y: y position of the parent target
        parameter time: scheduled drop time in seconds from the wave start
        parameter slot: original target number (an int from 0 through 8)
        parameter split_y: height where the bomb divides into children
        parameter children: list of two or three target slot numbers
        precondition: positions are finite numbers and time is nonnegative
        precondition: split_y is at least 150 and below GAME_HEIGHT
        precondition: every child slot is an int from 0 through 8
        """
        super().__init__(x, y, target_x, target_y, time, slot)
        self._split_y = split_y
        self._child_slots = children[:]
        self._split_done = False
        self.fillcolor = UI_ACCENT

    def shouldSplit(self):
        """
        returns True once this parent falls to split_y and has not already
        split
        """
        if self._split_done:
            return False
        if self.getArrived():
            return False
        if self.y <= self._split_y:
            return True
        return False

    def getChildSlots(self):
        """
        returns a copy of the target slots assigned to its child bombs
        """
        the_slots_to_use = self._child_slots[:]
        return the_slots_to_use

    def markSplit(self):
        """
        marks this parent as already split so it cannot split a second time
        """
        self._split_done = True

# bro i am so done with these circles 😭


class SkyCourier(GImage):
    """
    a plane or drone or satellite that drops bombs in a custom wave

    each courier gets a start time and its own list of drop orders
    the plane moves sideways and the drone bobs up and down
    the satellite moves slowly and can drop more than one bomb
    """
    # _kind: one of plane or drone or satellite
    # _speed: horizontal pixels per second (nonzero)
    # _start: nonnegative time of first appearance
    # _drops: list of pending dictionaries with time and target
    # _active: bool (False until the start time)
    # _alive: bool (False after a rocket explosion hits it)
    # _base_y: original vertical center in pixels
    # _motion: vertical movement direction (1 or -1)
    # _seconds_empty: seconds with no pending drops (nonnegative)

    def getAlive(self):
        """returns True if the courier has not been shot down"""
        return self._alive

    def getActive(self):
        """returns True after its start time has arrived"""
        return self._active

    def getKind(self):
        """returns the name of the type of courier"""
        return self._kind

    def getFinished(self):
        """returns True after a kill or after all drops are long finished"""
        if not self._alive:
            return True
        if self._active and not self._drops and self._seconds_empty > 1.8:
            return True
        return False

    def __init__(self, info):
        """makes one sprite from a validated courier dictionary

        parameter info: custom json entry with kind x y speed start drops
        precondition: all values were checked by Wave
        """
        self._kind = info['kind']
        images = {'plane': ('plane@2x.png', 106, 40),
                  'drone': ('drone@2x.png', 68, 68),
                  'satellite': ('satellite@2x.png', 94, 54)}
        picture = images[self._kind]
        super().__init__(x=info['x'], y=info['y'], source=picture[0],
                         width=picture[1], height=picture[2])
        self._speed = info['speed']
        self._start = info['start']
        self._drops = list(info['drops'])
        self._active = False
        self._alive = True
        self._base_y = info['y']
        self._motion = 1
        self._seconds_empty = 0

    def update(self, dt, elapsed):
        """moves an active courier for dt seconds and keeps the drone bobbing

        parameter dt: nonnegative seconds since last physics step
        parameter elapsed: nonnegative seconds since this wave started
        """
        if not self._alive or elapsed < self._start:
            return
        self._active = True
        self.x = self.x + self._speed * dt
        if self._kind == 'drone':
            self._move_drone(dt)
        if not self._drops:
            self._seconds_empty = self._seconds_empty + dt

    def _move_drone(self, dt):
        """moves a small distance up or down and reverses at the limits"""
        self.y = self.y + 42 * self._motion * dt
        if self.y > self._base_y + 26:
            self._motion = -1
        if self.y < self._base_y - 26:
            self._motion = 1

    def takeDueDrops(self, elapsed):
        """returns ready drop orders and removes them from the pending list

        parameter elapsed: seconds since this wave started
        precondition: elapsed is nonnegative
        """
        ready = []
        if not self._active or not self._alive:
            return ready
        position = 0
        while position < len(self._drops):
            if self._drops[position]['time'] <= elapsed + 0.000000001:
                ready.append(self._drops[position])
                del self._drops[position]
            else:
                position = position + 1
        return ready

    def destroy(self):
        """stops the courier and cancels its remaining drops"""
        self._alive = False
        self._drops = []

    def draw(self, view):
        """draws the sprite only after it appears and before it is destroyed"""
        if self._active and self._alive:
            super().draw(view)