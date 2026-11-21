"""check the supplied json schema and render colors with actual game2d/kivy."""
import hashlib
import json
import math
from pathlib import Path
import sys

from qa_paths import BUNDLE, OUTPUT, PROJECT


sys.path.insert(0, str(PROJECT))
sys.argv = ['shield']
from app import MissileShield
from consts import GAME_WIDTH, GAME_HEIGHT
from game2d import GEllipse, GLabel, GPath, GRectangle
from game2d.gobject import is_color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder


manifest = json.loads((BUNDLE / 'starter_manifest.json').read_text())
json_results = []
for relative, reference in manifest['protected_files'].items():
    if not relative.startswith('Data/'):
        continue
    path = PROJECT / relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256']
    if relative == 'Data/malformed.json':
        try:
            json.loads(path.read_text())
        except json.JSONDecodeError as error:
            result = {'path': relative, 'expected_invalid_json': True,
                      'error_line': error.lineno, 'error_column': error.colno}
        else:
            raise AssertionError('the supplied malformed example became valid')
    else:
        data = json.loads(path.read_text())
        assert set(data) == {'speed', 'missiles'}, relative
        assert isinstance(data['missiles'], list), relative
        result = {'path': relative, 'keys': sorted(data),
                  'missile_count': len(data['missiles'])}
    json_results.append(result)
    print('checked source json:', result)

game = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
game.build()
game.view.size = (GAME_WIDTH, GAME_HEIGHT)
shapes = []
labels = []
color_results = []
for column, container in enumerate((tuple, list)):
    for row, channels in enumerate((3, 4)):
        color = container([0.22, 0.67, 0.86, 0.55][:channels])
        expected = list(color) + ([1.0] if channels == 3 else [])
        assert is_color(color), (container.__name__, channels)
        for index, kind in enumerate((GRectangle, GEllipse, GPath)):
            x = 160 + column * 550 + index * 135
            y = 600 - row * 280
            keywords = {'linecolor': color, 'fillcolor': color, 'linewidth': 3}
            if kind is GPath:
                keywords['points'] = [x - 50, y - 30, x, y + 40, x + 50, y - 30]
            else:
                keywords.update(x=x, y=y, width=95, height=95)
            shape = kind(**keywords)
            for attribute in ('linecolor', 'fillcolor'):
                assert all(math.isclose(a, b, abs_tol=1e-7)
                           for a, b in zip(getattr(shape, attribute), expected))
                setattr(shape, attribute, color)
            shapes.append(shape)
            text = f'{container.__name__} {channels} / {kind.__name__.lower()}'
            labels.append(GLabel(text=text, x=x, y=y-85, font_size=13,
                                 font_name='Roboto-Regular.ttf',
                                 fillcolor='white'))
            color_results.append({'shape': kind.__name__,
                                  'container': container.__name__,
                                  'channels': channels,
                                  'linecolor': shape.linecolor,
                                  'fillcolor': shape.fillcolor})
            print('checked real kivy color:', text)

for unused in range(5):
    Clock.tick()
    game.view.clear()
    GRectangle(x=GAME_WIDTH / 2, y=GAME_HEIGHT / 2,
               width=GAME_WIDTH, height=GAME_HEIGHT,
               fillcolor=(0.04, 0.07, 0.12, 1)).draw(game.view)
    for shape in shapes + labels:
        shape.draw(game.view)
    Builder.sync()
    Clock.tick_draw()
    Window.dispatch('on_draw')
    Window.flip()
game.view.export_to_png(str(OUTPUT / 'color_compatibility.png'))
report = {'json_sources': json_results, 'color_cases': color_results,
          'color_case_count': len(color_results),
          'real_kivy_rendered': True,
          'source_evidence': manifest['color_source_evidence']}
(OUTPUT / 'compatibility.json').write_text(json.dumps(report, indent=2) + '\n')
print('pass: six original waves use missiles; malformed stays intentionally invalid')
print('pass: all 12 tuple/list, rgb/rgba, shape cases drew with real kivy')
