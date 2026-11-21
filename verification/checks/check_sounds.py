"""Scratch sound behavior checks; graphics and audio are replaced by spies."""
import contextlib
import io
from pathlib import Path
import unittest

import check_core as core


class SoundSpy:
    instances = []
    fail_loading = None

    def __init__(self, source):
        if source == self.fail_loading:
            raise OSError('test audio loader unavailable')
        self.source = source
        self.volume = 1
        self.playing = False
        self.play_count = 0
        self.stop_count = 0
        self.fail_play = False
        self.fail_stop = False
        self.instances.append(self)

    def play(self):
        if self.fail_play:
            raise OSError('test audio playback unavailable')
        if self.playing:
            raise AssertionError('a playing voice must stop before replay')
        self.play_count += 1
        self.playing = True

    def stop(self):
        if self.fail_stop:
            raise OSError('test audio stop unavailable')
        self.stop_count += 1
        self.playing = False


class SoundBankChecks(unittest.TestCase):
    def setUp(self):
        self.old_sound = core.models.Sound
        core.models.Sound = SoundSpy
        SoundSpy.instances = []
        SoundSpy.fail_loading = None

    def tearDown(self):
        core.models.Sound = self.old_sound

    def test_all_cues_preloaded_from_supplied_wavs_without_playing(self):
        bank = core.models.SoundEffects()
        self.assertEqual(len(SoundSpy.instances), 21)
        self.assertTrue(bank.getEnabled())
        self.assertTrue(bank.getAvailable())
        for sound in SoundSpy.instances:
            self.assertTrue((core.PROJECT / 'Sounds' / sound.source).is_file())
            self.assertEqual(sound.play_count, 0)
            self.assertGreater(sound.volume, 0)
            self.assertLessEqual(sound.volume, 0.42)

    def test_three_launches_overlap_and_fourth_safely_reuses_first(self):
        bank = core.models.SoundEffects()
        for _ in range(3):
            bank.play('launch')
        voices = bank._sounds['launch']
        self.assertEqual([sound.play_count for sound in voices], [1, 1, 1])
        self.assertTrue(all(sound.playing for sound in voices))
        bank.play('launch')
        self.assertEqual([sound.play_count for sound in voices], [2, 1, 1])

    def test_mute_stops_playback_blocks_new_cues_and_can_resume(self):
        bank = core.models.SoundEffects()
        bank.play('launch')
        bank.play('explode')
        bank.setEnabled(False)
        self.assertFalse(bank.getEnabled())
        self.assertFalse(any(sound.playing for sound in SoundSpy.instances))
        before = sum(sound.play_count for sound in SoundSpy.instances)
        bank.play('launch')
        self.assertEqual(sum(s.play_count for s in SoundSpy.instances), before)
        bank.setEnabled(True)
        bank.play('launch')
        self.assertEqual(sum(s.play_count for s in SoundSpy.instances), before + 1)

    def test_unknown_cue_is_harmless(self):
        bank = core.models.SoundEffects()
        bank.play('not a real event')
        self.assertFalse(any(sound.playing for sound in SoundSpy.instances))

    def test_missing_asset_disables_only_affected_cues(self):
        SoundSpy.fail_loading = 'ping.wav'
        with contextlib.redirect_stdout(io.StringIO()):
            bank = core.models.SoundEffects()
        self.assertNotIn('intercept', bank._sounds)
        self.assertNotIn('reward', bank._sounds)
        self.assertTrue(bank.getAvailable())
        bank.play('intercept')
        bank.play('launch')
        self.assertTrue(bank._sounds['launch'][0].playing)

    def test_failed_play_stops_other_voices_and_preserves_other_cues(self):
        bank = core.models.SoundEffects()
        bank.play('launch')
        voices = list(bank._sounds['launch'])
        voices[1].fail_play = True
        with contextlib.redirect_stdout(io.StringIO()):
            bank.play('launch')
        self.assertNotIn('launch', bank._sounds)
        self.assertFalse(any(sound.playing for sound in voices))
        bank.play('explode')
        self.assertTrue(bank._sounds['explode'][0].playing)

    def test_failed_stop_does_not_block_other_voices_or_other_cues(self):
        bank = core.models.SoundEffects()
        bank.play('launch')
        bank.play('launch')
        bank.play('explode')
        voices = list(bank._sounds['launch'])
        voices[0].fail_stop = True
        with contextlib.redirect_stdout(io.StringIO()):
            bank.stop()
        self.assertNotIn('launch', bank._sounds)
        self.assertFalse(voices[1].playing)
        self.assertFalse(bank._sounds['explode'][0].playing)


if __name__ == '__main__':
    unittest.main(verbosity=2)
