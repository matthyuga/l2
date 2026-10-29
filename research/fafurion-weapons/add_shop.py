"""Add Fafurion sections to NPC and administrative shops, preserving existing menus."""
from pathlib import Path
import datetime,hashlib,json,shutil,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
DATA=PROJECT/'server/game/data'
BUY=54130
MULTI=50035413
for folder,iid in [('buylists',BUY),('multisell',MULTI)]:
    assert not any(int(f.stem)==iid for f in (DATA/folder).rglob('*.xml') if f.stem.isdigit()),f'List ID already exists: {iid}'
names=[i.get('name') for i in ET.parse(DATA/'stats/items/54100-54199.xml').getroot().findall('item')]
changes={}
for rel,action in [('html/merchant/50010.htm',f'bypass -h npc_%objectId%_multisell {MULTI}'),
                   ('html/merchant/50010-1.htm',f'bypass -h npc_%objectId%_multisell {MULTI}'),
                   ('html/admin/gmshops.htm',f'bypass -h admin_buy {BUY}'),
                   ('html/admin/gmstore/gear/weapons.htm',f'bypass -h admin_buy {BUY}')]:
    raw=(DATA/rel).read_bytes();text=raw.decode('utf-8');assert 'value="Fafurion"' not in text
    button=f'<br><center><button action="{action}" value="Fafurion" width="120" height="21" back="bigbutton_over" fore="bigbutton"></center><br>\r\n'
    # Keep the new shortcut near the top of long menus.
    marker='</center>';at=text.index(marker)+len(marker)
    text=text[:at]+'\r\n'+button+text[at:]
    assert text.replace('\r\n'+button,'',1).encode('utf-8')==raw
    changes[rel]=text.encode('utf-8')
buy=['<?xml version="1.0" encoding="UTF-8"?>','<list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/buylist.xsd">']
multi=['<?xml version="1.0" encoding="UTF-8"?>','<list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../xsd/multisell.xsd">','\t<npcs><npc>50010</npc></npcs>']
for iid,name in zip(range(54130,54137),names):
    buy.append(f'\t<item id="{iid}" price="0" /> <!-- {name} -->')
    multi.extend(['\t<item>', '\t\t<ingredient id="57" count="48800000" />',f'\t\t<production id="{iid}" count="1" />','\t</item>'])
buy.append('</list>');multi.append('</list>')
changes[f'buylists/{BUY}.xml']=('\n'.join(buy)+'\n').encode()
changes[f'multisell/custom/{MULTI}.xml']=('\n'.join(multi)+'\n').encode()
backup=PROJECT/'backups'/('fafurion-shop-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
records=[]
for root in [DATA,PROJECT/'source/L2J_Mobius_CT_0_Interlude/dist/game/data',PROJECT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data']:
    for rel,raw in changes.items():
        target=root/rel;old=target.read_bytes() if target.exists() else None
        saved=backup/(str(len(records))+'-'+target.name)
        if old is not None:saved.write_bytes(old)
        records.append({'target':str(target),'backup':str(saved) if old is not None else None,
                        'before':hashlib.sha256(old).hexdigest() if old is not None else None,'after':hashlib.sha256(raw).hexdigest()})
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        assert target.read_bytes()==raw
        if target.suffix=='.xml':ET.parse(target)
(ROOT/'shop-installation.json').write_text(json.dumps({'backup':str(backup),'buylist':BUY,'multisell':MULTI,'files':records},indent=2),encoding='utf-8')
print('Installed both shop sections; backup '+str(backup))
