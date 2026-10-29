from pathlib import Path
import json,hashlib,shutil
d=Path(__file__).resolve().parent.parent;m=json.loads((d/'installation.json').read_text());rows=[r for r in m['files'] if r['target'].endswith('Dust2Arena.java')];backup=Path(json.loads((d/'native-arrival/installation.json').read_text())['backup'])
for i,r in enumerate(rows):
 p=Path(r['target']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['after_sha256'];s=p.read_text();s=s.replace('if(!inside(p)){p.sendMessage("Estas fuera de Dust2. Usa .dust2 para entrar.");return true;}','if(!inside(p)&&!RETURNS.containsKey(p.getObjectId())){p.sendMessage("Estas fuera de Dust2. Usa .dust2 para entrar.");return true;}');assert '!RETURNS.containsKey' in s;shutil.copy2(p,backup/('Dust2Arena-before-'+str(i)+'.java'));p.write_text(s,encoding='utf-8');r['after_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(d/'installation.json').write_text(json.dumps(m,indent=2));(Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2));(d/'native-arrival/reload.mf').write_text('Manifest-Version: 1.0\nAgent-Class: ReloadDust2\nCan-Redefine-Classes: true\n\n')
