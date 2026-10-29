import copy
import json
import pathlib
import struct
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'reports/npcgrp-parsed.json').read_text(encoding='utf8'))
rows=report['rows']
assert not any(row['npc_id']==59001 for row in rows)
row=copy.deepcopy(next(row for row in rows if row['npc_id']==30004))
row.update({'npc_id':59001,'class_name':'LineageNPC.a_traderB_FHuman','mesh_name':'L2AmberNPCv4.AmberNPC',
            'texture_name':2,'texture_name_items':[{'param_texture_name':'L2AmberNPCv4.AmberBodyShader'},
                                                 {'param_texture_name':'L2AmberNPCv4.AmberOutfitShader'}],
            'texture_name_second':0,'texture_name_second_items':[]})
schema=ET.parse(ROOT/'tools/L2ClientDat/dist/data/structure/dats/npcgrp.xml').getroot()
nodes=next(e for e in schema.findall('file') if e.get('pattern')=='Interlude').find('for')
def compact(value):
    negative=value<0
    value=abs(value)
    output=bytearray([(value&0x3f)|(0x80 if negative else 0)|(0x40 if value>>6 else 0)])
    value>>=6
    while value:
        output.append((value&0x7f)|(0x80 if value>>7 else 0))
        value>>=7
    return output
def encode(nodes,record):
    output=bytearray()
    for node in nodes:
        name=node.get('name')
        if node.tag=='node':
            kind=node.get('reader')
            value=record[name]
            if kind=='UNICODE':
                text=value.encode('utf-16-le')
                output+=struct.pack('<I',len(text))+text
            elif kind=='CNTR': output+=compact(value)
            else: output+=struct.pack('<I' if kind=='UINT' else '<f',value)
        else:
            for item in record[name+'_items']: output+=encode(node,item)
    return output
original=(ROOT/'exports/npcgrp.raw').read_bytes()
end=report['parsed_bytes']
patched=struct.pack('<I',report['count']+1)+original[4:end]+encode(nodes,row)+original[end:]
(ROOT/'exports/npcgrp-amber.raw').write_bytes(patched)
(ROOT/'reports/amber-npcgrp-row.json').write_text(json.dumps(row,indent=2),encoding='utf8')
xml='''<?xml version="1.0" encoding="UTF-8"?>
<list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../../xsd/npcs.xsd">
    <!-- Amber prototype: fixed outfit; isolated client profile system-amber. -->
    <npc id="902500" displayId="59001" level="80" type="Folk" name="Amber" title="Prueba Koikatsu" usingServerSideName="true" usingServerSideTitle="true">
        <race>HUMAN</race>
        <sex>FEMALE</sex>
        <stats str="40" int="21" dex="30" wit="20" con="43" men="20">
            <vitals hp="10000" hpRegen="10" mp="1000" mpRegen="5" />
            <attack physical="100" magical="100" attackSpeed="300" />
            <defence physical="1000" magical="1000" />
            <speed><walk ground="80" /><run ground="150" /></speed>
        </stats>
        <status talkable="true" attackable="false" undying="true" randomWalk="false" />
        <collision><radius normal="9" /><height normal="23" /></collision>
    </npc>
</list>
'''
(ROOT/'exports/amber_lab.xml').write_text(xml,encoding='utf8')
print('Prepared NPC 902500 / client display 59001; existing',report['count'],'rows preserved byte-for-byte.')
