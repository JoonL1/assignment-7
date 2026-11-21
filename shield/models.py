"""
Models for Missile Shield.

The models remember where each object is and what it can do. The Wave
controller decides when to call their methods.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026
"""
from consts import *
from game2d import *
import introcs
import math


# This is a shared helper for the two kinds of moving projectiles.
def _move_toward_destination(shape, destination_x, destination_y, speed, dt):
    """Moves shape toward a fixed destination. Returns True upon arrival.

    It never travels past the destination, even if dt is unusually large.
    The object must have public x and y attributes, like a GEllipse.
    """
    horizontal_distance = destination_x - shape.x
    vertical_distance = destination_y - shape.y
    remaining_distance_squared = horizontal_distance**2 + vertical_distance**2
    remaining_distance = math.sqrt(remaining_distance_squared)
    distance_this_frame = speed * dt
    if remaining_distance <= distance_this_frame or remaining_distance == 0:
        shape.x = destination_x
        shape.y = destination_y
        return True
    horizontal_fraction = horizontal_distance / remaining_distance
    vertical_fraction = vertical_distance / remaining_distance
    horizontal_movement = horizontal_fraction * distance_this_frame
    vertical_movement = vertical_fraction * distance_this_frame
    shape.x = shape.x + horizontal_movement
    shape.y = shape.y + vertical_movement
    return False


class Silo(GImage):
    """A mountain holding the rockets the player may launch.

    Attribute _ammo: Number of defensive missiles remaining, int >= 0.
    Attribute _ammo_label: GLabel placed over this silo's drawing.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _ammo: Number of defensive missiles remaining, int >= 0.
    # Attribute _ammo_label: GLabel placed over this silo's drawing.
    # end of invariant notes


    def getAmmo(self):
        """Returns the number of rockets left in this silo."""
        return self._ammo

    def setAmmo(self, amount):
        """Sets the remaining number of rockets, updating the visible label."""
        assert type(amount) == int and amount >= 0
        self._ammo = amount
        self._ammo_label.text = str(amount)

    def __init__(self, x):
        """Creates a full silo at horizontal coordinate x."""
        super().__init__(x=x, bottom=0, width=SILO_WIDTH,
                         height=SILO_HEIGHT, source=SILO_IMAGE)
        self._ammo = AMMO_COUNT
        self._ammo_label = GLabel(text=str(self._ammo), x=x, y=self.bottom+29,
                                  font_size=THEME_SMALL, font_name=BASIC_FONT,
                                  linecolor='white')

    def draw(self, view):
        """Draws the silo image, then places its ammunition count above it."""
        super().draw(view)
        self._ammo_label.draw(view)


class City(GImage):
    """A city to protect. A destroyed city is removed by Wave."""

    def __init__(self, x):
        """Creates a city whose base is CITY_OFFSET above the bottom."""
        super().__init__(x=x, bottom=CITY_OFFSET, width=CITY_WIDTH,
                         height=CITY_HEIGHT, source=CITY_IMAGE)


class Target(GImage):
    """The aiming crosshair moved by the arrow keys.

    Attribute _speed: Nonnegative movement speed in pixels per frame.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _speed: Nonnegative movement speed in pixels per frame.
    # end of invariant notes


    def getSpeed(self):
        """Returns how far this target moves in the current frame."""
        return self._speed

    def setSpeed(self, new_speed):
        """Changes speed without exceeding the course's speed limit."""
        self._speed = max(0, min(AIM_SPEED_LIMIT, new_speed))

    def __init__(self, x, y):
        """Starts the aiming target at (x,y), with no momentum."""
        super().__init__(x=x, y=y, width=AIM_WIDTH,
                         height=AIM_HEIGHT, source=AIM_IMAGE)
        self._speed = 0.0


class Bomb(GEllipse):
    """An incoming bomb with a fixed destination from the wave file.

    Attribute _destination_x: Where the bomb will hit, a number.
    Attribute _destination_y: The top of the target object, a number.
    Attribute _destination_slot: Number 0..8 of the target in ground order.
    Attribute _drop_time: Seconds after the start of the wave, number >= 0.
    Attribute _active: True if the bomb has been released, a bool.
    Attribute _arrived: True when it has reached the target, a bool.
    Attribute _tail: A GPath from the initial position to current position.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _destination_x: Where the bomb will hit, a number.
    # Attribute _destination_y: The top of the target object, a number.
    # Attribute _destination_slot: Number 0..8 of the target in ground order.
    # Attribute _drop_time: Seconds after the start of the wave, number >= 0.
    # Attribute _active: True if the bomb has been released, a bool.
    # Attribute _arrived: True when it has reached the target, a bool.
    # Attribute _tail: A GPath from the initial position to current position.
    # end of invariant notes


    def getDropTime(self):
        """Returns the scheduled time this bomb starts falling."""
        return self._drop_time

    def getTargetSlot(self):
        """Returns the left-to-right target index from the JSON file."""
        return self._destination_slot

    def getDestination(self):
        """Returns the point at which this incoming bomb will hit."""
        return (self._destination_x, self._destination_y)

    def isActive(self):
        """Returns True when the bomb has been released."""
        return self._active

    def hasArrived(self):
        """Returns True once the bomb reaches its original target."""
        return self._arrived

    def activate(self):
        """Allows this bomb to be drawn and moved."""
        self._active = True

    def __init__(self, start_x, target, slot, drop_time):
        """Creates a bomb at the sky's top aimed at a City or Silo."""
        super().__init__(x=start_x, y=GAME_HEIGHT,
                         width=2*BOMB_RADIUS, height=2*BOMB_RADIUS,
                         fillcolor=BOMB_COLOR, linecolor=None)
        self._destination_x = target.x
        self._destination_y = target.top
        self._destination_slot = slot
        self._drop_time = drop_time
        self._active = False
        self._arrived = False
        self._tail = GPath(points=[start_x,GAME_HEIGHT,start_x,GAME_HEIGHT],
                           linecolor=BOMB_TAIL, linewidth=BOMB_RADIUS)

    def advance(self, dt, speed):
        """Moves a dropped bomb one frame and extends its trailing line."""
        if self._active and not self._arrived:
            self._arrived = _move_toward_destination(
                self, self._destination_x, self._destination_y, speed, dt)
            original_points = self._tail.points
            original_x = original_points[0]
            original_y = original_points[1]
            self._tail.points = [original_x, original_y, self.x, self.y]

    def draw(self, view):
        """Draws the transparent tail first and the white bomb second."""
        if self._active:
            self._tail.draw(view)
            super().draw(view)


class Rocket(GEllipse):
    """A defensive rocket which becomes a circular blast at its target.

    Attribute _destination_x: The x coordinate selected at launch.
    Attribute _destination_y: The y coordinate selected at launch.
    Attribute _tail: GPath showing the flight path, or None after detonation.
    Attribute _exploding: Whether this rocket has reached its aim point.
    Attribute _finished: Whether its finished blast may be removed.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _destination_x: The x coordinate selected at launch.
    # Attribute _destination_y: The y coordinate selected at launch.
    # Attribute _tail: GPath showing the flight path, or None after detonation.
    # Attribute _exploding: Whether this rocket has reached its aim point.
    # Attribute _finished: Whether its finished blast may be removed.
    # end of invariant notes


    def isExploding(self):
        """Returns True after the rocket has reached its destination."""
        return self._exploding

    def isFinished(self):
        """Returns True if its full-size explosion has finished displaying."""
        return self._finished

    def __init__(self, start_x, start_y, target_x, target_y):
        """Starts a defensive rocket at a silo pointing at a fixed point."""
        start_size = 2*ROCKET_MIN_RADIUS
        super().__init__(x=start_x,y=start_y,width=start_size,
                         height=start_size,fillcolor=ROCKET_COLOR,
                         linecolor=None)
        self._destination_x = target_x
        self._destination_y = target_y
        self._exploding = False
        self._finished = False
        self._tail = GPath(points=[start_x,start_y,start_x,start_y],
                           linecolor=ROCKET_TAIL, linewidth=BOMB_RADIUS)

    def advance(self, dt):
        """Moves toward the aim point or grows an already-triggered blast."""
        if self._exploding:
            self._growExplosion(dt)
        elif not self._finished:
            has_reached_target = _move_toward_destination(
                self, self._destination_x, self._destination_y,
                ROCKET_SPEED, dt)
            self._updateTail()
            if has_reached_target:
                self._beginExplosion()

    def draw(self, view):
        """Draws the flight trail only before the explosion begins."""
        if self._tail is not None:
            self._tail.draw(view)
        super().draw(view)

    def _updateTail(self):
        """Connects the rocket's launch location to its current position."""
        original_points = self._tail.points
        launch_x = original_points[0]
        launch_y = original_points[1]
        self._tail.points = [launch_x,launch_y,self.x,self.y]

    def _beginExplosion(self):
        """Changes the travelling rocket to a translucent circular shield."""
        self._exploding = True
        self._tail = None
        self.fillcolor = ROCKET_TAIL

    def _growExplosion(self, dt):
        """Expands the radius but shows its maximum size for one whole frame."""
        current_radius = self.width / 2.0
        if current_radius >= ROCKET_MAX_RADIUS:
            self._finished = True
        else:
            # ugh this circle takes forever to grow 😭
            radius_change = ROCKET_STEP_RADIUS * dt
            new_radius = min(ROCKET_MAX_RADIUS, current_radius+radius_change)
            self.width = new_radius * 2
            self.height = new_radius * 2
            if new_radius >= ROCKET_MAX_RADIUS:
                self._finished = True



class MemoryLantern(GEllipse):
    """A harmless expanding outline marking a lost city.

    This is only a visual effect. It never collides with bombs or rockets.
    Attribute _remaining: Seconds until the effect disappears, number >= 0.
    """
    # HIDDEN ATTRIBUTES (documented for the graders)
    # Attribute _remaining: Seconds until the effect disappears, number >= 0.
    # end of invariant notes


    def isFinished(self):
        """Returns True once this temporary mark has faded away."""
        return self._remaining <= 0

    def __init__(self, x, y):
        """Places a small violet ring where a city was lost."""
        super().__init__(x=x,y=y,width=12,height=12,
                         fillcolor=None,linecolor=introcs.RGB(173,139,255,175),
                         linewidth=3)
        self._remaining = 4.0

    def advance(self, dt):
        """Widens the circle while it fades from the sky."""
        self._remaining = max(0.0,self._remaining-dt)
        new_diameter = min(110,self.width+dt*26)
        self.width = new_diameter
        self.height = new_diameter
        alpha = int(175 * self._remaining/4.0)
        self.linecolor = introcs.RGB(173,139,255,alpha)


# omg this took so long 😭