from pathlib import Path
import csv,json,collections
s=Path(__file__).resolve().parent
rows=list(csv.DictReader((s/'trials.csv').open()))
assert len(rows)==12,'Need six valid two-sided trials'
comparisons={}
for baseline in ['LEGACY','SIEGE_CAST','GUARDIAN_PATTERN']:
 group=[r for r in rows if r['baseline']==baseline]
 assert len(group)==4
 for leg in ['0','1']:
  subset=[r for r in group if r['leg']==leg];assert len(subset)==2 and sum(float(x['damage']) for x in subset)>1000,'Insufficient actual combat'
 totals={}
 for brain in ['TACTICAL',baseline]:
  selected=[r for r in group if r['brain']==brain]
  totals[brain]={key:sum(float(r[key]) for r in selected) for key in ['damage','skills','controls','deaths','healed_hp_samples','moving_samples']}
  totals[brain]['mean_tick_ms_combined_both_brains']=sum(float(r['tick_ms_mean']) for r in selected)/len(selected)
 base=totals[baseline]['damage'];totals['tactical_damage_change_percent']=round(100*(totals['TACTICAL']['damage']/base-1),1) if base else None
 comparisons[baseline]=totals
result={'status':'PASS','trial_count':6,'duration_seconds_per_trial':30,'actors':6,'design':'fixed actors; two brain assignments exchanged per comparator; no respawn within trial','comparisons':comparisons,'limitations':['Small exploratory sample; not statistical significance or universal win rate.','Damage events can include overkill and reflect resources, not direct DPS normalization.','healed_hp_samples includes regeneration and potions; not attributed skill healing.','controls counts executed non-damage debuffs; not confirmed successful control effects.','SIEGE_CAST uses native SiegeSquadBrain.cast through a room combat adapter, not castle mission AI.','GUARDIAN_PATTERN ports Ares/Nyx attack priorities onto the same Players; not original NPC stats or full patrol AI.']}
(s/'comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
