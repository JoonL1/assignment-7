"""
the visible objects for missile shield.

authors: joon lee (jl4875) + richard li (rl998)
date: december 6, 2026

the supplied game2d framework and starter are by walker m. white.
the pictures and fonts also come from the assignment package.
each object tracks the data it needs, so it never looks inside a Wave or
the app to figure out what to do.
"""
from consts import *
from game2d import *


class Silo(GImage):
    """
    a missile silo with a number showing how many rockets are left.

    the picture stays on screen after a bomb hits because the controller just
    sets the ammo to zero. x and y still give the center of the picture, and
    bottom gives the bottom edge, like the usual properties of a GImage.
    """
    # _ammunition: how many rockets are left in this silo.
    # invariant: _ammunition is an int greater than or equal to zero.
    # _ammunition_label: the number shown on top of the silo picture.
    # invariant: _ammunition_label is a GLabel with text str(_ammunition).

    def getAmmo(self):
        """
        returns how many rockets are left in this silo as an int.
        """
        remaining_ammunition = self._ammunition
        return remaining_ammunition

    def setAmmo(self, amount):
        """
        sets the ammo count and updates the number on the picture too.

        parameter amount: the new number of rockets in this silo.
        precondition: amount is an int greater than or equal to zero.
        """
        assert type(amount) == int
        assert amount >= 0
        self._ammunition = amount
        number_to_display = str(amount)
        self._ammunition_label.text = number_to_display

    def __init__(self, x):
        """
        sets up a full silo with the bottom on the ground and center at x.

        parameter x: the horizontal coordinate of the center of the silo.
        precondition: x is a number (int or float).
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
        draws the silo first, then puts the ammo number on top.

        parameter view: where to draw this silo.
        precondition: view is a GView.
        """
        super().draw(view)
        self._ammunition_label.x = self.x
        self._ammunition_label.y = self.bottom + self.height / 4
        self._ammunition_label.draw(view)


class City(GImage):
    """
    a city that stays visible until a bomb destroys it.

    the object stays in the target list even after the picture disappears,
    because later bombs still need the same destination. so destroying one
    city does not shift the positions of the other cities.
    """
    # _alive: whether this city is still standing.
    # invariant: _alive is a bool; a destroyed city never comes back.

    def getAlive(self):
        """
        returns True if this city is still standing, or False if it is gone.
        """
        return self._alive

    def __init__(self, x):
        """
        sets up a living city with the bottom edge at CITY_OFFSET.

        parameter x: the horizontal coordinate of the center of the city.
        precondition: x is a number (int or float).
        """
        half_city_height = CITY_HEIGHT / 2
        city_center_height = CITY_OFFSET + half_city_height
        super().__init__(x=x, y=city_center_height, width=CITY_WIDTH,
                         height=CITY_HEIGHT, source=CITY_IMAGE)
        self._alive = True

    def destroy(self):
        """
        marks this city as destroyed, even if an earlier bomb already hit it.
        """
        # a second bomb cannot make an already gone city extra gone 😭
        self._alive = False

    def draw(self, view):
        """
        draws the city if it is still standing, but draws nothing if it is gone.

        parameter view: where to draw this city.
        precondition: view is a GView.
        """
        if self._alive:
            super().draw(view)


class Target(GImage):
    """
    the aiming reticule and how fast it is moving right now.

    the controller reads the arrow keys and picks the next position. position
    and size stay public because those properties already come from GImage.
    """
    # _movement_speed: how fast the arrow keys move the reticule right now.
    # invariant: _movement_speed is a number from 0 to AIM_SPEED_LIMIT.

    def getSpeed(self):
        """
        returns the current movement speed of the reticule as a number.
        """
        return self._movement_speed

    def setSpeed(self, speed):
        """
        sets the movement speed to speed.

        parameter speed: how fast the reticule should move.
        precondition: speed is a number from 0 to AIM_SPEED_LIMIT, inclusive.
        """
        assert type(speed) == int or type(speed) == float
        assert speed >= 0
        assert speed <= AIM_SPEED_LIMIT
        self._movement_speed = speed

    def __init__(self, x, y):
        """
        sets up a reticule centered at (x, y), starting with zero speed.

        parameter x: the horizontal coordinate of the center of the reticule.
        precondition: x is a number (int or float).
        parameter y: the vertical coordinate of the center of the reticule.
        precondition: y is a number (int or float).
        """
        super().__init__(x=x, y=y, width=AIM_WIDTH, height=AIM_HEIGHT,
                         source=AIM_IMAGE)
        self._movement_speed = 0
        # ugh im so busy pls help 🫠


class Bomb(GEllipse):
    """
    a bomb that moves straight toward one fixed city or silo location.

    the bomb saves the drop time, but the controller decides when to start
    moving and drawing it. the tail always starts at the original position,
    and reaching the destination sets a flag so the controller can handle
    that hit.
    """
    # _starting_x: the horizontal coordinate where the tail starts.
    # invariant: _starting_x is a number and does not change.
    # _starting_y: the vertical coordinate where the tail starts.
    # invariant: _starting_y is a number and does not change.
    # _destination_x: the horizontal coordinate where this bomb will hit.
    # invariant: _destination_x is a number and does not change.
    # _destination_y: the vertical coordinate where this bomb will hit.
    # invariant: _destination_y is a number and does not change.
    # _drop_time: seconds from the start of the wave until this bomb drops.
    # invariant: _drop_time is a nonnegative number and does not change.
    # _target_slot: the original position of the target among nine slots.
    # invariant: _target_slot is an int from 0 through 8 and does not change.
    # _arrived: whether this bomb has reached the impact location.
    # invariant: _arrived is a bool; True means (x, y) is the destination.
    # _tail: the line from the start of the bomb to the current position.
    # invariant: _tail is a GPath with four coordinates and BOMB_TAIL color.

    def getStartTime(self):
        """
        returns the drop time in seconds from the start of the wave.
        """
        return self._drop_time

    def getTargetSlot(self):
        """
        returns the original slot of the target as an int from 0 through 8.
        """
        return self._target_slot

    def getArrived(self):
        """
        returns True if the bomb reached the destination, or False otherwise.
        """
        return self._arrived

    def getRemainingTime(self, speed):
        """
        returns how many seconds are left before impact at the given speed.

        the estimate assumes the bomb keeps that speed for the whole trip.

        parameter speed: the speed for the estimate, in pixels per second.
        precondition: speed is a number greater than zero.
        """
        remaining_distance = self._distance_to_destination()
        remaining_seconds = remaining_distance / speed
        return remaining_seconds

    def getFuturePosition(self, seconds, speed):
        """
        returns the predicted (x, y) tuple after seconds, without moving.

        the result stops at the destination if the prediction would go past it.
        this assumes a constant speed, so changing the speed later also changes
        the estimate.

        parameter seconds: how many seconds ahead to look.
        precondition: seconds is a nonnegative number.
        parameter speed: the predicted movement speed in pixels per second.
        precondition: speed is a nonnegative number.
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
        sets up a bomb from (start_x, start_y) to (target_x, target_y).

        parameter start_x: the horizontal coordinate where the bomb starts.
        precondition: start_x is a number (int or float).
        parameter start_y: the vertical coordinate where the bomb starts.
        precondition: start_y is a number (int or float).
        parameter target_x: the fixed horizontal coordinate of the destination.
        precondition: target_x is a number (int or float).
        parameter target_y: the fixed vertical coordinate of the destination.
        precondition: target_y is a number (int or float).
        parameter drop_time: seconds from the start of the wave to this drop.
        precondition: drop_time is a nonnegative number.
        parameter target_slot: the original position of the target in the row.
        precondition: target_slot is an int from 0 through 8.
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
        moves this bomb toward the destination but never past it.

        the controller only calls this after the drop time. if the bomb already
        arrived, it stays there until the controller removes it.

        parameter dt: how many seconds to move this bomb.
        precondition: dt is a nonnegative number.
        parameter speed: speed of the bomb this step, in pixels per second.
        precondition: speed is a nonnegative number.
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
        draws the see-through tail first, then the white circle of the bomb.

        parameter view: where to draw this bomb.
        precondition: view is a GView.
        """
        self._tail.draw(view)
        super().draw(view)

    def _distance_to_destination(self):
        """
        returns the distance from the bomb to the destination, at least 0.
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
    a rocket that flies to a fixed point and then grows into an explosion.

    the destination is copied at launch, so moving the reticule later does
    not move the rocket destination. the controller removes finished rockets
    before updating the others, which gives each explosion one frame at full
    size before it disappears.
    """
    # _starting_x: the horizontal coordinate where this rocket was fired.
    # invariant: _starting_x is a number and does not change.
    # _starting_y: the vertical coordinate where this rocket was fired.
    # invariant: _starting_y is a number and does not change.
    # _destination_x: the horizontal coordinate of the aim point at launch.
    # invariant: _destination_x is a number and does not change.
    # _destination_y: the vertical coordinate of the aim point at launch.
    # invariant: _destination_y is a number and does not change.
    # _exploding: whether this rocket has reached the destination.
    # invariant: _exploding is a bool; True means (x, y) is the destination.
    # _tail: the line from the silo to the current position of the rocket.
    # invariant: _tail is a GPath, drawn only when _exploding is False.
    # invariant: width == height; the radius stays from ROCKET_MIN_RADIUS
    # through ROCKET_MAX_RADIUS, including both limits.

    def getExploding(self):
        """
        returns True if the rocket has arrived and is now growing an explosion.
        """
        return self._exploding

    def getFinished(self):
        """
        returns True if the explosion has reached the maximum radius.

        True tells the controller to remove this when the next update starts,
        so the full-size explosion gets drawn once before disappearing.
        """
        current_radius = self.width / 2
        if self._exploding:
            if current_radius >= ROCKET_MAX_RADIUS:
                return True
        return False

    def __init__(self, start_x, start_y, target_x, target_y):
        """
        sets up a rocket that travels from the silo to a fixed aiming point.

        parameter start_x: the horizontal starting coordinate at the silo.
        precondition: start_x is a number (int or float).
        parameter start_y: the vertical starting coordinate at the silo.
        precondition: start_y is a number (int or float).
        parameter target_x: the horizontal aiming coordinate copied at launch.
        precondition: target_x is a number (int or float).
        parameter target_y: the vertical aiming coordinate copied at launch.
        precondition: target_y is a number (int or float).
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
        moves the rocket or grows the explosion for dt seconds.

        if the rocket arrives during this step, the leftover time grows the
        explosion. even a large dt cannot send it past the destination or make
        the radius larger than ROCKET_MAX_RADIUS.

        parameter dt: how many seconds to advance the rocket.
        precondition: dt is a nonnegative number.
        """
        if self._exploding:
            self._grow_explosion(dt)
        else:
            self._move_toward_destination(dt)

    def draw(self, view):
        """
        draws the moving rocket and tail, or just the explosion after arrival.

        parameter view: where to draw this rocket.
        precondition: view is a GView.
        """
        if not self._exploding:
            self._tail.draw(view)
        super().draw(view)

    def _move_toward_destination(self, dt):
        """
        moves toward the destination and starts the explosion when it arrives.

        parameter dt: how many seconds are available for movement.
        precondition: dt is a nonnegative number and this is not exploding.
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
        stops at the destination and starts a see-through explosion.

        parameter remaining_seconds: time left after arrival during this step.
        precondition: remaining_seconds is a nonnegative number.
        """
        # the little blue dot finally gets to be a big blue dot 😭
        self.x = self._destination_x
        self.y = self._destination_y
        self._exploding = True
        self.fillcolor = ROCKET_TAIL
        self._grow_explosion(remaining_seconds)

    def _grow_explosion(self, dt):
        """
        grows the radius by ROCKET_STEP_RADIUS per second, but stops at the max.

        parameter dt: how many seconds are available for growth.
        precondition: dt is a nonnegative number and this is exploding.
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
        returns the distance from this rocket to the destination, at least 0.
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