"""Read-only native editor compatibility probes, isolated from the live client."""
import pathlib, sys, shutil, subprocess, re, json, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'airships'))
from read_map import Package
CLIENT=pathlib.Path('E:/l2')
BASE=ROOT.parent/'amber-l2/tools/l2editor/L2Editor'
SYSTEM=ROOT/'system'; SYSTEM.mkdir(exist_ok=True)
PACKAGES=ROOT/'packages'; PACKAGES.mkdir(exist_ok=True)
for p in BASE.iterdir():
    if p.is_file() and (p.suffix.lower() in ('.dll','.int') or p.name in ('UCC.exe','Engine.u','Core.u','Editor.u','Fire.u','UnrealEd.u','UT2003.ini','Default.ini','User.ini','DefUser.ini')):
        shutil.copy2(p,SYSTEM/p.name)
ini=(BASE/'UT2003.ini').read_text()
ini=ini.replace('[Core.System]','[Core.System]\n'+'\n'.join('Paths='+str(PACKAGES/('*.'+ext)).replace('\\','/') for ext in ('u','utx','usx','unr','uax','ukx')))
(SYSTEM/'Probe.ini').write_text(ini)
index={p.stem.lower():p for folder in ('maps','StaticMeshes','Textures','Sounds','SysTextures','system','Animations') for p in (CLIENT/folder).glob('*') if p.is_file()}
copied=[]
def stage(name):
    p=index.get(name.lower())
    if not p: return False
    raw=p.read_bytes()
    if raw[:4] != b'\xc1\x83\x2a\x9e':
        marker=raw[:28].decode('utf-16le',errors='ignore')
        if marker not in ('Lineage2Ver111','Lineage2Ver121'): return False
        key=172 if marker.endswith('111') else sum(map(ord,p.name.lower()))&255
        raw=bytes(x^key for x in raw[28:-20])
    (PACKAGES/p.name).write_bytes(raw);copied.append(p.name);return True
proof=[]
for name,cls,ext in [('Statues_S','StaticMesh','t3d'),('22_22','Level','t3d')]:
    stage(name); target=PACKAGES/index[name.lower()].name
    out=ROOT/('export-'+name);out.mkdir(exist_ok=True)
    attempts=[]
    for i in range(48):
        cmd=[str(SYSTEM/'UCC.exe'),'batchexport',str(target),cls,ext,str(out),'ini=Probe.ini','-unattended','-nosound']
        try:
            r=subprocess.run(cmd,cwd=SYSTEM,capture_output=True,text=True,errors='replace',timeout=20)
        except subprocess.TimeoutExpired:
            attempts.append({'timeout':True});break
        txt=r.stdout+r.stderr
        (ROOT/(name+'-attempt-'+str(i)+'.txt')).write_text(txt,encoding='utf-8')
        attempts.append({'exit':r.returncode,'tail':txt[-2000:]})
        m=re.search(r"Can't find file for package '([^']+)'",txt)
        if not m or m.group(1).lower() in {pathlib.Path(x).stem.lower() for x in copied} or not stage(m.group(1)): break
    proof.append({'package':name,'attempts':attempts,'exports':[p.name for p in out.iterdir()]})
    print(name,json.dumps(attempts[-1]),flush=True)
proof.append({'staged_dependencies':copied,'live_map_sha256':hashlib.sha256((CLIENT/'maps/22_22.unr').read_bytes()).hexdigest(),'original_copy_sha256':hashlib.sha256((ROOT/'22_22.original.unr').read_bytes()).hexdigest()})
(ROOT/'editor-probe.json').write_text(json.dumps(proof,indent=2))
