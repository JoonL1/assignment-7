missile shield / extensions
===========================
authors: joon lee (jl4875) + richard li (rl998)

how to play
-----------
open a terminal in the folder that contains shield, then run:

    python3 shield

press s for classic mode (easy.json by default).
press c for the endless night post campaign.

other wave files
----------------
run any of these commands from the same folder:

    python3 shield nightpost_calm.json
    python3 shield nightpost.json
    python3 shield nightpost_campaign.json

then press s at the menu to play the wave you chose.
pressing c always opens the endless campaign instead.

nightpost_calm.json: a slower custom wave with the extra tools.
nightpost.json: a harder custom wave with the extra tools.
nightpost_campaign.json: three rounds followed by harder repeats.

controls
--------
arrow keys    move the aiming target
1 / 2 / 3     fire from the left, middle, or right silo
p             pause
r             resume after pausing or restart after final results
n or r        finish the score tally and go to the next campaign round
m             return to the main menu from pause or results
v             turn sound on or off

night post also has these controls:

f             show or hide the bomb forecasts
b             save the current aim position (up to 3 positions)
tab           jump to the next saved aim position
x             clear the saved aim positions
space         hold to slow nearby bombs; release to recharge

extensions
----------
1. sound effects
   rocket launches, explosions, bomb hits, and aircraft have sound effects.
   the sounds come from the supplied wav files. rockets and cities have
   different sounds and pressing v mutes/unmutes sound effects.

2. animated score
   after a wave, the game counts the number of leftover rockets and cities.
   each rocket is worth 5 points and each surviving city is worth 100 points.
   the rocket and city pictures pulse as their counts go up. the final
   results number also counts up to the player's total score.
   if every city is lost, the tally still counts any leftover rockets.

3. multiple waves and personal best
   the campaign has three rounds followed by harder repeats.
   cities that are destroyed in one round stay destroyed in later rounds.
   the surviving cities and total score carry over to the next round.
   the game saves the personal best in Data/highscore.txt when possible.

4. extra enemies (campaign only)
   planes fly across the screen and drop bombs at scheduled times.
   the plane picture faces the direction that the plane travels.
   drones dive, climb, and change direction during their flight.
   satellites hover and can drop at least three bombs each.
   some orange enemy bombs split into two or three smaller bombs.
   a rocket explosion can destroy an aircraft and stop its future drops.
   the aircraft and their bomb orders are set in the custom campaign json.
   none of these extra enemies appear in the supplied classic waves.

5. night post tools (custom waves only)
   forecasts: press f to see predicted bomb positions about 1.5 seconds
   ahead. these guides aren't real bombs and can't damage anything.

   bookmarks: press b to remember an aim position, tab to recall one,
   or x to clear all saved positions. the limit is three bookmarks.

   slow field: hold space to slow nearby enemy bombs. the field uses
   charge while active and refills after space is released.

   ammo recycling: every three bomb interceptions can return one
   rocket to the silo with the least ammunition.

6. visual effects
   rockets use the missile picture and point toward in their vector direction.
   rocket blasts expand over time, and some interceptions draw a fading
   gold signal toward a surviving city. split bombs also leave a brief
   circle. the menus, status cards, and score screens use simple animations.

gameplay rules
-----------------------
all classic waves keep the original gameplay rules and speeds.
bombs travel toward cities or silos. the player fires rockets with 1, 2,
or 3; the silos don't fire on their own. rockets explode at the saved aim
point, and a bomb is removed if its center enters the growing blast.

the player loses as soon as all six cities are destroyed. the player wins
when at least one city remains and all enemy bombs are gone. a win also
waits for any rockets and explosions still on the screen to finish.

credits and files
-----------------
the original game framework, sprites, fonts, and wav sounds come from the
cs 1110 missile shield package/assignment. the right-facing plane image
is a flipped copy of the supplied plane picture.