from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def closed():
    p=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)
    assert p.returncode==0,'L2 is open. Close it before applying the prepared skin. No process was stopped.'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--restore',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    closed();manifest=S/'installation.json'
    if args.restore:
        m=json.loads(manifest.read_text());assert m['installed'] and not m.get('restored')
        for row in m['files']:
            assert sha(Path(row['target']))==row['after_sha256'],'Concurrent change: '+row['target']
            if row['backup']:assert sha(Path(row['backup']))==row['before_sha256']
        if args.check:print('PASS: restoration hashes and backups verified; no writes');return
        for row in reversed(m['files']):
            closed();p=Path(row['target'])
            if row['backup']:shutil.copy2(row['backup'],p)
            else:p.unlink()
            assert (sha(p) if p.exists() else None)==row['before_sha256']
        m['installed']=False;m['restored']=True
        text=json.dumps(m,indent=2);manifest.write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
        print('RESTORED: exact previous sticker wheel');return
    assert not manifest.exists(),'Already applied; inspect installation.json'
    inputs=json.loads((S/'input-hashes.json').read_text());outputs=json.loads((S/'output-hashes.json').read_text())
    for n,h in inputs.items():assert sha(Path(n))==h,'Concurrent client change: '+n
    for n,h in outputs.items():assert sha(S/n)==h,'Staged output changed: '+n
    v=json.loads((S/'verification.json').read_text());assert v['texture_crc'] and v['texture_roundtrip'] and v['textures']==33
    assert '145 other windows byte identical' in (S/'build-xdat.log').read_text()
    java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
    p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(S/'verify.groovy'),str(S)],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
    (S/'install-verification.log').write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
    assert not (C/'NexusStickerGoldV7.u').exists(),'Package name collision'
    if args.check:print('PASS: prepared skin, native texture inventory, current inputs and closed-client guard');return
    backup=R/'backups'/('stickers-gold-v7-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
    records=[]
    for n in ['NexusStickerGoldV7.u','Interface.xdat']:
        p=C/n;saved=backup/n if p.exists() else None
        if saved:shutil.copy2(p,saved)
        records.append(dict(target=str(p),backup=str(saved) if saved else None,before_sha256=sha(p) if p.exists() else None,after_sha256=sha(S/n),source=str(S/n)))
    m=dict(backup=str(backup),files=records,installed=False,scope='Gold UI skin for two sticker windows only',interface_script_unchanged=True,sticker_effects_unchanged=True,server_changed=False,in_game_validation='pending')
    def save():
        text=json.dumps(m,indent=2);manifest.write_text(text);(backup/'manifest.json').write_text(text)
    save();written=[]
    try:
        for row in records:
            closed();p=Path(row['target']);assert (sha(p) if p.exists() else None)==row['before_sha256'];written.append(row);shutil.copy2(row['source'],p);assert sha(p)==row['after_sha256']
        for n,h in inputs.items():
            if Path(n).name!='Interface.xdat':assert sha(Path(n))==h,'Unrelated file changed: '+n
        m['installed']=True;save()
    except BaseException:
        for row in reversed(written):
            p=Path(row['target'])
            if row['backup']:shutil.copy2(row['backup'],p)
            elif p.exists():p.unlink()
        m['restored_after_failure']=True;save();raise
    print('INSTALLED: gold sticker wheel. Backup: '+str(backup))
if __name__=='__main__':main()
