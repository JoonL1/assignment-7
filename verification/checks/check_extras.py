"""Scratch-only independent Night Post behavior checks."""
import ast
import itertools
from pathlib import Path
import unittest

import check_core as core

Wave = core.Wave
Input = core.Input
View = core.View
models = core.models
consts = core.consts
FEATURES = ['forecast', 'bookmarks', 'time_bubble', 'recycling']


def custom_wave(flags=None, speed=100):
    if flags is None:
        flags = {name: True for name in FEATURES}
    return Wave({'speed': speed,
                 'features': flags,
                 'missiles': [{'x': 64, 'target': 0, 'time': 1000}]})


def add_center_bomb(wave, x=400, y=500):
    bomb = models.Bomb(x, y, x, 118, 0, 1)
    wave._falling_bombs.append(bomb)
    return bomb


class ExtrasBehavior(unittest.TestCase):
    def test_original_wave_ignores_all_bonus_keys(self):
        wave = core.holding_wave(100)
        bomb = add_center_bomb(wave)
        wave._target.x = 400
        wave._target.y = 500
        wave.update(Input(['f','b','tab','x','spacebar','space']), 1)
        self.assertFalse(wave.getCustomEnabled())
        self.assertFalse(wave._forecast_visible)
        self.assertEqual(wave._bookmarks, [])
        self.assertEqual(wave._bubble_seconds, consts.BUBBLE_CAPACITY)
        self.assertEqual(wave._bubble_fraction, 0)
        self.assertAlmostEqual(bomb.y, 400)
        for i in range(3):
            wave._record_interception(bomb)
        self.assertEqual(wave._constellation_points, [])
        self.assertEqual(wave._recycled_count, 0)

    def test_forecast_toggle_and_draw_do_not_mutate_gameplay(self):
        wave = custom_wave({'forecast': True})
        bomb = add_center_bomb(wave)
        wave._rockets = [models.Rocket(64,128,500,600)]
        before = (bomb.x,bomb.y,len(wave._falling_bombs),
                  len(wave._rockets),wave.getScore(),wave._elapsed_time)
        wave.draw(View())
        after = (bomb.x,bomb.y,len(wave._falling_bombs),
                 len(wave._rockets),wave.getScore(),wave._elapsed_time)
        self.assertEqual(before,after)
        self.assertTrue(wave._forecast_visible)
        wave.update(Input(['f']), 0)
        self.assertFalse(wave._forecast_visible)
        wave.update(Input(['f'], []), 0)
        self.assertFalse(wave._forecast_visible)
        wave.update(Input(['f']), 0)
        self.assertTrue(wave._forecast_visible)

    def test_forecast_clamps_before_impact_without_moving(self):
        bomb = models.Bomb(200,130,200,118,0,1)
        future = bomb.getFuturePosition(consts.FORECAST_SECONDS,100)
        self.assertEqual(future,(200,118))
        self.assertEqual((bomb.x,bomb.y),(200,130))
        self.assertFalse(bomb.getArrived())
        self.assertEqual(bomb.getFuturePosition(1000,0),(200,130))

    def test_bookmark_empty_recall_and_clear_are_safe(self):
        wave = custom_wave({'bookmarks': True})
        wave.update(Input(['tab']),0)
        self.assertEqual(wave._bookmarks,[])
        wave.update(Input(['x']),0)
        self.assertEqual(wave._next_bookmark,0)
        self.assertEqual(wave._replacement_bookmark,0)

    def test_bookmark_replacement_and_cyclic_recall(self):
        wave = custom_wave({'bookmarks': True})
        points = [(100,200),(200,300),(300,400),(400,500),(500,600),(600,700)]
        for x,y in points:
            wave._target.x = x
            wave._target.y = y
            wave.update(Input(['b']),0)
            self.assertLessEqual(len(wave._bookmarks),3)
        self.assertEqual(wave._bookmarks,points[-3:])
        for point in points[-3:] * 2:
            wave.update(Input(['tab']),0)
            self.assertEqual((wave._target.x,wave._target.y),point)
        wave.update(Input(['x']),0)
        wave._target.x = 123
        wave._target.y = 456
        wave.update(Input(['b']),0)
        self.assertEqual(wave._bookmarks,[(123,456)])

    def test_bookmarks_respect_limits_and_do_not_redirect_rockets(self):
        wave = custom_wave({'bookmarks': True})
        wave._target.x = -10
        wave._target.y = 100
        wave.update(Input(['b']),0)
        self.assertEqual(wave._bookmarks[0],(8,136))
        wave._target.x = 2000
        wave._target.y = 2000
        wave.update(Input(['b']),0)
        self.assertEqual(wave._bookmarks[1],(1144,856))
        wave.update(Input(['1']),0)
        rocket = wave._rockets[0]
        wave.update(Input(['tab']),0)
        self.assertEqual((wave._target.x,wave._target.y),(8,136))
        rocket.update(10)
        self.assertEqual((rocket.x,rocket.y),(1144,856))

    def test_bubble_slows_only_inside_and_does_not_slow_clock_or_rocket(self):
        wave = custom_wave({'time_bubble': True})
        wave._target.x = 400
        wave._target.y = 500
        inside = add_center_bomb(wave)
        outside = add_center_bomb(wave,700,500)
        rocket = models.Rocket(64,128,1144,856)
        wave._rockets = [rocket]
        wave.update(Input(['spacebar'],[]),1)
        self.assertAlmostEqual(inside.y,478)
        self.assertAlmostEqual(outside.y,400)
        self.assertAlmostEqual(wave._elapsed_time,1)
        self.assertAlmostEqual(wave._bubble_seconds,3)
        distance = ((rocket.x-64)**2+(rocket.y-128)**2)**0.5
        self.assertAlmostEqual(distance,500)

    def test_bubble_radius_boundary(self):
        wave = custom_wave({'time_bubble': True})
        wave._target.x = 400
        wave._target.y = 500
        wave._bubble_requested = True
        wave._update_bubble_charge(.1)
        exactly_on = models.Bomb(525,500,525,118,0,1)
        just_outside = models.Bomb(525.001,500,525.001,118,0,1)
        self.assertAlmostEqual(wave._get_bomb_speed(exactly_on),22)
        self.assertEqual(wave._get_bomb_speed(just_outside),100)

    def test_bomb_spawning_after_charge_runs_out_is_not_slowed(self):
        wave = Wave({'speed':100,
                     'features':{'time_bubble':True},
                     'missiles':[{'x':64,'target':0,'time':.006}]})
        wave._target.x = 64
        wave._target.y = 856
        wave._bubble_seconds = .002
        frame_seconds = 1 / 120
        wave.update(Input(['spacebar'],[]),frame_seconds)
        self.assertEqual(len(wave._falling_bombs),1)
        expected_movement = (frame_seconds - .006) * 100
        expected_y = consts.GAME_HEIGHT - expected_movement
        self.assertAlmostEqual(wave._falling_bombs[0].y,expected_y)
        self.assertAlmostEqual(wave._bubble_seconds,0)

    def test_charge_depletion_partial_step_and_recharge(self):
        wave = custom_wave({'time_bubble': True})
        wave._target.x = 400
        wave._target.y = 500
        bomb = add_center_bomb(wave)
        wave._bubble_seconds = .25
        wave.update(Input(['space'],[]),1)
        self.assertAlmostEqual(wave._bubble_seconds,0)
        self.assertAlmostEqual(bomb.y,419.5)
        wave.update(Input(['spacebar'],[]),.25)
        self.assertAlmostEqual(wave._bubble_seconds,0)
        self.assertAlmostEqual(bomb.y,394.5)
        wave.update(Input(),1)
        self.assertAlmostEqual(wave._bubble_seconds,.4)
        wave._falling_bombs = []
        wave.update(Input(),20)
        self.assertEqual(wave._bubble_seconds,consts.BUBBLE_CAPACITY)
        self.assertEqual(wave._bubble_fraction,0)

    def test_refund_lowest_ammo_and_no_duplicate_for_overlap(self):
        wave = custom_wave({'recycling':True})
        for silo,amount in zip(wave._silos,[7,2,5]):
            silo.setAmmo(amount)
        first = models.Rocket(400,500,400,500)
        second = models.Rocket(410,500,410,500)
        first.update(2)
        second.update(2)
        wave._rockets = [first,second]
        for x in [395,400,405]:
            add_center_bomb(wave,x,500)
        wave.update(Input(),.001)
        self.assertEqual(wave._falling_bombs,[])
        self.assertEqual(wave._intercepted_count,3)
        self.assertEqual(wave._recycled_count,1)
        self.assertEqual(wave.getAmmoCounts(),[7,3,5])
        self.assertEqual(len(wave._constellation_points),3)
        wave.update(Input(),.001)
        self.assertEqual(wave._intercepted_count,3)

    def test_refund_cap_and_stable_tie_break(self):
        wave = custom_wave({'recycling':True})
        bomb = models.Bomb(100,300,100,118,0,1)
        for _ in range(3):
            wave._record_interception(bomb)
        self.assertEqual(wave.getAmmoCounts(),[10,10,10])
        self.assertEqual(wave._recycled_count,0)
        for silo in wave._silos:
            silo.setAmmo(9)
        for _ in range(3):
            wave._record_interception(bomb)
        self.assertEqual(wave.getAmmoCounts(),[10,9,9])
        self.assertEqual(wave._recycled_count,1)

    def test_constellation_caps_at_eighteen_latest(self):
        wave = custom_wave({'recycling':True})
        for i in range(25):
            wave._record_interception(models.Bomb(i,300,i,118,0,1))
        self.assertEqual(len(wave._constellation_points),18)
        self.assertEqual(wave._constellation_points[0],(7,300))
        self.assertEqual(wave._constellation_points[-1],(24,300))
        self.assertEqual(wave.getAmmoCounts(),[10,10,10])

    def test_all_partial_flag_combinations_safe(self):
        for flags in itertools.product([False,True],repeat=4):
            mapping = dict(zip(FEATURES,flags))
            with self.subTest(flags=mapping):
                wave = custom_wave(mapping)
                wave._silos[0].setAmmo(5)
                bomb = add_center_bomb(wave)
                wave._target.x = 400
                wave._target.y = 500
                wave.update(Input(['b','tab','f','spacebar']),.01)
                wave.draw(View())
                self.assertEqual(wave.getCustomEnabled(),any(flags))
                self.assertEqual(bool(wave._bookmarks),mapping['bookmarks'])
                if not mapping['time_bubble']:
                    self.assertEqual(wave._bubble_fraction,0)
                if not mapping['forecast']:
                    self.assertFalse(wave._forecast_visible)
                for _ in range(3):
                    wave._record_interception(bomb)
                expected_ammo = 6 if mapping['recycling'] else 5
                self.assertEqual(wave.getAmmoCounts()[0],expected_ammo)
                wave.draw(View())

    def test_wave_accesses_only_own_hidden_fields(self):
        tree = ast.parse((core.PROJECT / 'wave.py').read_text())
        bad = []
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute) and node.attr.startswith('_'):
                if isinstance(node.value,ast.Name) and node.value.id == 'self':
                    continue
                bad.append((node.lineno,ast.unparse(node)))
        self.assertEqual(bad,[])


if __name__ == '__main__':
    unittest.main(verbosity=2)
