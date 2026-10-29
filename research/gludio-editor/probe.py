"""Explicit editor-only water dependency repair and native full-map probe."""
from pathlib import Path
import sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'gludio-sky'))
from package_tools import Edit,Package
pk=ROOT/'Packages'
p=Edit(pk/'water.usx')
changes=[]
for e in p.imports:
 old=dict(e)
 if e['outer']==0 and e['name']=='watertest':e['name']='L2_skies'
 elif e['name']=='water' and e['cl']=='Package':e['name']='Textures'
 elif e['name']=='Water01' and e['cl']=='Texture':e['name']='WhiteCloud'
 if old!=e:p.name(e['name']);changes.append({'before':old,'after':dict(e)})
if changes:p.save(pk/'water.usx')
(ROOT/'editor-only-compatibility.json').write_text(json.dumps({'water.usx':changes,'reason':'Missing watertest.water.Water01 in live client; fallback only in isolated editor package. Not installed.'},indent=2))
cmd=[str(ROOT/'System/UCC.exe'),'batchexport',str(pk/'24_19.unr'),'Level','t3d',str(ROOT/'Exports'),'ini=GludioEditor.ini','-unattended','-nosound']
try:
 r=subprocess.run(cmd,cwd=ROOT/'System',capture_output=True,text=True,errors='replace',timeout=90)
 (ROOT/'native-load-with-compatibility.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
 print('Exit',r.returncode,(r.stdout+r.stderr)[-7000:])
except subprocess.TimeoutExpired as e:
 (ROOT/'native-load-with-compatibility.txt').write_bytes((e.stdout or b'')+(e.stderr or b''))
 print('Timeout: native load not proven')
