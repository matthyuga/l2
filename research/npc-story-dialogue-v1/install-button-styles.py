"""Guarded install/restore for the four selectable button styles layer. Never closes L2."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess

B=Path(__file__).resolve().parent
R=B.parents[1]
S=B/'client-demo-button-styles-v5'
C=R.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def closed():
    check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)
    assert check.returncode==0,'L2 is open. Installation prepared; close L2 before applying. No process was stopped.'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--restore',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    manifest_path=S/'installation.json'
    if args.restore:
        m=json.loads(manifest_path.read_text())
        assert m['installed'] and not m.get('restored'),'Not an installed active layer'
        closed()
        for row in m['files']:
            assert sha(Path(row['target']))==row['after_sha256'],'Concurrent client change: '+row['target']
            if row['backup']:assert sha(Path(row['backup']))==row['before_sha256'],'Backup integrity failure'
        if args.check:
            print('PASS: restore inputs verified; no writes');return
        for row in reversed(m['files']):
            closed();p=Path(row['target'])
            if row['backup']:shutil.copy2(row['backup'],p)
            else:p.unlink()
            assert (sha(p) if p.exists() else None)==row['before_sha256']
        m['restored']=True;m['installed']=False
        text=json.dumps(m,indent=2);manifest_path.write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
        print('RESTORED: exact previous client layer');return
    assert not manifest_path.exists(),'This layer has already been applied; inspect installation.json'
    closed()
    for name,h in json.loads((S/'input-hashes.json').read_text()).items():
        assert sha(Path(name))==h,'Concurrent change: '+name
    outputs=json.loads((S/'output-hashes.json').read_text())
    for name,h in outputs.items():assert sha(S/name)==h,'Staged output changed: '+name
    java=R/'tools/jdk-25.0.4.1+1/bin/java.exe'
    cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
    result=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(B/'verify-button-styles.groovy'),str(S)],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
    (S/'install-verification.log').write_text(result.stdout+result.stderr,encoding='utf8')
    assert result.returncode==0,result.stdout+result.stderr
    assert 'all other' in (S/'build-button-styles-xdat.log').read_text()
    names=['NexusAmberButtonsV5.u','Interface.u','Interface.xdat']
    assert not (C/names[0]).exists(),'Package name collision'
    if args.check:
        print('PASS: inputs, outputs, native bytecode checks and closed-client guard; no installation writes');return
    backup=R/'backups'/('npc-story-button-styles-v5-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir()
    records=[]
    for n in names:
        p=C/n;saved=backup/n if p.exists() else None
        if saved:shutil.copy2(p,saved)
        records.append(dict(target=str(p),backup=str(saved) if saved else None,before_sha256=sha(p) if p.exists() else None,after_sha256=sha(S/n),source=str(S/n)))
    m=dict(backup=str(backup),files=records,installed=False,server_changed=False,global_gamma_changed=False,in_game_validation='pending',scope='Four selectable button styles with three states; V4 background and portrait controls preserved')
    def save():
        text=json.dumps(m,indent=2);manifest_path.write_text(text);(backup/'manifest.json').write_text(text)
    save();written=[]
    try:
        for row in records:
            closed();p=Path(row['target'])
            assert (sha(p) if p.exists() else None)==row['before_sha256'],'Concurrent client change'
            written.append(row)
            shutil.copy2(row['source'],p)
            assert sha(p)==row['after_sha256']
        m['installed']=True;save()
    except BaseException:
        for row in reversed(written):
            p=Path(row['target'])
            if row['backup']:shutil.copy2(row['backup'],p)
            elif p.exists():p.unlink()
        m['restored_after_failure']=True;save();raise
    print('INSTALLED: four selectable button styles. Backup: '+str(backup))

if __name__=='__main__':main()
