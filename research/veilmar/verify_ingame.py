"""Verify the installed package hashes and the latest actual GameServer smoke run."""
import pathlib,json,hashlib,xml.etree.ElementTree as ET,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar'
m=json.loads((D/'installation.json').read_text())
for entry in m['files']:
 p=pathlib.Path(entry['path'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['after_sha256'],p
 if entry['existed']:
  assert hashlib.sha256(pathlib.Path(entry['backup']).read_bytes()).hexdigest()==entry['before_sha256'],entry['backup']
instance=ET.parse(ROOT/'server/game/data/instances/custom/veilmar_pvp.xml').getroot()
ids={int(e.attrib['id']) for e in instance.find('doorlist')}
doors={int(e.attrib['id']):e.attrib for e in ET.parse(ROOT/'server/game/data/Doors.xml').getroot()}
assert len(ids)==26 and ids.issubset(doors) and all(doors[i]['default_status']=='open' for i in ids)
assert instance.find('PvPInstance').attrib['val']=='true'
assert instance.find('allowSummon').attrib['val']=='true'
log=(ROOT/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
assert 'VEILMAR_SMOKE FAIL' not in log
success=next(line for line in log.splitlines() if 'VEILMAR_SMOKE PASS' in line and '9 agite spawns/cleanup' in line)
assert 'veilmar_pvp.xml Line=' not in log
report=dict(date=datetime.datetime.now().isoformat(),installed_files=len(m['files']),hashes='pass',backup_hashes='pass',doors=26,server_smoke=success,
            client_visual_test='pending first interactive entry',full_map_navigation='not exhaustively audited',backup=m['backup'],geodata_toolkit_revision=m['geodata_toolkit_revision'])
(D/'ingame-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'ingame-success.log').write_text(success+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
