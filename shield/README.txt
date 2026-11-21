missile shield / night post

which waves to run

from the folder containing shield, run either command, then press s:

    python3 shield nightpost.json
    python3 shield nightpost_calm.json

both waves turn on all four tools below. nightpost.json has 42 bombs at
62 pixels per second, while nightpost_calm.json is the slower intro with
18 bombs at 38 pixels per second. the supplied waves keep these tools off,
but the new interface and sound effects work in every wave.

1. postcards from tomorrow / forecasts

press f to show or hide the forecasts; they start on. an amber ring shows
where each falling bomb would be 1.5 seconds later at the current speed.
an amber time estimate above each threatened target shows the earliest
expected hit. basically, these help you aim ahead and spot the urgent bombs,
but the rings are just guides, so only real bombs can be intercepted.

2. sky bookmarks / saved aim spots

press b to save the current aim position, with up to three numbered markers.
tab moves the reticule through the saved spots, and x clears them. after
three saves, b replaces slot 1, then 2, then 3, and repeats. this gives you a
quick way back to a useful spot, but rockets already flying keep the aim
point from launch.

3. borrowed sky / a slow field

hold space to put a mint field around the reticule. bombs within 125 pixels
move at 22% of normal speed while charge is left. the meter holds 4 seconds
of charge, drains one second per real second while held, and restores 0.4
seconds per second when released. holding an empty meter does not refill it.

only nearby bombs slow down, so rockets, blasts, and scheduled drops keep
the usual timing. the field moves with your aim but cannot destroy bombs.
pausing freezes the charge meter too.

4. comet compost / ammo from interceptions

every three intercepted bombs automatically give one round to the silo with
the least ammo. ties go left to right, and no silo goes above ten rounds.
if all three are full, that group gives no ammo. the recycle card shows
progress and actual refunds, and a message says which silo got the round.

each interception also leaves a faint star, with the newest 18 points joined
into a small constellation. the stars are decoration, so they do not affect
collisions or keep a finished wave running.

5. the new interface

the game uses lowercase text, a darker sunset, separate menu cards, and
matching pause, result, and loading-error panels. the top bar shows cities,
ammo, and incoming threats, while each silo has an ammo badge and bar.
custom tools get their own status cards, so you can see forecast status,
saved spots, slow-field charge, and refund progress while playing. the pause
help only lists the tools enabled in the current wave.

6. sound effects

sounds mark the start of a wave, launches, blasts, interceptions, impacts,
empty silos, ammo refunds, and the final result. quick actions can have
overlapping cues. press v to mute or unmute; that choice sticks across
pauses, retries, and trips to the menu. pausing or muting stops active sounds,
and resuming does not replay the start cue.

the interface and sounds use the art, fonts, and wav files supplied with
the assignment.

other controls

    s   start the selected wave from the menu.
    c   start nightpost.json from the menu.
    p   pause and show help.
    r   resume from pause, or retry the same wave after a result or error.
    m   return to the menu from pause, results, or a loading error.

f, b, tab, x, and space only work when the matching custom tool is enabled.
v works on every screen. the usual arrow keys and number keys still handle
aiming and firing.
