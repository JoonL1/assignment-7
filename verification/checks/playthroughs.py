import json
from pathlib import Path
import check_core as qa
from qa_paths import OUTPUT

folder = qa.PROJECT / 'Data'
outcomes = []
for filename in ['easy.json','medium.json','hard.json','immediate.json',
                 'staggered.json','doubletap.json','nightpost.json',
                 'nightpost_calm.json']:
    wave = qa.Wave(json.loads((folder/filename).read_text()))
    targeted = set()
    cooldown = 0
    frames = 0
    while not wave.getLost() and not wave.getWon() and frames < 180*60:
        pressed = []
        cooldown -= 1/60
        choices = []
        for bomb in wave._falling_bombs:
            if id(bomb) not in targeted:
                choices.append(bomb)
        if choices and cooldown <= 0:
            chosen = min(choices, key=lambda b:b.getRemainingTime(wave._bomb_speed))
            future = chosen.getFuturePosition(1.6,wave._bomb_speed)
            wave._target.x = future[0]
            wave._target.y = future[1]
            wave._keep_target_inside()
            silos = []
            for i,silo in enumerate(wave._silos):
                if silo.getAmmo() > 0:
                    silos.append((abs(silo.x-wave._target.x),i))
            if silos:
                chosen_silo = min(silos)[1]
                pressed = [str(chosen_silo+1)]
                targeted.add(id(chosen))
                cooldown = .25
        wave.update(qa.Input(down=pressed,pressed=pressed),1/60)
        frames += 1
    assert wave.getLost() or wave.getWon(), filename
    print(filename, 'won' if wave.getWon() else 'lost', 'cities',wave.getCitiesLeft(),
          'score',wave.getScore(),'time',round(wave._elapsed_time,2),
          'refunds',wave._recycled_count)
    outcomes.append({'file': filename, 'won': wave.getWon(),
                     'cities_left': wave.getCitiesLeft(),
                     'score': wave.getScore(),
                     'elapsed_seconds': round(wave._elapsed_time, 2),
                     'ammo_refunds': wave._recycled_count})

report = {'mode': 'scripted aim with graphics stubs', 'waves': outcomes,
          'wave_count': len(outcomes),
          'all_won': all(item['won'] for item in outcomes)}
(OUTPUT / 'playthroughs.json').write_text(json.dumps(report, indent=2) + '\n')
