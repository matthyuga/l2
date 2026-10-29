from pathlib import Path
import re,json
s=Path(__file__).resolve().parent;t=(s/'live-audit.txt').read_text()
rows=t.splitlines()
def positive(key):return any(int(n)>0 for n in re.findall(re.escape(key)+r'=(\d+)',t))
checks={
 'six_live_bots':len(rows)==6,
 'native_mp_potion_used':positive('item_used_728'),
 'native_hp_potion_used':positive('item_used_1539'),
 'native_cp_potion_used':positive('item_used_5592'),
 'native_blessed_spiritshots_used':positive('item_used_3952'),
 'warrior_soulshots_used':any('mage=false' in row and re.search(r'item_used_1467=[1-9]',row) for row in rows),
 'magic_skills_executed':positive('skill_executed_1239') and positive('skill_executed_1230'),
 'physical_skills_executed':positive('skill_executed_3') and positive('skill_executed_255'),
 'native_summon_and_transfer_pain':any('summon=true TP=true' in row and 'skill_executed_1333=' in row and 'skill_executed_1262=' in row for row in rows),
 'healing_executed':positive('skill_executed_1401'),
}
result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks}
(s/'combat-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
