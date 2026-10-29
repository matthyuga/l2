from package_tools import *
import json,subprocess,hashlib
D=pathlib.Path(__file__).resolve().parent;installed='--installed' in sys.argv
stage=ROOT.parent/'l2' if installed else D/'stage';out=D/('asset-load-installed' if installed else 'asset-load');out.mkdir(exist_ok=True)
names=sorted({p['mesh'].split('.')[-1] for p in json.loads((D/'build-audit.json').read_text())['placed']})
reader=ROOT/'research/amber-l2/tools/umodel.exe';report=[]
for package,name in [('HGGludioSky_S.usx',n) for n in names]+[('HGGludioSky_T.utx','AcademyCloudSea')]:
    run=subprocess.run([str(reader),'-dump','-game=l2','-path='+str(stage),package,name],capture_output=True,text=True,errors='replace',timeout=60)
    text=run.stdout+run.stderr;(out/(name+'.log')).write_text(text,encoding='utf-8')
    assert run.returncode==0 and '*** ERROR' not in text and 'Unable to load' not in text and 'WARNING: missing' not in text,(name,text[-1500:])
    report.append(dict(package=package,object=name,loaded=True,warnings=[x for x in text.splitlines() if 'WARNING:' in x]))
(D/('installed-native-load-proof.json' if installed else 'native-load-proof.json')).write_text(json.dumps(report,indent=2));print('PASS:',len(names),'unique dock meshes and cloud shader load with converted textures. UModel FadeColor preview warnings retained in logs.')
