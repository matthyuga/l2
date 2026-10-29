"""Stage and verify the current core patch and a separate native client profile."""
import pathlib,hashlib,json,zipfile,shutil,subprocess,os,copy
R=pathlib.Path(__file__).resolve().parent;LAB=R.parents[2];CLIENT=LAB.parent/'l2'
sysroot=CLIENT/'system-hud';profile=R/'client-lab';profile.mkdir(exist_ok=True)
backup=LAB/'backups/behemoth-v2-20261019';backup.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# Build a complete staging JAR from the CURRENT active JAR, preserving all other entries.
active=LAB/'server/libs/GameServer.jar';before=backup/'GameServer.jar'
if not before.exists():shutil.copy2(active,before)
oldhash=sha(active);compiled=LAB/'build/behemoth-v2-core';replacements={p.relative_to(compiled).as_posix():p for p in (compiled/'org').rglob('*.class')}
staged=R/'GameServer.behemoth.jar';changed=[];added=[]
with zipfile.ZipFile(active) as a,zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED) as b:
 old_names=set(a.namelist())
 for entry in a.infolist():
  data=replacements[entry.filename].read_bytes() if entry.filename in replacements else a.read(entry.filename)
  if entry.filename in replacements and data!=a.read(entry.filename):changed.append(entry.filename)
  b.writestr(entry,data)
 for name,p in replacements.items():
  if name not in old_names:b.writestr(name,p.read_bytes());added.append(name)
with zipfile.ZipFile(active) as a,zipfile.ZipFile(staged) as b:
 assert b.testzip() is None
 for name in a.namelist():
  if name not in replacements:assert a.read(name)==b.read(name)
assert all(n.startswith('org/l2jmobius/gameserver/') for n in changed+added)
(R/'core-patch-manifest.json').write_text(json.dumps({'baseSHA256':oldhash,'stagedSHA256':sha(staged),'changed':changed,'added':added,'allOtherEntriesIdentical':True},indent=2),encoding='utf8')

# Hard links are restricted to immutable game resources. The system profile is a real copy.
resources=['Animations','Maps','Music','Sounds','StaticMeshes','SysTextures','Textures','Voice']
linked=0
for name in resources:
 origin=CLIENT/name
 if not origin.exists():continue
 for p in origin.rglob('*'):
  if not p.is_file():continue
  dest=profile/name/p.relative_to(origin);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():
   try:os.link(p,dest);linked+=1
   except OSError:shutil.copy2(p,dest)
system=profile/'system'
if not system.exists():shutil.copytree(sysroot,system)
mainhash=sha(sysroot/'npcgrp.dat')
import sys
sys.path.insert(0,str(LAB/'research/amber-l2/scripts'));from contract_dat import Catalog
codec=LAB/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(args):subprocess.run([str(v) for v in args],check=True,capture_output=True)
run([codec,'-o',R/'npcgrp.before.raw',sysroot/'npcgrp.dat']);cat=Catalog(R/'npcgrp.before.raw','npcgrp.xml','Interlude')
assert not any(row['npc_id']==59091 for row in cat.rows),'Reserved client display ID already used'
row=copy.deepcopy(next(row for row in cat.rows if row['npc_id']==29069))
row.update(npc_id=59091,class_name='LineageMonster3.antaras_ex_a',mesh_name='BHMTransport.BehemothMesh',texture_name=3,texture_name_items=[{'param_texture_name':'BHMTransport.Mat'+str(i)} for i in range(3)],deco_effect=0,deco_effect_items=[],attack_effect='')
cat.append([row],R/'npcgrp.after.raw')
run([codec,'-c','encode','-p','413','-o',R/'npcgrp.dat',R/'npcgrp.after.raw']);run([codec,'-o',R/'npcgrp.roundtrip.raw',R/'npcgrp.dat']);assert (R/'npcgrp.after.raw').read_bytes()==(R/'npcgrp.roundtrip.raw').read_bytes()
shutil.copy2(R/'npcgrp.dat',system/'npcgrp.dat');shutil.copy2(R/'BHMTransport.u',system/'BHMTransport.u')
assert sha(sysroot/'npcgrp.dat')==mainhash
(R/'client-installation.json').write_text(json.dumps({'profile':str(profile),'displayId':59091,'nativeServerId':902791,'mainNpcgrpUnchanged':True,'allOriginalRecordsPreserved':cat.count,'newRecords':1,'datRoundtrip':True,'linkedImmutableResourceFiles':linked,'engineDllUnchanged':sha(system/'Engine.dll')==sha(sysroot/'Engine.dll'),'packageSHA256':sha(system/'BHMTransport.u'),'nativeClientVerified':False},indent=2),encoding='utf8')
print('BEHEMOTH_LAB_PREPARED',len(changed),'changed core entries,',len(added),'new;',cat.count,'original NPC records preserved')
