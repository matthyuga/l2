import json
import pathlib
import struct
import xml.etree.ElementTree as ET
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
schema = ET.parse(ROOT / 'tools/L2ClientDat/dist/data/structure/dats/npcgrp.xml').getroot()
entry = next(e for e in schema.findall('file') if e.get('pattern') == 'Interlude')
data = pathlib.Path(sys.argv[1]).read_bytes() if len(sys.argv)>1 else (ROOT / 'exports/npcgrp.raw').read_bytes()
offset = 0
def read(kind):
    global offset
    if kind in ('UINT','FLOAT'):
        value = struct.unpack_from('<I' if kind == 'UINT' else '<f',data,offset)[0]
        offset += 4
        return value
    if kind == 'UNICODE':
        size = read('UINT')
        if size > 1000000:
            raise ValueError(('bad string', offset, size))
        text = data[offset:offset+size].decode('utf-16-le')
        offset += size
        return text
    if kind == 'CNTR':
        b = data[offset]; offset += 1
        negative = b & 0x80
        value = b & 0x3f
        more = b & 0x40
        shift = 6
        while more:
            b=data[offset]; offset+=1
            value |= (b & 0x7f)<<shift
            more=b & 0x80
            shift+=7
        return -value if negative else value
    raise ValueError(kind)
def parse(nodes, variables):
    values = {}
    for node in nodes:
        name = node.get('name')
        if node.tag == 'node':
            values[name] = read(node.get('reader'))
            variables[name] = values[name]
        elif node.tag == 'for':
            count = variables[node.get('size').lstrip('#')]
            values[name+'_items'] = [parse(node,dict(variables)) for _ in range(count)]
    return values
count=read('UINT')
rows=[]
row_node=entry.find('for')
for _ in range(count):
    start=offset
    row=parse(row_node,{})
    row['_offset']=start
    row['_length']=offset-start
    rows.append(row)
report={'count':count,'parsed_bytes':offset,'total_bytes':len(data),'trailing_bytes':len(data)-offset,'rows':rows}
(ROOT / ('reports/npcgrp-amber-parsed.json' if len(sys.argv)>1 else 'reports/npcgrp-parsed.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print('NPCGRP',count,offset,len(data),'trailing',len(data)-offset)
for row in rows:
    if row['npc_id']==59001:
        print(json.dumps({k:row[k] for k in ('npc_id','class_name','mesh_name')},ensure_ascii=False))
