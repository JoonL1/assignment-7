shield verification
===================

this folder is the supporting evidence, so keep it outside the shield folder
that gets submitted. the game needs the complete shield folder from shield.zip;
these checks do not rebuild missing game files or install python packages.

run it again
------------

use the python 3 environment that already runs the course game2d examples, with
kivy and introcs installed. put verification/ and shield/ beside each other,
open a terminal in that parent folder, and run:

    python3 verification/run_checks.py --project shield --snapshots

if the folders live somewhere else, pass the actual path of shield:

    python3 verification/run_checks.py --project "/path/to/shield" --snapshots

on linux without a desktop, the environment must support the sdl2 offscreen
video driver; then append --headless. leave --headless off on mac or windows.
the real rendering checks can open a window when a desktop is available.

    python3 verification/run_checks.py --project shield --snapshots --headless

the default output is verification/evidence/, so a new run replaces those
reports. to keep the supplied evidence, choose another output folder:

    python3 verification/run_checks.py --project shield \
        --snapshots --output verification/my_run

the runner uses the same python executable for every check. each suite gets a
fresh process, because the numerical tests install small graphics stubs and
those stubs must never leak into the real kivy checks. loading failure tests
work on a temporary copy, so they do not add broken test waves to the game.

what gets checked
-----------------

* all python files compile, without writing bytecode into the game folder.
* 74 unittest cases cover game rules, optional features, sound triggers,
  audio lifecycle, and wave loading/retry/menu recovery.
* 56 of those cases use graphics stubs or audio spies for deterministic
  behavior checks; 18 use real kivy graphics/input, with audio spies in 8.
* 32 real kivy screen states check lowercase visible text, actual glyph bounds,
  and major text overlap; this includes all 16 feature flag combinations.
* 12 real kivy color cases construct, reassign, and draw rgba/rgb tuples and
  lists on GRectangle, GEllipse, and GPath.
* all 7 sound cues load and enter the playing state through real kivy, and
  mute stops them; a dummy audio device is used, so this is not a listening
  test of speakers or volume balance.
* 8 scripted playthroughs exercise all valid supplied and custom waves with
  graphics stubs; the saved results show wins, cities, scores, and refunds.
* the style audit checks method docs, physical body lengths, 80-character
  lines, and tabs. only three exact lines already over 80 characters in the
  supplied template are exempt: app.py original lines 4 and 21, and wave.py
  original line 24. each exemption is listed in the report; new or changed
  long lines still fail. the audit also checks 17 protected starter files and
  all 43 original image/font/sound assets against the original upload.
* the template check compares all 15 original documentation blocks and 91
  original comment tokens verbatim, including section placement. the only
  allowed text substitutions fill the two module-header placeholders with
  the existing authors/date of each module. all 151 added method blocks keep
  their exact source, and the executable ast and token sequences stay the
  same as the completed version before this restoration.

the automated bounds check flags substantial text overlap, but the screenshots
also let a person inspect the layout. the scripted aim is a repeatable test
driver, so the recorded wins are not a claim about difficulty for a player.

what settled the review questions
--------------------------------

the actual original shield(1).zip contains these six valid wave files, all with
the same two top-level keys: speed and missiles.

    easy.json          9 missiles
    medium.json       21 missiles
    hard.json         30 missiles
    immediate.json     9 missiles
    staggered.json     9 missiles
    doubletap.json    18 missiles

malformed.json is the supplied negative example. parsing it is supposed to
fail at line 23, column 3, so a blanket test that every json file must parse
would incorrectly reject the starter package. the two custom files are also
loaded by the actual app in the loading checks.

the bundled game2d/gobject.py accepts both tuple and list in is_color at line
35. the linecolor setter at lines 242-253 and fillcolor setter at lines
281-292 use that validator and convert the values into kivy Color objects.
the real rendering probe checks the behavior, in addition to reading source.
therefore the delivered code keeps the supplied missiles schema and its valid
tuple colors, while the original framework and supplied json stay unchanged.

evidence files
--------------

evidence/summary.json
    machine-readable results, python/dependency versions, exact hashes of all
    game files and check scripts, timestamps, and project-change detection.

evidence/logs/*.log
    raw stdout/stderr for every suite, including named unittest results.

evidence/interface/interface_report.json
    text and actual glyph bounds observed for each of the 32 screen states.

evidence/interface/*.png
    actual kivy screenshots; --snapshots saves all 32 states.

evidence/loading/*.png
    loading success, missing file, malformed json, invalid schema, unexpected
    constructor failure, and long error-message screenshots.

evidence/compatibility.json and evidence/color_compatibility.png
    original json findings and all 12 real color-rendering cases.

evidence/real_audio.json and evidence/playthroughs.json
    cue/voice results and the eight scripted game outcomes.

evidence/submission_audit.json
    method/body counts, source-style findings, original-file checks, and the
    three explicit width exemptions for unchanged original template lines.

evidence/template_preservation.json
    exact original specifications/comments, section-placement results,
    unchanged added method blocks, and executable-code comparisons.

evidence/source_comparison.json
    current output hashes and executable-code comparisons against the latest
    uploaded completed python modules, before restoring the template text.

starter_manifest.json
    hashes recorded directly from the uploaded original starter zip, plus the
    exact source excerpts of color validation. rerunning these checks does
    not require the original zip to be on the machine.

template_preservation_manifest.json
    raw original specifications/comments from shield (2).zip, the permitted
    name/date substitutions, hashes of the filled code and added methods,
    and the three exact original long lines. its resource comparison records
    that all 17 protected files and 43 assets match the earlier starter zip.

the supplied evidence is for the file hashes in summary.json. if any game file
changes later, rerun the checks so the evidence matches that version.

check the complete zip
----------------------

to compare every file in shield.zip with the recorded hashes, run:

    python3 verification/verify_archive.py --archive shield.zip

this checks the exact shield/ names, contents, and file count, so a missing
custom wave or asset makes it fail. it writes evidence/archive_verification.json
with the sha256 of the game zip and the associated summary. it never extracts
or changes the archive.

play it yourself
----------------

from the parent folder of shield, run:

    python3 shield

that uses normal audio output. the automated runner uses dummy audio only
inside its own child processes, so it does not change your shell settings.
