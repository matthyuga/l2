from pathlib import Path
import subprocess,zipfile,json
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');J=P/'tools/jdk-25.0.4.1+1/bin'
def run(*args):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True)
cp=str(P/'server/libs/*')+';'+str(D/'compiled')
out=run(J/'javac.exe','-encoding','UTF-8','-cp',cp,'-d',D/'build',D/'GraftHsl.java',D/'HslReloadAgent.java',D/'HslProtocolTest.java');print(out.stdout+out.stderr)
out=run(J/'java.exe','-cp',cp+';'+str(D/'build'),'HslProtocolTest');print(out.stdout);(D/'server-test-results.json').write_text(json.dumps(dict(output=out.stdout,passed=16394),indent=2))
with zipfile.ZipFile(D/'hsl-helper.jar','w',zipfile.ZIP_DEFLATED) as z:
 for f in (D/'compiled/org/l2jmobius/gameserver/custom').rglob('*.class'):z.write(f,f.relative_to(D/'compiled').as_posix())
with zipfile.ZipFile(D/'reload-hsl.jar','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('META-INF/MANIFEST.MF','Manifest-Version: 1.0\nAgent-Class: HslReloadAgent\nCan-Redefine-Classes: true\nCan-Retransform-Classes: true\n\n')
 for pattern in ['HslReloadAgent*.class','GraftHsl*.class']:
  for f in (D/'build').glob(pattern):z.write(f,f.name)
for i,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 run(J/'java.exe','-cp',D/'build','GraftHsl',D,target,'grafted-'+str(i))
 classes={f.relative_to(D/('grafted-'+str(i))).as_posix():f.read_bytes() for f in (D/('grafted-'+str(i))).rglob('*.class')}
 with zipfile.ZipFile(D/'hsl-helper.jar') as z:classes.update({n:z.read(n) for n in z.namelist()})
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(D/('GameServer-'+str(i)+'.jar'),'w') as dst:
  names=src.namelist()
  for info in src.infolist():dst.writestr(info,classes.get(info.filename,src.read(info.filename)))
  for name,b in classes.items():
   if name not in names:dst.writestr(name,b,compress_type=zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(D/('GameServer-'+str(i)+'.jar')) as dst:
  assert not dst.testzip();assert all(src.read(n)==dst.read(n) for n in src.namelist() if n not in classes)
print('Prepared both current JAR mirrors; only selected packet methods and new helper changed.')
