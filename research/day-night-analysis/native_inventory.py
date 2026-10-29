"""Read-only PE symbol/string inventory and focused x86 instruction views."""
from pathlib import Path
import pefile,re,json,hashlib,capstone
ROOT=Path(__file__).resolve().parent
TARGET=Path('E:/l2/system-hud/engine.dll')
PATTERN=re.compile(r'L2Time|TimeEnv|Sun|Moon|Sky|Weather|Rain|Fog|DayNight|Directional|LightMap|WorldMax|OutsideWorld',re.I)
def main():
 b=TARGET.read_bytes();pe=pefile.PE(data=b);exports=[]
 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
  name=e.name.decode('ascii','replace') if e.name else ''
  if PATTERN.search(name):exports.append({'name':name,'ordinal':e.ordinal,'rva':hex(e.address),'va':hex(pe.OPTIONAL_HEADER.ImageBase+e.address),'offset':hex(pe.get_offset_from_rva(e.address)) if not e.forwarder else None,'forwarder':e.forwarder.decode() if e.forwarder else None})
 strings=[]
 for m in re.finditer(rb'[\x20-\x7e]{5,}',b):
  s=m.group().decode('ascii')
  if len(s)<400 and PATTERN.search(s):strings.append({'encoding':'ascii','offset':hex(m.start()),'value':s})
 for m in re.finditer(rb'(?:[\x20-\x7e]\x00){5,}',b):
  s=m.group().decode('utf-16le')
  if len(s)<400 and PATTERN.search(s):strings.append({'encoding':'utf16le','offset':hex(m.start()),'value':s})
 result={'tool':'ordinary Python pefile/capstone static inspection (not REA Evidence)','target':str(TARGET),'sha256':hashlib.sha256(b).hexdigest(),'imagebase':hex(pe.OPTIONAL_HEADER.ImageBase),'exports':exports,'strings':strings}
 (ROOT/'engine-inventory.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print('Matched exports',len(exports),'strings',len(strings))
 print('\n'.join(x['va']+' '+x['name'] for x in exports if re.search('L2Time|TimeEnv|Sky|Sun|Moon|Weather',x['name'],re.I)))
if __name__=='__main__':main()
