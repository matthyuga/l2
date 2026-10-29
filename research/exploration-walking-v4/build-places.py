from pathlib import Path
import xml.etree.ElementTree as E
import re,hashlib,json
root=Path(__file__).resolve().parents[2]; data=root/'server/game/data'
out=Path(__file__).resolve().parent/'server/custom/ExplorationWalking/places.xml'
norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
entries={}
for f in sorted((data/'teleporters/town').glob('*.xml')):
    for n in E.parse(f).iter('location'):
        a=n.attrib;name=a['name'];point=tuple(int(a[k]) for k in ('x','y','z'))
        entries.setdefault(name,set()).add(point)
spawnfiles={norm(f.stem):f for f in sorted((data/'spawns').rglob('*.xml'))}
aliases={'varkasilenosoutpost':'varkaslenosoutpost','forgeofthegods':'forgeofgods'}
catalog=E.Element('places',{'version':'1','description':'Named teleport destinations; entry circles and matching spawn territories. Editable exploration geometry, not native client ZoneName boundaries.'})
summary=[]
for name,points in sorted(entries.items()):
    place=E.SubElement(catalog,'place',{'id':hashlib.sha256(name.encode()).hexdigest()[:16],'name':name})
    for x,y,z in sorted(points):
        E.SubElement(place,'circle',dict(x=str(x),y=str(y),z=str(z),radius='3000',height='1200'))
    source=spawnfiles.get(aliases.get(norm(name),norm(name)))
    count=0
    if source:
        place.set('source',str(source.relative_to(data)).replace('\\','/'))
        for t in E.parse(source).iter('territory'):
            nodes=t.findall('node')
            if len(nodes)<3:continue
            poly=E.SubElement(place,'polygon',dict(minZ=t.attrib['minZ'],maxZ=t.attrib['maxZ']))
            for node in nodes:E.SubElement(poly,'node',dict(x=node.attrib['x'],y=node.attrib['y']))
            count+=1
    summary.append(dict(name=name,circles=len(points),polygons=count,source=str(source) if source else None))
E.indent(catalog);out.write_bytes(E.tostring(catalog,encoding='utf-8',xml_declaration=True))
(out.parent.parent.parent.parent/'places-catalog.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print('Places:',len(summary),'spawn polygons:',sum(s['polygons'] for s in summary))
print('Ketra:',next(s for s in summary if s['name']=='Ketra Orc Outpost'))
