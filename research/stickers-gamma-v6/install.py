from pathlib import Path
import subprocess,json,hashlib,shutil,datetime
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Already installed'
v=json.loads((S/'verification.json').read_text());t=Path(v['target']);src=S/t.name
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'Close L2 before replacing textures'
assert sha(t)==v['before_sha256'] and sha(src)==v['after_sha256']
assert v['textures']==19 and v['all_other_raw_bytes_identical'] and v['alpha_preserved'] and v['wrapper_roundtrip'] and v['wrapper_crc']
assert (S/'verification.txt').read_text().startswith('PASS: exactly19 world sticker RGB mip arrays compensated')
preserve=[C/'Interface.u',C/'Interface.xdat',C/'Option.ini',C/'l2.ini',C/'NexusAmberGammaV2.u',R.parent/'l2/animations/NexusStickerEffectsV3.usk'];hashes={str(p):sha(p) for p in preserve}
B=R/'backups'/('stickers-gamma-v6-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir();saved=B/t.name;shutil.copy2(t,saved)
m={'target':str(t),'backup':str(saved),'before_sha256':sha(t),'after_sha256':sha(src),'textures':19,'scope':'RGB-only inverse gamma on world sticker textures; menu and emitters unchanged','installed':False,'visual_verification':'pending user test','preserved_files':hashes}
def save():
 data=json.dumps(m,indent=2);(S/'installation.json').write_text(data);(B/'manifest.json').write_text(data)
save()
try:
 t.write_bytes(src.read_bytes());assert sha(t)==m['after_sha256']
 for name,h in hashes.items():assert sha(Path(name))==h
 m['installed']=True;save()
except BaseException:
 shutil.copy2(saved,t);m['restored_after_failure']=True;save();raise
print('INSTALLED:19 compensated world stickers. Backup:',B)
