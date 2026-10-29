from pathlib import Path
import hashlib,json,struct,zlib,collections,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((ROOT/'installation.json').read_text(encoding='utf8'))
for c in m['files']:assert sha(c['target'])==c['after'],c['target']
profile_fix=ROOT/'camera-profile-fix/installation.json'
profile_files=0
if profile_fix.exists():
 fix=json.loads(profile_fix.read_text(encoding='utf8'))
 for c in fix['files']:assert sha(c['target'])==c['after'],c['target']
 profile_files=len(fix['files'])
counts=collections.Counter()
for p in (PROJECT/'server/game/data/stats/items').rglob('*.xml'):
 for t in ET.parse(p).getroot().findall('item'):counts[int(t.get('id'))]+=1
for t in m['items']:assert counts[t['id']]==1,t['id']
for name,c in m['catalogs'].items():
 before=(ROOT/(name+'.before.raw')).read_bytes();after=(ROOT/'stage'/(name+'.raw')).read_bytes();footer=b'\x0cSafePackage\0'
 assert after[4:len(before)-len(footer)]==before[4:-len(footer)]
 assert struct.unpack_from('<I',after)[0]==struct.unpack_from('<I',before)[0]+13
 assert sha(ROOT/'stage'/(name+'.raw'))==c['raw_sha256']
for a in m['assets']:
 p=ROOT/'stage/assets'/a['name'];b=p.read_bytes()
 assert b[:28]==('Lineage2Ver'+str(a['protocol'])).encode('utf-16le'),p
 assert zlib.crc32(b[:-20])==struct.unpack_from('<I',b,len(b)-8)[0],p
for name in ['native-verification.txt','runtime-verification.txt']:
 assert (ROOT/name).read_text().endswith('SUCCESS\n'),name
u=json.loads((ROOT/'umodel-verification.json').read_text());assert len(u)==20 and all(r['code']==0 and not r['error'] for r in u)
result=dict(status='PASS',installed_items=13,installed_files_checked=len(m['files'])+profile_files,camera_profile_files_checked=profile_files,unique_ids=[t['id'] for t in m['items']],packages_loaded_and_exported=20,checked_client_references=m['checked_references'],original_catalog_record_bytes_preserved=True,native_parser='PASS',live_templates_and_shops='PASS',in_game_visual_check='pending',real_character_or_inventory_modified=False)
(ROOT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
