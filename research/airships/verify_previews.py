from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]/'model-catalog'
chrome='C:/Program Files/Google/Chrome/Application/chrome.exe'
url='http://127.0.0.1:32280/?q=Gracia&model=airship_assembled_gracia&view=3d'
p=subprocess.run([chrome,'--headless=new','--no-first-run','--user-data-dir='+str(root.parent/'airships/qa-browser'),'--window-size=1440,1100','--screenshot='+str(root.parent/'airships/gallery-3d.png'),'--dump-dom','--virtual-time-budget=6000',url],capture_output=True,text=True,errors='replace',timeout=45)
(root.parent/'airships/browser-dom.html').write_text(p.stdout,encoding='utf-8')
assert p.returncode==0
report=json.loads((root/'gallery.json').read_text(encoding='utf-8'))
count=sum(m.get('external_source',False) and 'Gracia' in ' '.join(m.get('names',[])) for m in report['models'])
assert str(count)+' modelos' in p.stdout and '<canvas' in p.stdout
assert 'No se pudo abrir la vista 3D.' not in p.stdout
print('PASS:',count,'Gracia views visible and assembled WebGL canvas loaded')
