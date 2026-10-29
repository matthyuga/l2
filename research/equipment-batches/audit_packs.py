from pathlib import Path
import hashlib,json,re,shutil,subprocess,collections
ROOT=Path(__file__).resolve().parent
SOURCE=Path('D:/L2Remoto/Entrada/Equipamiento')
EXTRACT=ROOT/'originals';EXTRACT.mkdir(parents=True,exist_ok=True)
TOOL=SOURCE/'tools/7zr.exe'
packs=[]
for batch in range(1,4):
    manifest=json.loads((SOURCE/f'Tanda-{batch:02d}'/'download-manifest.json').read_text(encoding='utf-8'))
    for index,row in enumerate(manifest['files'],1):
        key=f'b{batch}-{index:02d}-'+re.sub('[^a-z0-9]+','-',row['name'].lower()).strip('-')
        folder=EXTRACT/key;folder.mkdir(exist_ok=True)
        archive=Path(row['path']);assert hashlib.sha256(archive.read_bytes()).hexdigest()==row['sha256']
        for e in row['contents']:
            parts=Path(e['path']).parts;assert '..' not in parts and not Path(e['path']).is_absolute()
        marker=folder/'.extracted'
        if not marker.exists():
            p=subprocess.run([str(TOOL),'x','-y',f'-o{folder}',str(archive)],capture_output=True)
            assert p.returncode==0,(row['name'],p.stdout[-300:],p.stderr)
            marker.write_text(row['sha256'])
        files=[]
        for file in folder.rglob('*'):
            if file.is_file() and file.name!='.extracted':
                files.append({'path':str(file),'relative':str(file.relative_to(folder)),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'suffix':file.suffix.lower()})
        packs.append({'key':key,'name':row['name'],'category':row['category'],'batch':batch,'archive':str(archive),'archive_sha256':row['sha256'],'folder':str(folder),'files':files})
(ROOT/'audit.json').write_text(json.dumps(packs,indent=2,ensure_ascii=False),encoding='utf-8')
for pack in packs:
    interesting=[f['relative'] for f in pack['files'] if f['suffix'] in ['.txt','.dat','.xml','.sql','.ini','.htm','.html']]
    assets=[f['relative'] for f in pack['files'] if f['suffix'] in ['.u','.ukx','.utx','.usx']]
    print(pack['key'],'ASSETS',len(assets),'DATA',json.dumps(interesting,ensure_ascii=True),flush=True)
