missile shield / extensions

run this from the folder containing shield

    python3 shield

press s for the chosen regular wave (easy.json by default)
press c for the custom endless night post campaign

custom waves to try

    python3 shield nightpost_calm.json
    python3 shield nightpost.json
    python3 shield nightpost_campaign.json

press s after choosing a wave from the command line
nightpost_calm.json is the easier custom wave
nightpost.json is a single harder custom wave
nightpost_campaign.json is the full endless campaign with special enemies

extensions

1. sound effects
launches and hits and explosions use the supplied wav files
<<<<<<< HEAD
score counting has a quiet tick sound and v toggles sound at any time

2. animated score counting
at the end of a successful wave each leftover rocket is worth 5 points
and each living city is worth 100 points
small rocket and city pictures appear one at a time as points are added
=======
rockets and cities get different score sounds and v toggles sound
planes use afterburner.wav (drones and satellites use their own wav files)

2. animated score counting
after a win or a loss each leftover rocket is worth 5 points
and each living city is worth 100 points
the rocket and city pictures pulse on each point beat
visible counts rise with the score so each item is easy to recognize
the final results number counts from zero to the actual score too
>>>>>>> eea581d (Update Missile Shield)
in campaign mode press n or r to finish the tally and start the next round

3. multiple waves + personal best
press c for the campaign (three designed rounds followed by harder repeats)
destroyed cities remain gone between rounds
surviving cities and total score carry forward
personal best is saved in Data/highscore.txt when possible
it appears on the main menu even after restarting the app

4. extra threats only in custom campaign waves
a few orange bombs split into 2 or 3 smaller bombs during the fall
<<<<<<< HEAD
rounds 2 and 3 also have planes and bouncing drones and a satellite
these enemies drop bombs at times and target slots set in the campaign json
shooting the moving enemy with a normal rocket blast stops future drops
custom missiles can have different speeds and accelerate or slow down
regular supplied waves never include these new threats or speed changes
=======
all three aircraft appear in round one (with more in later rounds)
satellites hover and launch at least 3 bombs from their scheduled orders
planes face the direction of flight using a flipped supplied sprite
drones dive then change direction abruptly (with short zigzag moves)
all enemy bombs come from times and targets listed in the custom json
shooting the moving enemy with a normal rocket blast stops future drops
the supplied missile image turns toward the target during flight
all bombs in each wave use its json speed (later rounds are faster)
regular supplied waves never include these new threats
>>>>>>> eea581d (Update Missile Shield)

5. extra animations and night post tools
intercepting a bomb can make a fading gold signal toward a saved city
splitting bombs also create a fading circle
f toggles predicted bomb positions about 1.5 seconds ahead
b saves one aiming position (up to 3) and tab recalls the next one
x clears the saved positions
hold space to slow nearby bombs and release to refill the meter
every 3 intercepted bombs can return 1 rocket to the least full silo
these tools are enabled only by custom json feature flags

controls

arrows move the aiming target
1 / 2 / 3 fire from the corresponding silo
p pauses and r resumes
<<<<<<< HEAD
r restarts after a final result
=======
r restarts after final results (the last score animates first)
>>>>>>> eea581d (Update Missile Shield)
n or r starts the next campaign round after score counting
m returns to the main menu from paused or completed screens
v turns the supplied game sounds on or off

original gameplay is unchanged for supplied waves
one city must survive to win and the wave must have no bombs left
the wave also waits for all remaining rockets and explosions to end
losing every city ends the game immediately

all graphics and audio come from the supplied assignment package
