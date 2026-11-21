"""real kivy checks for the lowercase interface redesign.

Run in the existing Kivy environment with SDL_VIDEODRIVER=offscreen.
This observes rendered GLabels after texture synchronization. It does not
assert the old wording, menu layout, or any particular implementation.
"""
from pathlib import Path
import argparse
import itertools
import json
import os
import sys


from qa_paths import PROJECT, OUTPUT as EVIDENCE
OUTPUT = EVIDENCE / 'interface'
OUTPUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--snapshots', action='store_true')
options = parser.parse_args()
sys.argv = ['shield']
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(PROJECT))

from app import MissileShield
from wave import Wave
from consts import *
from game2d import GLabel
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window


class Keys:
    def __init__(self, pressed=(), down=()):
        self.pressed = set(pressed)
        self.down = set(down) | self.pressed

    def is_key_pressed(self, key):
        return key in self.pressed

    def is_key_down(self, key):
        return key in self.down


game = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
game.build()
game.view.size = (GAME_WIDTH, GAME_HEIGHT)
game.start()
original_label_draw = GLabel.draw
drawn_labels = []
cases = []
issues = []


def captured_label_draw(label, view):
    drawn_labels.append(label)
    original_label_draw(label, view)


GLabel.draw = captured_label_draw


def glyph_box(label):
    """Use actual glyph texture bounds, not a retained larger GLabel box."""
    texture = label._label
    return [label.x + texture.x, label.y + texture.y,
            label.x + texture.right, label.y + texture.top]


def overlap(first, second):
    width = min(first[2], second[2]) - max(first[0], second[0])
    height = min(first[3], second[3]) - max(first[1], second[1])
    if width <= 2 or height <= 2:
        return False
    first_area = (first[2] - first[0]) * (first[3] - first[1])
    second_area = (second[2] - second[0]) * (second[3] - second[1])
    return width * height > 0.08 * min(first_area, second_area)


def record_screen(name, save=False):
    """Draw several actual frames, then inspect only the final frame."""
    for unused in range(5):
        Clock.tick()
        drawn_labels.clear()
        game.view.clear()
        game.draw()
        Builder.sync()
        Clock.tick_draw()
        Window.dispatch('on_draw')
        Window.flip()
    observed = []
    unique_ids = set()
    for label in drawn_labels:
        if id(label) in unique_ids or not label.text.strip():
            continue
        unique_ids.add(id(label))
        box = glyph_box(label)
        observed.append({'label': label, 'text': label.text,
                         'bounds': box, 'font': label.font_name})
        if label.text != label.text.lower():
            issues.append(f'{name}: uppercase visible text: {label.text!r}')
        if (box[0] < -0.5 or box[1] < -0.5 or
                box[2] > GAME_WIDTH + 0.5 or
                box[3] > GAME_HEIGHT + 0.5):
            issues.append(f'{name}: text outside screen: {label.text!r}, {box}')

    overlay_ids = {id(label) for label in game._screen_labels}
    overlay_ids.update([id(game._title), id(game._text)])
    compare = observed
    if game._state in [STATE_PAUSED, STATE_COMPLETE]:
        # Wave labels behind the modal are not visible through its opaque card.
        compare = [item for item in observed
                   if id(item['label']) in overlay_ids]
    for first, second in itertools.combinations(compare, 2):
        if overlap(first['bounds'], second['bounds']):
            issues.append(f'{name}: overlapping labels: '
                          f'{first["text"]!r} / {second["text"]!r}')
    cases.append({'name': name, 'labels': [
        {key: value for key, value in item.items() if key != 'label'}
        for item in observed]})
    if options.snapshots or save:
        game.view.export_to_png(str(OUTPUT / (name + '.png')))
    print(f'checked {name}: {len(observed)} drawn labels', flush=True)


def activate(data):
    game._clear_messages()
    game._wave = Wave(data)
    game._state = STATE_ACTIVE
    return game._wave


def load(filename):
    game._begin_loading(filename)
    game._load_wave()
    if game._state != STATE_ACTIVE:
        raise AssertionError(f'Could not load {filename}')
    return game._wave


def press(key):
    game.input._capture_key(None, (ord(key), key), key, [])
    game._refresh(0)
    game.input._release_key(None, (ord(key), key))


if not isinstance(game.title, str) or game.title != game.title.lower():
    issues.append(f'window title is not lowercase: {game.title!r}')

record_screen('welcome', save=True)
press('v')
record_screen('welcome_muted')
press('v')
game._begin_loading('easy.json')
record_screen('loading')
game._load_wave()
wave = game._wave
wave.update(Keys(), 4)
record_screen('standard_active', save=True)
game._pause_wave()
record_screen('standard_paused', save=True)
game._continue_wave()

wave = load('nightpost.json')
wave.update(Keys(), 6)
wave._target.x = 400
wave._target.y = 500
wave.update(Keys(['b', '1']), 0)
wave.update(Keys(['tab'], ['spacebar']), 0.3)
record_screen('custom_active', save=True)
press('v')
record_screen('custom_muted')
press('v')
wave.update(Keys(['x']), 0)
record_screen('custom_notice_clear')
wave.update(Keys(['tab']), 0)
record_screen('custom_notice_empty_bookmarks')
wave._silos[0].setAmmo(0)
wave.update(Keys(['1']), 0)
record_screen('custom_notice_empty_silo')
game._pause_wave()
record_screen('custom_paused', save=True)
game._continue_wave()

feature_names = ['forecast', 'bookmarks', 'time_bubble', 'recycling']
help_markers = {'forecast': 'f /', 'bookmarks': 'b /',
                'time_bubble': 'space /', 'recycling': 'interceptions'}
for combination in itertools.product([False, True], repeat=4):
    flags = dict(zip(feature_names, combination))
    wave = activate({'speed': 40, 'features': flags, 'missiles': [
        {'x': 140, 'target': 1, 'time': 0},
        {'x': 1000, 'target': 7, 'time': 1000}]})
    wave.update(Keys(['b'], ['spacebar']), 2)
    name = 'features_' + ''.join(str(int(value)) for value in combination)
    help_rows = wave.getHelpRows()
    if len(help_rows) != sum(combination):
        issues.append(f'{name}: help row count does not match enabled tools')
    help_text = '\n'.join(help_rows)
    for feature, marker in help_markers.items():
        if (marker in help_text) != flags[feature]:
            issues.append(f'{name}: incorrect help availability for {feature}')
    if help_text != help_text.lower():
        issues.append(f'{name}: help contains uppercase text')
    record_screen(name)

wave = activate({'speed': 40, 'missiles': []})
wave.update(Keys(), 0)
game._finish_wave(True)
record_screen('win', save=True)

wave = load('immediate.json')
while not wave.getLost():
    wave.update(Keys(), 0.1)
game._finish_wave(False)
record_screen('loss', save=True)

game._begin_loading('missing_UI_test.json')
game._load_wave()
record_screen('missing_file', save=True)

game._begin_loading('malformed.json')
game._load_wave()
record_screen('malformed_file')

game._selected_wave_file = 'nightpost.json'
game._show_load_error('Could Not Create The Wave.',
                     'RuntimeError: ' + ('WIDEWords ' * 70),
                     'Check The Wave Values And Use One Complete Shield Folder.')
record_screen('long_error', save=True)

GLabel.draw = original_label_draw
evidence = {'screens_checked': len(cases), 'help_combinations_checked': 16,
            'cases': cases, 'issues': issues}
(OUTPUT / 'interface_report.json').write_text(json.dumps(evidence, indent=2))
print(f'\nchecked {len(cases)} screen states, including all 16 feature sets')
if issues:
    print('\n'.join(issues))
    raise SystemExit(1)
print('PASS: lowercase visible text, actual glyph bounds, no major text overlap')
