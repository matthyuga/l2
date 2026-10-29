"""Guarded one-package install/restore. Leaves the live game process alone."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1];S=B/'client-demo-ornamental-v4'
C=R.parent/'l2/system-hud';P='NexusAmberAngularV3.u'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def closed():
    p=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)
    assert p.returncode==0,'L2 is open; close it before applying this prepared update. No process was stopped.'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--restore',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    manifest=S/'installation.json';closed()
    if args.restore:
        m=json.loads(manifest.read_text());assert m['installed'] and not m.get('restored')
        assert sha(C/P)==m['after_sha256'],'Concurrent package change'
        assert sha(Path(m['backup'])/P)==m['before_sha256'],'Backup integrity failure'
        if args.check:print('PASS: exact backup and active package verified; no writes');return
        shutil.copy2(Path(m['backup'])/P,C/P);assert sha(C/P)==m['before_sha256']
        m['installed']=False;m['restored']=True
        text=json.dumps(m,indent=2);manifest.write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
        print('RESTORED: exact prior angular texture package');return
    assert not manifest.exists(),'Already applied; inspect installation.json'
    inputs=json.loads((S/'input-hashes.json').read_text())
    for n,h in inputs.items():assert sha(Path(n))==h,'Concurrent change: '+n
    outputs=json.loads((S/'output-hashes.json').read_text());assert sha(S/P)==outputs[P]
    v=json.loads((S/'verification.json').read_text());assert v['native_verification'] and v['texture_crc'] and v['texture_roundtrip']
    if args.check:print('PASS: verified texture patch and current client inputs; no writes');return
    backup=R/'backups'/('npc-story-ornamental-v4-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
    shutil.copy2(C/P,backup/P)
    m=dict(backup=str(backup),target=str(C/P),before_sha256=sha(C/P),after_sha256=sha(S/P),installed=False,changed_exports=['BackgroundOpaque','BackgroundSemi'],interface_and_xdat_unchanged=True,server_changed=False,in_game_validation='pending')
    def save():
        text=json.dumps(m,indent=2);manifest.write_text(text);(backup/'manifest.json').write_text(text)
    save();closed()
    try:
        assert sha(C/P)==m['before_sha256'];shutil.copy2(S/P,C/P);assert sha(C/P)==m['after_sha256']
        for n,h in inputs.items():
            if Path(n).name!=P:assert sha(Path(n))==h,'Unrelated file changed'
        m['installed']=True;save()
    except BaseException:
        shutil.copy2(backup/P,C/P);m['restored_after_failure']=True;save();raise
    print('INSTALLED: ornamental fill only. Backup: '+str(backup))
if __name__=='__main__':main()
