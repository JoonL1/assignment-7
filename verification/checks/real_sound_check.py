"""Exercise supplied wav assets through real Kivy with a dummy audio device."""
from pathlib import Path
import sys
import json

from qa_paths import PROJECT as project
from qa_paths import OUTPUT
sys.path.insert(0, str(project))
sys.argv = ['shield']
from app import MissileShield
from models import SoundEffects
from consts import GAME_WIDTH, GAME_HEIGHT

game = MissileShield(width=GAME_WIDTH, height=GAME_HEIGHT)
game.build()
bank = SoundEffects()
assert bank.getAvailable(), 'no real audio provider could load the wav assets'
assert len(bank._sounds) == 7
results = []
for cue in bank._sounds:
    bank.play(cue)
    assert bank._sounds[cue][0].playing, cue
    results.append({'cue': cue, 'source': bank._sounds[cue][0].source,
                    'voices_loaded': len(bank._sounds[cue]),
                    'playing_state_observed': True})
bank.setEnabled(False)
for cue in bank._sounds:
    assert not any(voice.playing for voice in bank._sounds[cue]), cue
bank.setEnabled(True)
bank.play('launch')
assert bank._sounds['launch'][1].playing
bank.stop()
print('pass: all 7 cues loaded and played through real Kivy; mute stopped all')
print('audio device is dummy, so this verifies requests rather than audibility')
(OUTPUT / 'real_audio.json').write_text(json.dumps({
    'cues': results, 'cue_count': len(results),
    'mute_stopped_all_voices': True,
    'next_voice_played_after_unmute': True,
    'audio_driver': 'dummy', 'audible_audio_verified': False
}, indent=2) + '\n')
