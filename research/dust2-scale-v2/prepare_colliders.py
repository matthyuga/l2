import pathlib,json,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=ROOT/'research/dust2-integration';g=json.loads((D/'geodata-audit.json').read_text());count=g['reachable_layers']
for sub,file in [('native-floor','build.py'),('native-floor','verify.py'),('native-walls','build.py'),('native-walls','verify.py')]:
 s=(OLD/sub/file).read_text(encoding='utf-8')
 s=s.replace("geo=ROOT/'server/game/data/geodata/24_19.l2j'","geo=BASE/'stage/Geodata/24_19.l2j'" if file=='build.py' else "geo=D.parent/'stage/Geodata/24_19.l2j'")
 s=s.replace("source=CLIENT/'Maps/24_19.unr'","source=BASE/'stage/Maps/24_19.unr'")
 s=s.replace('HGDust2Floor','HGDust2V2Floor').replace('HGDust2Wall','HGDust2V2Wall')
 s=s.replace('len(seen)>60000','len(seen)>4000').replace('len(seen)==61234',f'len(seen)=={count}').replace('len(covered)==61234',f'len(covered)=={count}')
 if sub=='native-walls':
  s=s.replace('h-z>=100','h-z>=64').replace('height>=92','height>=56').replace('abs(h-z)<=96','abs(h-z)<=24').replace('h>z+96','h>z+24')
  if file=='verify.py':
   s=s.replace("==1591","==json.loads((D.parent/'native-floor/audit.json').read_text())['floor_actors']")
 p=D/sub/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
print('Prepared isolated scaled native-collider builders; expected reachable',count)
