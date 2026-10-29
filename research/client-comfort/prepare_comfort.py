from pathlib import Path
import hashlib, json, re, subprocess, zipfile, shutil

root = Path(__file__).resolve().parents[2]
stage = root / 'research/client-comfort'
client = root.parent / 'l2/system-hud'
backup = root / 'backups/client-comfort-2026-10-10'
codec = root / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
proof = {}
for name, old, new in (
    ('user.ini', b'MaxZoomingDist=250', b'MaxZoomingDist=1800'),
    ('l2.ini', b'Paths=../System/*.u', b'Paths=../system-hud/*.u\r\nPaths=../System/*.u'),
):
    saved = backup / 'client' / name
    if not saved.exists(): shutil.copy2(client / name, saved)
    rawfile = stage / (name + '.original.raw')
    subprocess.run([str(codec), '-o', str(rawfile), str(client / name)], check=True, capture_output=True)
    raw = rawfile.read_bytes()
    assert raw.count(old) == 1, (name, raw.count(old))
    changed = raw.replace(old, new, 1)
    modified = stage / (name + '.modified.raw')
    modified.write_bytes(changed)
    output = stage / name
    subprocess.run([str(codec), '-c', 'encode', '-p', '413', '-o', str(output), str(modified)], check=True, capture_output=True)
    roundtrip = stage / (name + '.roundtrip.raw')
    subprocess.run([str(codec), '-o', str(roundtrip), str(output)], check=True, capture_output=True)
    assert roundtrip.read_bytes() == changed
    proof[name] = {'change': [old.decode(), new.decode()], 'roundtrip': True}

start = root / 'Start-L2Local.ps1'
text = start.read_text(encoding='utf-8-sig')
assert 'VerifySkillCatalog' not in text
text = text.replace('[switch]$VerifyArenaSpawns)', '[switch]$VerifyArenaSpawns, [switch]$VerifySkillCatalog)', 1)
text = text.replace("$ArenaVerificationOption = '-Dlab.arena.spawn.verify=' + $VerifyArenaSpawns.IsPresent.ToString().ToLowerInvariant()",
                    "$ArenaVerificationOption = '-Dlab.arena.spawn.verify=' + $VerifyArenaSpawns.IsPresent.ToString().ToLowerInvariant()\n$CatalogVerificationOption = '-Dlab.catalog.verify=' + $VerifySkillCatalog.IsPresent.ToString().ToLowerInvariant()", 1)
text = text.replace("$ArenaVerificationOption,'-XX:+UseZGC'", "$ArenaVerificationOption,$CatalogVerificationOption,'-XX:+UseZGC'", 1)
assert text.count('$CatalogVerificationOption') == 2
with start.open('w', encoding='utf-8-sig', newline='') as f: f.write(text.replace('\n', '\r\n'))

jar = root / 'server/libs/GameServer.jar'
assert hashlib.sha256(jar.read_bytes()).hexdigest().upper() == '2E35D88F6050EB22619ADF00EE0070494126AE0ED535DC33B0E4C1E18BC99349'
classes = root / 'build/client-comfort'
prefix = 'org/l2jmobius/gameserver/network/serverpackets/'
replacements = {prefix + name: (classes / prefix / name).read_bytes() for name in
                ('SkillList.class', 'SkillCatalogView.class', 'SkillCatalogView$Model.class')}
target = classes / 'GameServer.jar'
with zipfile.ZipFile(jar) as src, zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():
        dst.writestr(info, replacements.pop(info.filename, src.read(info.filename)))
    for name, data in replacements.items(): dst.writestr(name, data)
with zipfile.ZipFile(jar) as src, zipfile.ZipFile(target) as dst:
    changed_entries = [name for name in src.namelist() if src.read(name) != dst.read(name)]
    new_entries = sorted(set(dst.namelist()) - set(src.namelist()))
    assert changed_entries == [prefix + 'SkillList.class'], changed_entries
    assert new_entries == sorted([prefix + 'SkillCatalogView.class', prefix + 'SkillCatalogView$Model.class'])
proof['jar'] = {'changed_entries': changed_entries, 'new_entries': new_entries, 'all_other_entries_identical': True}
proof['original_hashes'] = {name: hashlib.sha256((backup / 'client' / name).read_bytes()).hexdigest()
                            for name in ('user.ini', 'l2.ini', 'Interface.u', 'Interface.xdat')}
proof['original_jar_sha256'] = hashlib.sha256(jar.read_bytes()).hexdigest()
(stage / 'verification.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
print(json.dumps(proof, indent=2))
