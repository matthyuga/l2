from pathlib import Path
import xml.etree.ElementTree as E
s=Path(__file__).resolve().parent
p=s/'GiranSiegeLab/GiranSiegeLab.java';t=p.read_text()
t=t.replace('Boss special AI pending; native base combat only.','Ares/Nyx V7 patrol sectors, detect attackers and protect the artifact; native combat.')
t=t.replace('Guardianes Ares/Nyx protegen al propietario actual<br>','Ares: patrulla patio y acceso interior<br>Nyx: patrulla sala, pasillo y artefacto<br>Defienden al propietario actual<br>')
p.write_text(t,encoding='utf-8')
ids={1,6,9,78,261,337,1064,1074,1239,1291,1341}
for p in (s.parents[1]/'server/game/data/stats/skills').glob('*.xml'):
    for skill in E.parse(p).getroot():
        if int(skill.get('id',0)) in ids:print(skill.attrib,{e.tag:e.text for e in skill if e.tag in {'operateType','targetType','affectScope','castRange','reuseDelay','chargeConsume'}})
