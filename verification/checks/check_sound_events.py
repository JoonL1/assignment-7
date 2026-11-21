"""Scratch checks that actual Wave events request sound once at the right time."""
import unittest

import check_core as core


class CueRecorder:
    def __init__(self):
        self.events = []
        self.enabled = True
        self.stops = 0

    def play(self, cue):
        if self.enabled:
            self.events.append(cue)

    def stop(self):
        self.stops += 1

    def getEnabled(self):
        return self.enabled

    def getAvailable(self):
        return True

    def setEnabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.stop()


def make_wave(custom=False):
    data = {'speed': 10,
            'missiles': [{'x': 64, 'target': 0, 'time': 1000}]}
    if custom:
        data['features'] = {'recycling': True}
    wave = core.Wave(data)
    wave._sounds = CueRecorder()
    return wave


class WaveSoundChecks(unittest.TestCase):
    def test_start_cue_requires_explicit_start(self):
        wave = make_wave()
        self.assertEqual(wave._sounds.events, [])
        wave.startSounds()
        self.assertEqual(wave._sounds.events, ['start'])

    def test_launch_cue_follows_one_key_press_not_held_frames(self):
        wave = make_wave()
        wave.update(core.Input(['1']), 0)
        wave.update(core.Input(['1'], pressed=[]), 0)
        self.assertEqual(wave._sounds.events, ['launch'])
        self.assertEqual(wave._silos[0].getAmmo(), 9)
        self.assertEqual(len(wave._rockets), 1)

    def test_empty_silo_only_plays_empty_feedback(self):
        wave = make_wave()
        wave._silos[0].setAmmo(0)
        wave.update(core.Input(['1']), 0)
        self.assertEqual(wave._sounds.events, ['empty'])
        self.assertEqual(wave._silos[0].getAmmo(), 0)
        self.assertEqual(wave._rockets, [])

    def test_explosion_plays_once_at_arrival_not_every_growth_step(self):
        wave = make_wave()
        wave._rockets = [core.models.Rocket(64, 128, 64, 129)]
        for _ in range(10):
            wave._step_world(1 / 120)
        self.assertTrue(wave._rockets[0].getExploding())
        self.assertEqual(wave._sounds.events, ['explode'])

    def test_interception_plays_once_even_with_two_collision_passes(self):
        wave = make_wave()
        rocket = core.models.Rocket(300, 300, 300, 300)
        rocket.update(0)
        wave._rockets = [rocket]
        wave._falling_bombs = [core.models.Bomb(300, 300, 192, 118, 0, 1)]
        wave._resolve_interceptions()
        wave._resolve_interceptions()
        self.assertEqual(wave._sounds.events, ['intercept'])
        self.assertEqual(wave._falling_bombs, [])

    def test_city_impact_plays_once_and_destroys_the_target(self):
        wave = make_wave()
        city = wave._targets[1]
        bomb = core.models.Bomb(city.x, city.top, city.x, city.top, 0, 1)
        bomb.update(0, 10)
        wave._falling_bombs = [bomb]
        wave._resolve_impacts()
        wave._resolve_impacts()
        self.assertEqual(wave._sounds.events, ['impact'])
        self.assertFalse(city.getAlive())

    def test_refund_cue_only_when_an_ammo_round_is_actually_added(self):
        wave = make_wave(custom=True)
        wave._silos[0].setAmmo(9)
        wave._recycle_ammunition()
        wave._recycle_ammunition()
        self.assertEqual(wave._sounds.events, ['reward'])
        self.assertEqual(wave._silos[0].getAmmo(), 10)

    def test_mute_and_stop_public_api_do_not_change_gameplay(self):
        wave = make_wave()
        wave.setSoundsEnabled(False)
        self.assertFalse(wave.getSoundsEnabled())
        wave.update(core.Input(['1']), 0)
        self.assertEqual(wave._sounds.events, [])
        self.assertEqual(wave._silos[0].getAmmo(), 9)
        wave.setSoundsEnabled(True)
        self.assertTrue(wave.getSoundsEnabled())
        wave.update(core.Input(['2']), 0)
        self.assertEqual(wave._sounds.events, ['launch'])
        wave.stopSounds()
        self.assertEqual(wave._sounds.stops, 2)

    def test_wave_finish_stops_old_cues_then_requests_one_result_cue(self):
        for won, cue in [(True, 'reward'), (False, 'impact')]:
            with self.subTest(won=won):
                wave = make_wave()
                wave.finishSounds(won)
                self.assertEqual(wave._sounds.stops, 1)
                self.assertEqual(wave._sounds.events, [cue])


if __name__ == '__main__':
    unittest.main(verbosity=2)
