"""independent behavioral checks; kept outside the submission.

Run with Python; this installs minimal graphics modules, then imports the real
project models and Wave. These checks verify numerical/game rules only. They do
not claim to replace a live Kivy rendering and input smoke test.
"""
import importlib.util
import json
import math
from pathlib import Path
import sys
import types
import unittest


from qa_paths import PROJECT


class Color:
    def __init__(self, *values):
        self.values = values
        self.red = values[0] if values else 0
        self.green = values[1] if len(values) > 1 else 0
        self.blue = values[2] if len(values) > 2 else 0
        self.alpha = values[3] if len(values) > 3 else 255

    def __eq__(self, other):
        return isinstance(other, Color) and self.values == other.values


class Point:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, factor):
        return Point(self.x * factor, self.y * factor)

    def distanceTo(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)


class Vector(Point):
    def length(self):
        return math.hypot(self.x, self.y)

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length

    def normal(self):
        length = self.length()
        return Vector(self.x / length, self.y / length)


class Graphic:
    def __init__(self, **kwargs):
        self.x = kwargs.pop("x", 0)
        self.y = kwargs.pop("y", 0)
        self.width = kwargs.pop("width", 0)
        self.height = kwargs.pop("height", 0)
        self.fillcolor = kwargs.pop("fillcolor", None)
        self.linecolor = kwargs.pop("linecolor", None)
        self.linewidth = kwargs.pop("linewidth", 0)
        self.source = kwargs.pop("source", "")
        self.points = kwargs.pop("points", [])
        self.text = kwargs.pop("text", "")
        self.font_size = kwargs.pop("font_size", 20)
        self.children = kwargs.pop("children", [])
        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def left(self):
        return self.x - self.width / 2

    @left.setter
    def left(self, value):
        self.x = value + self.width / 2

    @property
    def right(self):
        return self.x + self.width / 2

    @right.setter
    def right(self, value):
        self.x = value - self.width / 2

    @property
    def bottom(self):
        return self.y - self.height / 2

    @bottom.setter
    def bottom(self, value):
        self.y = value + self.height / 2

    @property
    def top(self):
        return self.y + self.height / 2

    @top.setter
    def top(self, value):
        self.y = value - self.height / 2

    def draw(self, view):
        view.drawn.append(self)

    def contains(self, point):
        if hasattr(point, "x"):
            x, y = point.x, point.y
        else:
            x, y = point
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class GImage(Graphic):
    pass


class GEllipse(Graphic):
    def contains(self, point):
        if hasattr(point, "x"):
            x, y = point.x, point.y
        else:
            x, y = point
        if self.width <= 0 or self.height <= 0:
            return False
        horizontal = (x - self.x) / (self.width / 2)
        vertical = (y - self.y) / (self.height / 2)
        return horizontal * horizontal + vertical * vertical <= 1


class GLabel(Graphic):
    pass


class GPath(Graphic):
    pass


class Sound:
    def __init__(self, *args, **kwargs):
        self.state = "stop"

    def play(self):
        self.state = "play"

    def stop(self):
        self.state = "stop"


class View:
    def __init__(self):
        self.drawn = []


class Input:
    def __init__(self, down=(), pressed=None):
        self.down = set(down)
        self.pressed = set(down if pressed is None else pressed)
        self.touch = None

    def is_key_down(self, key):
        return key in self.down if key else bool(self.down)

    def is_key_pressed(self, key):
        return key in self.pressed if key else bool(self.pressed)

    def is_touch_pressed(self):
        return False


def install_stubs():
    introcs = types.ModuleType("introcs")
    introcs.RGB = Color
    introcs.HSV = Color
    introcs.Point2 = Point
    introcs.Vector2 = Vector
    sys.modules["introcs"] = introcs
    game2d = types.ModuleType("game2d")
    classes = {"GObject": Graphic, "GRectangle": Graphic,
               "GEllipse": GEllipse, "GImage": GImage, "GLabel": GLabel,
               "GPath": GPath, "GScene": Graphic, "GSprite": GImage,
               "GPolygon": Graphic, "GTriangle": Graphic,
               "GameApp": Graphic, "GInput": Input, "GView": View,
               "Sound": Sound}
    for name, cls in classes.items():
        setattr(game2d, name, cls)
    game2d.__all__ = list(classes)
    sys.modules["game2d"] = game2d


install_stubs()
sys.path.insert(0, str(PROJECT))
import consts
import models

# Avoid Python's standard-library module with the same name.
spec = importlib.util.spec_from_file_location("wave", PROJECT / "wave.py")
wave_module = importlib.util.module_from_spec(spec)
sys.modules["wave"] = wave_module
spec.loader.exec_module(wave_module)
Wave = wave_module.Wave


def holding_wave(speed=10):
    return Wave({"speed": speed,
                 "missiles": [{"x": 64, "target": 0, "time": 1000}]})


class ModelsBehavior(unittest.TestCase):
    def assert_xy(self, object, x, y):
        self.assertAlmostEqual(object.x, x, places=7)
        self.assertAlmostEqual(object.y, y, places=7)

    def test_silo_ammunition_and_city_lifecycle(self):
        silo = models.Silo(64)
        self.assertEqual(silo.getAmmo(), 10)
        silo.setAmmo(4)
        self.assertEqual(silo.getAmmo(), 4)
        silo.setAmmo(0)
        self.assertEqual(silo.getAmmo(), 0)
        city = models.City(192)
        self.assertTrue(city.getAlive())
        city.destroy()
        city.destroy()
        self.assertFalse(city.getAlive())

    def test_bomb_known_three_four_five_path(self):
        bomb = models.Bomb(0, 0, 30, 40, 7, 1)
        self.assertEqual(bomb.getStartTime(), 7)
        self.assertEqual(bomb.getTargetSlot(), 1)
        self.assertFalse(bomb.getArrived())
        bomb.update(2, 5)
        self.assert_xy(bomb, 6, 8)
        self.assertAlmostEqual(bomb.getRemainingTime(5), 8)
        future = bomb.getFuturePosition(3, 5)
        self.assertAlmostEqual(future[0], 15)
        self.assertAlmostEqual(future[1], 20)
        self.assert_xy(bomb, 6, 8)
        bomb.update(100, 5)
        self.assert_xy(bomb, 30, 40)
        self.assertTrue(bomb.getArrived())
        bomb.update(3, 5)
        self.assert_xy(bomb, 30, 40)

    def test_bomb_zero_distance_does_not_divide(self):
        bomb = models.Bomb(20, 30, 20, 30, 0, 0)
        bomb.update(1, 50)
        self.assert_xy(bomb, 20, 30)
        self.assertTrue(bomb.getArrived())

    def test_rocket_speed_and_stationary_explosion(self):
        rocket = models.Rocket(0, 0, 30, 40)
        rocket.update(0.025)
        self.assert_xy(rocket, 7.5, 10)
        self.assertFalse(rocket.getExploding())
        rocket.update(0.075)
        self.assert_xy(rocket, 30, 40)
        self.assertTrue(rocket.getExploding())
        diameter = rocket.width
        rocket.update(1)
        self.assertAlmostEqual(rocket.width - diameter, 40)
        self.assertAlmostEqual(rocket.height, rocket.width)
        self.assert_xy(rocket, 30, 40)

    def test_explosion_caps_at_maximum(self):
        rocket = models.Rocket(100, 200, 100, 200)
        rocket.update(0)
        self.assertTrue(rocket.getExploding())
        rocket.update(100)
        self.assertEqual(rocket.width, 200)
        self.assertEqual(rocket.height, 200)
        self.assertTrue(rocket.getFinished())
        rocket.update(1 / 60)
        self.assertTrue(rocket.getFinished())
        self.assertEqual(rocket.width, 200)


class WaveBehavior(unittest.TestCase):
    def test_layout_and_initial_score(self):
        wave = holding_wave()
        self.assertEqual([item.x for item in wave._silos], [64, 576, 1088])
        self.assertEqual([item.x for item in wave._cities],
                         [192, 320, 448, 704, 832, 960])
        self.assertEqual(len(wave._targets), 9)
        self.assertEqual(wave.getAmmoCounts(), [10, 10, 10])
        self.assertEqual(wave.getCitiesLeft(), 6)
        self.assertEqual(wave.getScore(), 750)
        self.assertTrue(all(item.bottom == 0 for item in wave._silos))
        self.assertTrue(all(item.bottom == 20 for item in wave._cities))
        self.assertFalse(wave.getCustomEnabled())

    def test_partial_frame_launch_timing(self):
        wave = Wave({"speed": 10, "missiles": [
            {"x": 64, "target": 0, "time": 0.75}]})
        wave.update(Input(), 1)
        self.assertEqual(len(wave._falling_bombs), 1)
        self.assertAlmostEqual(wave._falling_bombs[0].y, 861.5)

    def test_bomb_at_exact_drop_time_has_not_moved(self):
        wave = Wave({"speed": 10, "missiles": [
            {"x": 64, "target": 0, "time": 1}]})
        wave.update(Input(), 1)
        self.assertEqual(len(wave._falling_bombs), 1)
        self.assertEqual(wave._falling_bombs[0].y, 864)

    def test_unsorted_pending_bombs(self):
        wave = Wave({"speed": 10, "missiles": [
            {"x": 64, "target": 0, "time": 20},
            {"x": 192, "target": 1, "time": 4},
            {"x": 320, "target": 2, "time": 0}]})
        wave.update(Input(), 1)
        self.assertEqual(len(wave._falling_bombs), 1)
        self.assertEqual(wave._falling_bombs[0].getTargetSlot(), 2)
        wave.update(Input(), 4)
        self.assertEqual(len(wave._falling_bombs), 2)
        dropped_slots = sorted(b.getTargetSlot() for b in wave._falling_bombs)
        self.assertEqual(dropped_slots, [1, 2])
        self.assertEqual(len(wave._pending_bombs), 1)
        self.assertFalse(wave.getWon())

    def test_pending_bombs_are_not_drawn(self):
        wave = holding_wave()
        view = View()
        wave.draw(view)
        self.assertFalse(any(isinstance(item, models.Bomb)
                             for item in view.drawn))

    def test_firing_edges_and_no_ammunition(self):
        wave = holding_wave()
        wave._target.x = 300
        wave._target.y = 500
        wave.update(Input(["1"]), 0)
        self.assertEqual(wave.getAmmoCounts(), [9, 10, 10])
        self.assertEqual(len(wave._rockets), 1)
        wave.update(Input(["1"], pressed=[]), 0)
        self.assertEqual(wave.getAmmoCounts(), [9, 10, 10])
        self.assertEqual(len(wave._rockets), 1)
        wave._silos[1].setAmmo(0)
        wave.update(Input(["2"]), 0)
        self.assertEqual(wave.getAmmoCounts(), [9, 0, 10])
        self.assertEqual(len(wave._rockets), 1)

    def test_simultaneous_silo_presses_are_all_handled(self):
        wave = holding_wave()
        wave.update(Input(["1", "2", "3"]), 0)
        self.assertEqual(wave.getAmmoCounts(), [9, 9, 9])
        self.assertEqual(len(wave._rockets), 3)

    def test_rocket_aim_is_frozen(self):
        wave = holding_wave()
        wave._target.x = 300
        wave._target.y = 500
        wave.update(Input(["1"]), 0)
        rocket = wave._rockets[0]
        wave._target.x = 900
        wave._target.y = 700
        rocket.update(10)
        self.assertAlmostEqual(rocket.x, 300)
        self.assertAlmostEqual(rocket.y, 500)

    def test_target_clips_all_edges(self):
        wave = holding_wave()
        for keys in [["right", "up"], ["left", "down"]]:
            for _ in range(250):
                wave.update(Input(keys, []), 1)
            target = wave._target
            self.assertGreaterEqual(target.left, 0)
            self.assertLessEqual(target.right, consts.GAME_WIDTH)
            self.assertLessEqual(target.top, consts.GAME_HEIGHT)
            self.assertGreaterEqual(target.bottom, consts.SILO_HEIGHT)

    def test_target_release_resets_speed(self):
        wave = holding_wave()
        for _ in range(60):
            wave.update(Input(["right"], []), 1 / 60)
        wave.update(Input(), 1 / 60)
        if hasattr(wave._target, "getSpeed"):
            self.assertEqual(wave._target.getSpeed(), 0)
        previous_x = wave._target.x
        wave.update(Input(), 1)
        self.assertEqual(wave._target.x, previous_x)

    def test_overlapping_blasts_delete_every_contained_bomb(self):
        wave = holding_wave()
        first = models.Rocket(400, 400, 400, 400)
        first.update(0)
        first.update(2.35)
        second = models.Rocket(405, 400, 405, 400)
        second.update(0)
        second.update(2.35)
        wave._rockets = [first, second]
        wave._falling_bombs = []
        for x, y in [(400, 400), (410, 400), (400, 410), (390, 390)]:
            wave._falling_bombs.append(models.Bomb(x, y, x, 118, 0, 1))
        wave.update(Input(), 1 / 600)
        self.assertEqual(wave._falling_bombs, [])
        self.assertFalse(wave.getWon())

    def test_bomb_center_not_radius_or_tail_decides_collision(self):
        wave = holding_wave()
        rocket = models.Rocket(400, 400, 400, 400)
        rocket.update(0)
        rocket.update(2.35)
        self.assertAlmostEqual(rocket.width, 100)
        wave._rockets = [rocket]
        # First bomb overlaps by its radius but its center is outside.
        outside = models.Bomb(451, 400, 451, 118, 0, 1)
        # Second bomb's tail crosses the blast, but its head is below it.
        tail_crossing = models.Bomb(400, 600, 400, 118, 0, 1)
        tail_crossing.update(6, 50)
        inside = models.Bomb(449, 400, 449, 118, 0, 1)
        boundary = models.Bomb(450, 400, 450, 118, 0, 1)
        wave._falling_bombs = [outside, tail_crossing, inside, boundary]
        wave.update(Input(), 1 / 600)
        self.assertIn(outside, wave._falling_bombs)
        self.assertIn(tail_crossing, wave._falling_bombs)
        self.assertNotIn(inside, wave._falling_bombs)
        self.assertNotIn(boundary, wave._falling_bombs)

    def test_flying_rocket_has_no_blast(self):
        wave = holding_wave()
        rocket = models.Rocket(400, 400, 800, 700)
        bomb = models.Bomb(400, 400, 400, 118, 0, 1)
        wave._rockets = [rocket]
        wave._falling_bombs = [bomb]
        wave.update(Input(), 0)
        self.assertIn(bomb, wave._falling_bombs)

    def test_repeated_hits_same_city_safe(self):
        wave = Wave({"speed": 10000, "missiles": [
            {"x": 192, "target": 1, "time": 0},
            {"x": 192, "target": 1, "time": 0},
            {"x": 192, "target": 1, "time": 0}]})
        wave.update(Input(), 1)
        self.assertEqual(wave.getCitiesLeft(), 5)
        self.assertEqual(len(wave._falling_bombs), 0)
        self.assertEqual(len(wave._targets), 9)
        self.assertEqual(wave.getScore(), 650)
        self.assertTrue(wave.getWon())

    def test_last_city_loss_precedes_pending_or_rocket_completion(self):
        wave = holding_wave(10)
        for city in wave._cities[:-1]:
            city.destroy()
        last_city = wave._cities[-1]
        bomb = models.Bomb(last_city.x, last_city.top + 1,
                           last_city.x, last_city.top, 0, 7)
        wave._falling_bombs = [bomb]
        wave._rockets = [models.Rocket(64, 128, 1000, 800)]
        wave.update(Input(), 0.2)
        self.assertTrue(wave.getLost())
        self.assertFalse(wave.getWon())
        self.assertEqual(wave.getCitiesLeft(), 0)
        self.assertEqual(wave._falling_bombs, [])
        self.assertEqual(wave._rockets, [])

    def test_empty_ammunition_does_not_lose(self):
        wave = holding_wave()
        for silo in wave._silos:
            silo.setAmmo(0)
        wave.update(Input(), 1)
        self.assertFalse(wave.getLost())
        self.assertFalse(wave.getWon())
        self.assertEqual(wave.getScore(), 600)

    def test_win_waits_for_all_three_collections(self):
        wave = holding_wave()
        wave.update(Input(), 0)
        self.assertFalse(wave.getWon())
        wave._pending_bombs = []
        wave._falling_bombs = [models.Bomb(64, 300, 64, 128, 0, 0)]
        wave.update(Input(), 0)
        self.assertFalse(wave.getWon())
        wave._falling_bombs = []
        wave._rockets = [models.Rocket(64, 128, 500, 500)]
        wave.update(Input(), 0)
        self.assertFalse(wave.getWon())
        wave._rockets = []
        wave.update(Input(), 0)
        self.assertTrue(wave.getWon())
        self.assertFalse(wave.getLost())

    def test_short_rocket_finishes_before_older_long_rocket(self):
        wave = holding_wave()
        older = models.Rocket(64, 128, 1080, 840)
        newer = models.Rocket(64, 128, 64, 140)
        wave._rockets = [older, newer]
        for _ in range(340):
            wave.update(Input(), 1 / 60)
        self.assertIn(older, wave._rockets)
        self.assertNotIn(newer, wave._rockets)

    def test_max_radius_is_drawn_before_next_frame_removal(self):
        wave = holding_wave()
        rocket = models.Rocket(400, 400, 400, 400)
        wave._rockets = [rocket]
        for _ in range(6):
            wave.update(Input(), 1)
            if rocket.width == 200:
                break
        self.assertEqual(rocket.width, 200)
        self.assertIn(rocket, wave._rockets)
        view = View()
        wave.draw(view)
        self.assertIn(rocket, view.drawn)
        wave.update(Input(), 1 / 60)
        self.assertNotIn(rocket, wave._rockets)

    def test_supplied_immediate_and_doubletap_lose(self):
        for filename in ["immediate.json", "doubletap.json"]:
            with self.subTest(filename=filename):
                data = json.loads((PROJECT / "Data" / filename).read_text())
                wave = Wave(data)
                for _ in range(1800):
                    wave.update(Input(), 1 / 60)
                    if wave.getLost():
                        break
                self.assertTrue(wave.getLost())
                self.assertFalse(wave.getWon())
                self.assertEqual(wave.getCitiesLeft(), 0)
                self.assertEqual(wave._rockets, [])
                self.assertEqual(wave._falling_bombs, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
