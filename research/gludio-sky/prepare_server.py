"""Stage data/config changes against current files; installation has hash guards."""
from package_tools import *
import json,re,hashlib
D=pathlib.Path(__file__).resolve().parent;stage=D/'stage/server'
items=[]
def put(rel,text):
    p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def changed(rel,mutate):
    p=ROOT/'server/game'/rel;b=p.read_bytes();items.append(dict(relative=rel,sha256=hashlib.sha256(b).hexdigest()));put(rel,mutate(b.decode('utf-8-sig')))
def start(text):
    for key,value in [('CustomStartingLocation','True'),('CustomStartingLocX','149000'),('CustomStartingLocY','46700'),('CustomStartingLocZ','12040')]:
        text,n=re.subn(r'(?m)^'+key+r'\s*=.*$',key+' = '+value,text);assert n==1
    return text
changed('config/Custom/StartingLocation.ini',start)
def scripts(text):
    assert 'GludioSky' not in text,'Already installed; review existing manifest'
    text,n=re.subn(r'(?m)^(CustomScriptFolders\s*=\s*)([^\r\n]+)',lambda m:m[1]+m[2]+';GludioSky',text);assert n==1
    return text
changed('config/Custom/WorldContent.ini',scripts)
put('data/scripts/custom/GludioSky/GludioSky.java',(D/'GludioSky.java').read_text())
put('data/mapregion/gludio_sky.xml','''<?xml version="1.0" encoding="UTF-8"?>
<list enabled="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/MapRegion.xsd">
 <region name="gludio_sky" town="Gludio Sky Dock" castle="0" locId="925" bbs="13">
  <respawnPoint X="149000" Y="46700" Z="12040" />
  <respawnPoint X="149000" Y="46700" Z="12040" isChaotic="true" />
 </region>
</list>
''')
races='\n'.join('  <race name="'+r+'" point="gludio_sky" />' for r in ['HUMAN','ELF','DARK_ELF','ORC','DWARF'])
put('data/zones/gludio_sky.xml','''<?xml version="1.0" encoding="UTF-8"?>
<list enabled="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/zones.xsd">
 <zone name="Gludio Sky Arrival Peace" type="PeaceZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="145000" Y="44000" /><node X="151000" Y="50000" />
 </zone>
 <zone name="Gludio Sky Arrival Respawn" type="RespawnZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="145000" Y="44000" /><node X="151000" Y="50000" />
'''+races+'''
 </zone>
</list>
''')
# Service NPCs use existing shop/buffer definitions and are positioned by actual geo on startup.
# Spawn manually in script later only if needed; existing lower Coliseum services remain reachable.
(D/'server-source-hashes.json').write_text(json.dumps(items,indent=2))
print('Server configuration, respawn/peace zones and public .muelle command staged.')
