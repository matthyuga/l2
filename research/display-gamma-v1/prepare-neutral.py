from pathlib import Path
import subprocess,re,json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud';O=S/'neutral';O.mkdir(exist_ok=True)
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def crypt(*args):
 r=subprocess.run([str(codec),*map(str,args)],input=b'\n',capture_output=True,timeout=30);assert r.returncode==0,r.stdout+r.stderr
before=C/'l2.ini';raw=O/'l2.before.raw';crypt('-o',raw,before);b=raw.read_bytes();enc='utf-16' if b.startswith(b'\xff\xfe') else 'utf-8';text=b.decode(enc)
section=re.search(r'(?ms)^\[WinDrv.WindowsClient\]\r?\n.*?(?=^\[|\Z)',text);assert section
new=section[0]
for name,value in [('Brightness','0.500000'),('Contrast','0.500000'),('Gamma','1.000000')]:
 new,n=re.subn(r'(?m)^'+name+r'=[^\r\n]*',name+'='+value,new);assert n==1
out=text[:section.start()]+new+text[section.end():];(O/'l2.neutral.raw').write_bytes(out.encode(enc))
crypt('-c','encode','-p','413','-o',O/'l2.ini',O/'l2.neutral.raw');crypt('-o',O/'l2.roundtrip.raw',O/'l2.ini');assert (O/'l2.roundtrip.raw').read_bytes()==(O/'l2.neutral.raw').read_bytes()
old=(C/'Option.ini').read_bytes();opt=old.decode('utf-8-sig');opt,count=re.subn(r'(?m)^Gamma=[^\r\n]*','Gamma=1.000000',opt);assert count==1
(O/'Option.ini').write_bytes(opt.encode('utf-8-sig' if old.startswith(b'\xef\xbb\xbf') else 'utf-8'))
proof={'inputs':{str(C/n):sha(C/n) for n in ['l2.ini','Option.ini']},'outputs':{n:sha(O/n) for n in ['l2.ini','Option.ini']},'l2_roundtrip':True,'changes':['WinDrv.WindowsClient Brightness0.8 ->0.5','Contrast0.7 ->0.5','Gamma0.8 ->1.0','Option.ini Gamma0.8 ->1.0'],'status':'prepared, not installed'}
(O/'verification.json').write_text(json.dumps(proof,indent=2));print('PREPARED: neutral client settings, exact encryption roundtrip; no installed changes.')
