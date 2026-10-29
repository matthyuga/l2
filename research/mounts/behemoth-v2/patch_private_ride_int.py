"""Correct localized animation overrides that supersede class defaults."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parent;LAB=R.parents[2];source=LAB.parent/'l2/system-hud/LineageMonster.int';target=R/'LineageMonster-native-ride.int'
sys.path.insert(0,str(LAB/'research/dust2-animation-study/native'))
from write_l2_animation import chunks
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(source);original=source.read_bytes();assert original[:28].decode('utf-16-le')=='Lineage2Ver111';plain=bytes(x^0xac for x in original[28:])
match=re.search(rb'^\[strider\]\r?\n.*?(?=^\[|\Z)',plain,re.M|re.S);assert match
section=match.group();old_section=section;newline=b'\r\n' if b'\r\n'in section else b'\n'
tables={'WaitAnimName':'atkwait','AtkWaitAnimName':'atkwait','WalkAnimName':'Walk','RunAnimName':'run','DeathAnimName':'death','DeathWaitAnimName':'deathwait'}
for key,clip in tables.items():
 for index in range(8):
  entry=f'{key}[{index}]={clip}'.encode();pattern=rb'^'+re.escape(f'{key}[{index}]'.encode())+rb'=[^\r\n]*'
  if re.search(pattern,section,re.M):section=re.sub(pattern,entry,section,flags=re.M)
  else:section=section.rstrip(b'\r\n')+newline+entry+newline+newline
changed=plain[:match.start()]+section+plain[match.end():]
encoded=original[:28]+bytes(x^0xac for x in changed);target.write_bytes(encoded);decoded=bytes(x^0xac for x in target.read_bytes()[28:]);assert decoded==changed
new_match=re.search(rb'^\[strider\]\r?\n.*?(?=^\[|\Z)',decoded,re.M|re.S)
assert decoded[:new_match.start()]==plain[:match.start()] and decoded[new_match.end():]==plain[match.end():]
info=chunks(R/'native-source/LineageMonsters3/MeshAnimation/antaras_ex_a_anim.psa')['ANIMINFO'];clips=[info[2][i*info[0]:i*info[0]+64].rstrip(b'\0').decode()for i in range(info[1])]
assert 'wait'not in {x.lower()for x in clips}
for key,clip in tables.items():
 assert clip.lower() in {x.lower()for x in clips}
 for index in range(8):assert f'{key}[{index}]={clip}'.encode()in section
assert sha(source)==before
report={'passed':True,'originalWaitLine':re.search(rb'^WaitAnimName\[0\]=[^\r\n]*',old_section,re.M).group().decode(),'correctedWait':'WaitAnimName[0]=atkwait','waitAbsentFromBehemoth':True,'allConfiguredClipsExist':True,'allOtherSectionsByteIdentical':True,'mainClientUnchanged':True,'originalSHA256':before,'stagedSHA256':sha(target),'encryptionRoundtripExact':True,'installed':False,'nativeGameVisualVerified':False}
(R/'native-ride-int-fix.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
