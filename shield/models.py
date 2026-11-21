"""
The visible objects in Missile Shield.

Authors: Joon Lee (jl4875) + Richard Li (rl998)
Date: December 6, 2026

The provided game2d framework and assignment starter are by Walker M. White.
The images and fonts used here are the assets provided with the assignment.
Each object keeps its own information. It does not look inside a Wave or app.
"""
from consts import *
from game2d import *


class Silo(GImage):
    """
    A missile silo with a visible count of its remaining ammunition.

    A silo stays on screen after a bomb hits it. The controller responds to
    that hit by setting its ammunition to zero. The inherited x and y are
    the center of the picture, while bottom is the bottom of the picture.
    """
    # Attribute _ammunition: The number of rockets left in this silo.
    # Invariant: _ammunition is an int greater than or equal to zero.
    # Attribute _ammunition_label: The number drawn over the silo picture.
    # Invariant: _ammunition_label is a GLabel with text str(_ammunition).

    def getAmmo(self):
        """
        Returns the number of rockets left in this silo, as an int.
        """
        remaining_ammunition = self._ammunition
        return remaining_ammunition

    def setAmmo(self, amount):
        """
        Changes the ammunition count and the number shown on the silo.

        Parameter amount: The new number of rockets in this silo.
        Precondition: amount is an int greater than or equal to zero.
        """
        assert type(amount) == int
        assert amount >= 0
        self._ammunition = amount
        number_to_display = str(amount)
        self._ammunition_label.text = number_to_display

    def __init__(self, x):
        """
        Initializes a full silo centered horizontally at x, on the ground.

        Parameter x: The horizontal coordinate of the silo's center.
        Precondition: x is a number (int or float).
        """
        silo_center_height = SILO_HEIGHT / 2
        super().__init__(x=x, y=silo_center_height, width=SILO_WIDTH,
                         height=SILO_HEIGHT, source=SILO_IMAGE)
        self._ammunition = AMMO_COUNT
        # ugh im so tired 😴
        label_center_height = SILO_HEIGHT / 4
        starting_number = str(self._ammunition)
        self._ammunition_label = GLabel(
            x=x, y=label_center_height, text=starting_number,
            font_name=BASIC_FONT, font_size=THEME_SMALL,
            linecolor='white')

    def draw(self, view):
        """
        Draws the silo picture and then its ammunition number.

        Parameter view: The view where this silo should be drawn.
        Precondition: view is a GView.
        """
        super().draw(view)
        self._ammunition_label.x = self.x
        self._ammunition_label.y = self.bottom + self.height / 4
        self._ammunition_label.draw(view)


class City(GImage):
    """
    A city that is drawn until it is destroyed.

    Keeping the object after its destruction preserves its original target
    location. A later bomb can reach that same location without shifting
    the positions of any of the other cities.
    """
    # Attribute _alive: Whether this city is still standing.
    # Invariant: _alive is a bool; a destroyed city never becomes alive again.

    def getAlive(self):
        """
        Returns True if this city is still standing; otherwise returns False.
        """
        return self._alive

    def __init__(self, x):
        """
        Initializes a living city with its bottom at CITY_OFFSET.

        Parameter x: The horizontal coordinate of the city's center.
        Precondition: x is a number (int or float).
        """
        half_city_height = CITY_HEIGHT / 2
        city_center_height = CITY_OFFSET + half_city_height
        super().__init__(x=x, y=city_center_height, width=CITY_WIDTH,
                         height=CITY_HEIGHT, source=CITY_IMAGE)
        self._alive = True

    def destroy(self):
        """
        Marks this city as destroyed, including if it was already destroyed.
        """
        # a second bomb cannot make an already gone city extra gone 😭
        self._alive = False

    def draw(self, view):
        """
        Draws this city only if it has not been destroyed.

        Parameter view: The view where this city should be drawn.
        Precondition: view is a GView.
        """
        if self._alive:
            super().draw(view)


class Target(GImage):
    """
    The aiming reticule and its current movement speed.

    The controller checks the arrow keys and chooses the new position. The
    inherited position and size properties remain public, as in GImage.
    """
    # Attribute _movement_speed: The current arrow-key movement speed.
    # Invariant: _movement_speed is a number from 0 to AIM_SPEED_LIMIT.

    def getSpeed(self):
        """
        Returns the reticule's current movement speed, as a number.
        """
        return self._movement_speed

    def setSpeed(self, speed):
        """
        Changes the movement speed to speed.

        Parameter speed: The new movement speed.
        Precondition: speed is a number from 0 to AIM_SPEED_LIMIT, inclusive.
        """
        assert type(speed) == int or type(speed) == float
        assert speed >= 0
        assert speed <= AIM_SPEED_LIMIT
        self._movement_speed = speed

    def __init__(self, x, y):
        """
        Initializes a stationary aiming reticule centered at (x, y).

        Parameter x: The horizontal coordinate of the reticule's center.
        Precondition: x is a number (int or float).
        Parameter y: The vertical coordinate of the reticule's center.
        Precondition: y is a number (int or float).
        """
        super().__init__(x=x, y=y, width=AIM_WIDTH, height=AIM_HEIGHT,
                         source=AIM_IMAGE)
        self._movement_speed = 0
        # ugh im so busy pls help 🫠


class Bomb(GEllipse):
    """
    A bomb moving in a straight line toward a fixed city or silo location.

    A bomb remembers when it should drop, but the controller decides when
    to start updating and drawing it. Its tail begins at its original
    location. Reaching the destination sets a flag for the controller.
    """
    # Attribute _starting_x: The horizontal coordinate of the tail's start.
    # Invariant: _starting_x is a number and does not change.
    # Attribute _starting_y: The vertical coordinate of the tail's start.
    # Invariant: _starting_y is a number and does not change.
    # Attribute _destination_x: The horizontal coordinate of the impact.
    # Invariant: _destination_x is a number and does not change.
    # Attribute _destination_y: The vertical coordinate of the impact.
    # Invariant: _destination_y is a number and does not change.
    # Attribute _drop_time: Seconds from the beginning of the wave to launch.
    # Invariant: _drop_time is a nonnegative number and does not change.
    # Attribute _target_slot: The original target's position among nine slots.
    # Invariant: _target_slot is an int from 0 through 8 and does not change.
    # Attribute _arrived: Whether this bomb has reached its impact location.
    # Invariant: _arrived is a bool; True implies (x, y) is the destination.
    # Attribute _tail: The line from the bomb's start to its current position.
    # Invariant: _tail is a GPath with four coordinates and BOMB_TAIL color.

    def getStartTime(self):
        """
        Returns the scheduled drop time, in seconds from the wave's start.
        """
        return self._drop_time

    def getTargetSlot(self):
        """
        Returns the original target's slot number, as an int from 0 to 8.
        """
        return self._target_slot

    def getArrived(self):
        """
        Returns True if this bomb has reached its destination; False otherwise.
        """
        return self._arrived

    def getRemainingTime(self, speed):
        """
        Returns the seconds needed to reach the destination at speed.

        This estimate assumes that the bomb keeps moving at the given speed.

        Parameter speed: The speed to use for this estimate, in pixels/second.
        Precondition: speed is a number greater than zero.
        """
        remaining_distance = self._distance_to_destination()
        remaining_seconds = remaining_distance / speed
        return remaining_seconds

    def getFuturePosition(self, seconds, speed):
        """
        Returns the predicted (x, y) tuple after seconds, without moving.

        A prediction past impact returns the destination. The result assumes
        a constant speed, so a later change to the speed changes the estimate.

        Parameter seconds: How far into the future to look, in seconds.
        Precondition: seconds is a nonnegative number.
        Parameter speed: The predicted movement speed, in pixels/second.
        Precondition: speed is a nonnegative number.
        """
        horizontal_difference = self._destination_x - self.x
        vertical_difference = self._destination_y - self.y
        remaining_distance = self._distance_to_destination()
        requested_distance = seconds * speed
        if remaining_distance == 0:
            return (self._destination_x, self._destination_y)
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

    def __init__(self, start_x, start_y, target_x, target_y,
                 drop_time, target_slot):
        """
        Initializes a bomb from (start_x, start_y) to (target_x, target_y).

        Parameter start_x: The horizontal starting coordinate.
        Precondition: start_x is a number (int or float).
        Parameter start_y: The vertical starting coordinate.
        Precondition: start_y is a number (int or float).
        Parameter target_x: The fixed horizontal destination coordinate.
        Precondition: target_x is a number (int or float).
        Parameter target_y: The fixed vertical destination coordinate.
        Precondition: target_y is a number (int or float).
        Parameter drop_time: Seconds from the wave's start until this drops.
        Precondition: drop_time is a nonnegative number.
        Parameter target_slot: The target's original position in the row.
        Precondition: target_slot is an int from 0 through 8.
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

    def update(self, dt, speed):
        """
        Moves this bomb toward its destination without passing it.

        The controller only calls this after the scheduled drop time. A bomb
        already at its destination stays there until the controller removes it.

        Parameter dt: The number of seconds to move this bomb.
        Precondition: dt is a nonnegative number.
        Parameter speed: This bomb's speed for this step, in pixels/second.
        Precondition: speed is a nonnegative number.
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
        Draws the bomb's translucent tail and then its white circular head.

        Parameter view: The view where this bomb should be drawn.
        Precondition: view is a GView.
        """
        self._tail.draw(view)
        super().draw(view)

    def _distance_to_destination(self):
        """
        Returns the nonnegative distance from the bomb to its destination.
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
    A rocket that travels to a fixed point and then slowly expands.

    The destination is copied when the rocket is created. Moving the aiming
    reticule later does not move that destination. The controller removes
    finished rockets before updating the remaining ones so that an explosion
    is drawn at its maximum radius for one frame before disappearing.
    """
    # Attribute _starting_x: The horizontal coordinate where this was fired.
    # Invariant: _starting_x is a number and does not change.
    # Attribute _starting_y: The vertical coordinate where this was fired.
    # Invariant: _starting_y is a number and does not change.
    # Attribute _destination_x: The horizontal coordinate chosen at launch.
    # Invariant: _destination_x is a number and does not change.
    # Attribute _destination_y: The vertical coordinate chosen at launch.
    # Invariant: _destination_y is a number and does not change.
    # Attribute _exploding: Whether this rocket has reached its destination.
    # Invariant: _exploding is a bool; True implies (x, y) is the destination.
    # Attribute _tail: The line from the silo to the current rocket position.
    # Invariant: _tail is a GPath, drawn only when _exploding is False.
    # Invariant: width == height, with radius from MIN to MAX rocket radius.

    def getExploding(self):
        """
        Returns True if this rocket is expanding at its destination.
        """
        return self._exploding

    def getFinished(self):
        """
        Returns True if this explosion has reached its maximum radius.

        A True result means the controller should remove it at the start of
        the next update, after it has been drawn at full size.
        """
        current_radius = self.width / 2
        if self._exploding:
            if current_radius >= ROCKET_MAX_RADIUS:
                return True
        return False

    def __init__(self, start_x, start_y, target_x, target_y):
        """
        Initializes a rocket traveling from its silo to a fixed aim point.

        Parameter start_x: The horizontal starting coordinate at the silo.
        Precondition: start_x is a number (int or float).
        Parameter start_y: The vertical starting coordinate at the silo.
        Precondition: start_y is a number (int or float).
        Parameter target_x: The horizontal aiming coordinate at launch.
        Precondition: target_x is a number (int or float).
        Parameter target_y: The vertical aiming coordinate at launch.
        Precondition: target_y is a number (int or float).
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

    def update(self, dt):
        """
        Moves the rocket or grows its explosion for dt seconds.

        If it arrives during this update, the remaining part of dt is used
        to grow the explosion. A large dt cannot move it past the destination
        or make its explosion larger than ROCKET_MAX_RADIUS.

        Parameter dt: The number of seconds to advance the rocket.
        Precondition: dt is a nonnegative number.
        """
        if self._exploding:
            self._grow_explosion(dt)
        else:
            self._move_toward_destination(dt)

    def draw(self, view):
        """
        Draws the traveling rocket and tail, or only its expanding explosion.

        Parameter view: The view where this rocket should be drawn.
        Precondition: view is a GView.
        """
        if not self._exploding:
            self._tail.draw(view)
        super().draw(view)

    def _move_toward_destination(self, dt):
        """
        Moves toward the destination and starts the explosion on arrival.

        Parameter dt: The number of seconds available for movement.
        Precondition: dt is a nonnegative number and this is not exploding.
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
        Stops at the destination and begins a translucent explosion.

        Parameter remaining_seconds: The time left after arriving this step.
        Precondition: remaining_seconds is a nonnegative number.
        """
        # the little blue dot finally gets to be a big blue dot 😭
        self.x = self._destination_x
        self.y = self._destination_y
        self._exploding = True
        self.fillcolor = ROCKET_TAIL
        self._grow_explosion(remaining_seconds)

    def _grow_explosion(self, dt):
        """
        Increases the radius by ROCKET_STEP_RADIUS per second, up to the max.

        Parameter dt: The number of seconds available for growth.
        Precondition: dt is a nonnegative number and this is exploding.
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
        Returns the nonnegative distance from this rocket to its destination.
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


# omg this took so long 😭