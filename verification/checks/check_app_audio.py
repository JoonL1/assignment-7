"""Real Kivy input/UI lifecycle checks with a deterministic audio provider spy."""
from pathlib import Path
import sys
import unittest

from qa_paths import PROJECT as project
sys.path.insert(0, str(project))
sys.argv = ['shield']
import models
from app import MissileShield
from consts import *


class AudioSpy:
    def __init__(self, source):
        self.source = source
        self.volume = 1
        self.playing = False
        self.play_count = 0
        self.stop_count = 0

    def play(self):
        self.play_count += 1
        self.playing = True

    def stop(self):
        self.stop_count += 1
        self.playing = False


models.Sound = AudioSpy
game = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
game.build()
game.view.size = (GAME_WIDTH, GAME_HEIGHT)
game.start()


def frame():
    game._refresh(1 / 60)


def press(key):
    game.input._capture_key(None, (ord(key), key), key, [])
    frame()
    game.input._release_key(None, (ord(key), key))


def count(bank, cue):
    return sum(voice.play_count for voice in bank._sounds[cue])


def playing(bank):
    return any(voice.playing for voices in bank._sounds.values()
               for voice in voices)


class AppAudioChecks(unittest.TestCase):
    def setUp(self):
        game._open_menu()
        game._sounds_enabled = True
        game._open_menu()
        game.input._keystate.clear()
        game.input._keypress.clear()
        game.input._keyrelease.clear()
        game.input._keycount = 0

    def tearDown(self):
        game._open_menu()

    def load(self, key='s'):
        press(key)
        self.assertEqual(game._state, STATE_LOADING)
        frame()
        self.assertEqual(game._state, STATE_ACTIVE)
        return game._wave

    def win(self):
        game._wave._pending_bombs = []
        game._wave._falling_bombs = []
        game._wave._rockets = []
        frame()
        self.assertEqual(game._state, STATE_COMPLETE)

    def test_menu_mute_persists_into_custom_wave_and_unmute_is_silent(self):
        press('v')
        self.assertFalse(game._sounds_enabled)
        self.assertIn('sound off', game._audio_label.text)
        wave = self.load('c')
        self.assertFalse(wave.getSoundsEnabled())
        self.assertEqual(count(wave._sounds, 'start'), 0)
        press('v')
        self.assertTrue(wave.getSoundsEnabled())
        self.assertFalse(playing(wave._sounds))
        press('1')
        self.assertEqual(count(wave._sounds, 'launch'), 1)
        self.assertTrue(playing(wave._sounds))
        press('v')
        self.assertFalse(playing(wave._sounds))
        self.assertIn('sound off', wave._audio_label.text)

    def test_start_cue_once_and_v_held_does_not_toggle_again(self):
        wave = self.load()
        self.assertEqual(count(wave._sounds, 'start'), 1)
        for _ in range(4):
            frame()
        self.assertEqual(count(wave._sounds, 'start'), 1)
        game.input._capture_key(None, (ord('v'), 'v'), 'v', [])
        frame()
        self.assertFalse(game._sounds_enabled)
        for _ in range(4):
            frame()
        self.assertFalse(game._sounds_enabled)
        game.input._release_key(None, (ord('v'), 'v'))

    def test_pause_stops_audio_and_muted_resume_keeps_the_same_wave(self):
        wave = self.load()
        press('1')
        self.assertTrue(playing(wave._sounds))
        press('p')
        self.assertEqual(game._state, STATE_PAUSED)
        self.assertFalse(playing(wave._sounds))
        elapsed = wave._elapsed_time
        press('v')
        self.assertFalse(wave.getSoundsEnabled())
        self.assertIn('sound off', game._audio_label.text)
        press('r')
        self.assertEqual(game._state, STATE_CONTINUE)
        frame()
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertIs(game._wave, wave)
        self.assertEqual(wave._elapsed_time, elapsed)
        press('2')
        self.assertEqual(wave._silos[1].getAmmo(), 9)
        self.assertEqual(count(wave._sounds, 'launch'), 1)
        self.assertEqual(count(wave._sounds, 'start'), 1)

    def test_win_cue_once_and_retry_preserves_mute(self):
        wave = self.load()
        self.win()
        self.assertEqual(count(wave._sounds, 'reward'), 1)
        for _ in range(4):
            frame()
        self.assertEqual(count(wave._sounds, 'reward'), 1)
        press('v')
        self.assertFalse(playing(wave._sounds))
        press('r')
        self.assertEqual(game._state, STATE_LOADING)
        frame()
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertIsNot(game._wave, wave)
        self.assertFalse(game._wave.getSoundsEnabled())
        self.assertEqual(count(game._wave._sounds, 'start'), 0)
        self.assertFalse(playing(wave._sounds))

    def test_loss_cue_once_and_menu_stops_it(self):
        wave = self.load()
        for city in wave._cities:
            city.destroy()
        frame()
        self.assertEqual(game._state, STATE_COMPLETE)
        self.assertEqual(count(wave._sounds, 'impact'), 1)
        for _ in range(4):
            frame()
        self.assertEqual(count(wave._sounds, 'impact'), 1)
        self.assertTrue(playing(wave._sounds))
        press('m')
        self.assertEqual(game._state, STATE_INACTIVE)
        self.assertIsNone(game._wave)
        self.assertFalse(playing(wave._sounds))

    def test_muted_menu_to_standard_and_new_unmuted_load(self):
        wave = self.load()
        press('v')
        press('p')
        press('m')
        self.assertFalse(game._sounds_enabled)
        self.assertIn('sound off', game._audio_label.text)
        new_wave = self.load()
        self.assertFalse(new_wave.getSoundsEnabled())
        self.assertEqual(count(new_wave._sounds, 'start'), 0)
        press('p')
        press('m')
        press('v')
        third_wave = self.load()
        self.assertTrue(third_wave.getSoundsEnabled())
        self.assertEqual(count(third_wave._sounds, 'start'), 1)

    def test_close_stops_all_audio(self):
        wave = self.load()
        press('1')
        press('2')
        self.assertTrue(playing(wave._sounds))
        game.on_stop()
        self.assertFalse(playing(wave._sounds))

    def test_close_before_bootstrap_is_harmless(self):
        not_started = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
        not_started.on_stop()


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AppAudioChecks)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    print('app audio lifecycle checks:', result.testsRun,
          'passed:', result.wasSuccessful())
    sys.exit(0 if result.wasSuccessful() else 1)
