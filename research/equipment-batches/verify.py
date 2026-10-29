from pathlib import Path
import json,hashlib,csv,collections,re,subprocess,struct,zlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];STAGE=ROOT/'stage';m=json.loads((ROOT/'installation.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
encrypted=0
for f in m['files']:
 assert sha(f['target'])==f['after'],f['target']
 p=Path(f['target'])
 if p.stem.startswith('EB') and p.suffix.lower() in ('.utx','.ukx','.usx'):
  b=p.read_bytes();protocol=121 if p.suffix.lower()=='.utx' else 111
  assert b[:28]==('Lineage2Ver'+str(protocol)).encode('utf-16le'),p
  assert zlib.crc32(b[:-20])==struct.unpack_from('<I',b,len(b)-8)[0],p
  encrypted+=1
assert 'SUCCESS' in (STAGE/'native-verification.txt').read_text(encoding='utf-8')
assert 'SUCCESS' in (STAGE/'shop-verification.txt').read_text(encoding='utf-8')
assert not re.search(r'cvc-|SEVERE|Exception', (STAGE/'shop-verification.log').read_text(errors='replace'))
allids=collections.defaultdict(list)
for f in (PROJECT/'server/game/data/stats/items').glob('*.xml'):
 for i in ET.parse(f).getroot().findall('item'):allids[int(i.get('id'))].append(str(f))
for i in m['items']:assert len(allids[i['id']])==1,(i['id'],allids[i['id']])
assert set(range(54130,54137))<=allids.keys()
for name,entry in m['catalogs'].items():
 p=STAGE/(name+'.installed.raw')
 subprocess.run([str(PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-o',str(p),str(PROJECT.parent/'l2/system-hud'/(name+'.dat'))],capture_output=True,check=True)
 assert p.read_bytes()==(STAGE/(name+'.raw')).read_bytes()
 before=(STAGE/(name+'.before.raw')).read_bytes();after=p.read_bytes();foot=b'\x0cSafePackage\0'
 assert after[4:len(before)-len(foot)]==before[4:-len(foot)]
result={'status':'PASS','installed_items':len(m['items']),'pending_entries':len(m['blocked']),'server_types':dict(collections.Counter(i['server_type'] for i in m['items'])),'all_installed_file_hashes':len(m['files']),'encrypted_texture_mesh_packages_checked':encrypted,'catalogs':m['catalogs'],'native_item_parser':'PASS','native_itemdata_and_multisell':'PASS','existing_catalog_record_bytes_preserved':True,'duplicate_server_item_ids':False,'in_game_visual_check':'pending'}
(ROOT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
with (ROOT/'CATALOGO.csv').open('w',encoding='utf-8-sig',newline='') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(m['items'][0]));writer.writeheader();writer.writerows(m['items'])
print(json.dumps(result,indent=2))
