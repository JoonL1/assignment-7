"""real kivy checks for loading diagnostics; outside the submission."""
from pathlib import Path
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

from qa_paths import PROJECT, OUTPUT
temporary = tempfile.TemporaryDirectory(prefix='shield-checks-')
project = Path(temporary.name) / 'shield'
shutil.copytree(PROJECT, project,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
sys.path.insert(0, str(project))
sys.argv = ['shield']
os.chdir('/')
import app as app_module
from app import MissileShield
from consts import *
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window

game = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
game.build()
game.view.size = (GAME_WIDTH, GAME_HEIGHT)
game.start()
game._sounds_enabled = False
renders = OUTPUT / 'loading'
renders.mkdir(exist_ok=True)
real_wave = app_module.Wave


def screen_text():
    labels = list(game._screen_labels)
    if game._text is not None:
        labels.append(game._text)
    return '\n'.join(label.text for label in labels)


def press(key):
    game.input._capture_key(None, (ord(key), key), key, [])
    game._refresh(1 / 60)
    game.input._release_key(None, (ord(key), key))


def render(name):
    for _ in range(5):
        Clock.tick()
        game.view.clear()
        game.draw()
        Builder.sync()
        Clock.tick_draw()
        Window.dispatch('on_draw')
        Window.flip()
    game.view.export_to_png(str(renders / (name + '.png')))


class LoadingChecks(unittest.TestCase):
    def setUp(self):
        app_module.Wave = real_wave
        game._open_menu()
        game.input._keystate.clear()
        game.input._keypress.clear()
        game.input._keyrelease.clear()
        game.input._keycount = 0

    def tearDown(self):
        app_module.Wave = real_wave

    def load(self, filename):
        game._begin_loading(filename)
        self.assertEqual(game._state, STATE_LOADING)
        game._refresh(1 / 60)

    def assert_error(self, stage, detail):
        self.assertEqual(game._state, STATE_COMPLETE)
        self.assertIsNone(game._wave)
        self.assertEqual(game._text.text, stage)
        self.assertIn(detail, screen_text())
        self.assertEqual(screen_text(), screen_text().lower())
        label_texts = [label.text for label in game._screen_labels]
        for control_text in ['r', 'retry', 'm', 'back to menu']:
            self.assertIn(control_text, label_texts)

    def assert_labels_fit(self):
        labels = list(game._screen_labels) + [game._text]
        for label in labels:
            self.assertGreaterEqual(label.left, 216,
                                    repr((label.text, label.left, label.width)))
            self.assertLessEqual(label.right, GAME_WIDTH - 216,
                                 repr((label.text, label.right, label.width)))
            self.assertGreaterEqual(label.bottom, 155)
            self.assertLessEqual(label.top, 709)

    def test_01_standard_load(self):
        self.load('easy.json')
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertFalse(game._wave.getCustomEnabled())

    def test_02_custom_load_from_real_c_press(self):
        press('c')
        self.assertEqual(game._state, STATE_LOADING)
        game._refresh(1 / 60)
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertTrue(game._wave.getCustomEnabled())
        self.assertEqual(len(game._wave._pending_bombs), 42)
        for _ in range(240):
            game._refresh(1 / 60)
        self.assertEqual(len(game._wave._falling_bombs), 2)
        render('nightpost_loaded')

    def test_03_calm_load(self):
        self.load('nightpost_calm.json')
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertEqual(len(game._wave._pending_bombs), 18)

    def test_04_missing_file_and_layout(self):
        self.load('missing_level.json')
        self.assert_error('could not read the wave file.', 'filenotfounderror')
        self.assertIn('data/missing_level.json', screen_text())
        render('missing_file')
        self.assert_labels_fit()

    def test_05_malformed_json_and_layout(self):
        self.load('malformed.json')
        self.assert_error('could not read the wave file.', 'valueerror')
        self.assertIn('could not read json: data/malformed.json',
                      ' '.join(screen_text().split()))
        render('malformed_json')
        self.assert_labels_fit()

    def test_06_bad_schema_and_layout(self):
        (project / 'Data/bad_schema.json').write_text(
            json.dumps({'speed': -1, 'missiles': []}))
        self.load('bad_schema.json')
        self.assert_error('could not create the wave.', 'valueerror')
        self.assertIn('wave speed must be greater than zero.',
                      ' '.join(screen_text().split()))
        render('bad_schema')
        self.assert_labels_fit()

    def test_07_unexpected_constructor_error(self):
        def broken_constructor(data):
            raise RuntimeError('test-only setup failure')
        app_module.Wave = broken_constructor
        self.load('nightpost.json')
        self.assert_error('could not create the wave.',
                          'runtimeerror: test-only setup failure')
        self.assertNotIn('could not read json', screen_text())
        render('setup_exception')
        self.assert_labels_fit()

    def test_08_long_multiline_error_and_layout(self):
        def broken_constructor(data):
            raise RuntimeError('details\n' + 'W' * 300 + '\n' + 'extra ' * 100)
        app_module.Wave = broken_constructor
        self.load('nightpost.json')
        self.assert_error('could not create the wave.', 'runtimeerror')
        detail_labels = [label for label in game._screen_labels
                         if label.y in [468, 440, 412]]
        self.assertEqual(len(detail_labels), 3)
        self.assertTrue(detail_labels[-1].text.endswith('...'))
        self.assertTrue(all('\n' not in label.text for label in detail_labels))
        render('long_exception')
        self.assert_labels_fit()

    def test_09_retry_after_missing_file_is_fixed(self):
        filename = 'retry_missing.json'
        self.load(filename)
        self.assert_error('could not read the wave file.', 'filenotfounderror')
        shutil.copyfile(project / 'Data/nightpost.json', project / 'Data' / filename)
        press('r')
        self.assertEqual(game._state, STATE_LOADING)
        game._refresh(1 / 60)
        self.assertEqual(game._state, STATE_ACTIVE)
        self.assertEqual(len(game._wave._pending_bombs), 42)
        self.assertEqual(game._selected_wave_file, filename)

    def test_10_menu_after_error(self):
        self.load('missing_again.json')
        self.assert_error('could not read the wave file.', 'filenotfounderror')
        press('m')
        self.assertEqual(game._state, STATE_INACTIVE)
        self.assertIsNone(game._wave)
        self.assertIsNotNone(game._title)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LoadingChecks)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    print('render directory:', renders)
    sys.exit(0 if result.wasSuccessful() else 1)
