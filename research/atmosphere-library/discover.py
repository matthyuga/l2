import concurrent.futures, json, pathlib, urllib.request, urllib.parse
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES={
 'cloudy':'https://opengameart.org/content/cloudy-skyboxes-0',
 'kenney-sky':'https://kenney.nl/assets/skyboxes',
 'kenney-particles':'https://kenney.nl/assets/particle-pack',
 'kenney-smoke':'https://kenney.nl/assets/smoke-particles',
 'spritepilot':'https://spritepilot.com/free-game-assets/weather',
 'freesound':'https://freesound.org/people/IllusiaProductions/packs/15337/',
 'sonniss':'https://sonniss.com/gameaudiogdc/',
 'sonniss-2026':'https://gdc.sonniss.com/',
 'polyhaven-license':'https://polyhaven.com/license',
 'polyhaven-api-terms':'https://raw.githubusercontent.com/Poly-Haven/Public-API/master/terms.md',
}
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and a.get('href'):self.links.append(a['href'])
def read(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 L2LabAssetLibrary/1.0'}),timeout=45) as r:return r.read()
def run(item):
 name,url=item
 try:
  data=read(url);(ROOT/'sources').mkdir(exist_ok=True);(ROOT/'sources'/f'{name}.html').write_bytes(data)
  p=Links();p.feed(data.decode('utf8','replace'))
  links=list(dict.fromkeys(urllib.parse.urljoin(url,x) for x in p.links))
  (ROOT/'sources'/f'{name}-links.json').write_text(json.dumps(links,indent=2))
  selected=[x for x in links if any(s in x.lower() for s in ['.zip','.wav','.torrent','download','license','tracklist','.pdf'])]
  return {'source':name,'links':selected}
 except Exception as e:return {'source':name,'error':str(e)}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
  for result in ex.map(run,SOURCES.items()):print(json.dumps(result),flush=True)
