"""keep test paths separate from the game, so the bundle can move anywhere."""
import os
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1]
PROJECT = Path(os.environ.get('SHIELD_PROJECT', BUNDLE.parent / 'shield'))
PROJECT = PROJECT.expanduser().resolve()
OUTPUT = Path(os.environ.get('SHIELD_EVIDENCE_OUTPUT', BUNDLE / 'evidence'))
OUTPUT = OUTPUT.expanduser().resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)

