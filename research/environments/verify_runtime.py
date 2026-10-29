"""Read-only final checks. Run while both new profiles are started, no clients."""
from pathlib import Path
import json
import re
import subprocess

here = Path(__file__).resolve().parent
results = []
for profile in ('hellgames', 'academy'):
    root = Path('E:/l2-' + profile)
    log = (root/'logs/game-stderr.log').read_text(encoding='utf8', errors='replace')
    assert 'Server loaded in ' in log and 'Registered on login as Server' in log
    assert not re.search(r'SEVERE|Exception|\bERROR\b', log), profile + ' runtime errors'
    expected = ['HELLGAMES_ARRIVAL_READY'] if profile == 'hellgames' else [
        'ACADEMY_WORLD_READY', 'ACADEMY_TELEMETRY_PASSIVE',
        'ACADEMY_RETURN_TEST PASS', 'ACADEMY_ROSTER_TEST PASS']
    assert all(marker in log for marker in expected), profile + ' verification not complete'
    command = [str(root/'tools/mariadb/bin/mariadb.exe'),
               '--defaults-extra-file='+str(root/'database/client.ini'),
               '--batch', '--skip-column-names', 'l2_'+profile, '-e']
    def query(sql):
        return subprocess.check_output(command+[sql], text=True).strip()
    accounts, characters, online = map(int, query('SELECT (SELECT COUNT(*) FROM accounts),(SELECT COUNT(*) FROM characters),(SELECT COUNT(*) FROM characters WHERE online<>0);').split('\t'))
    assert accounts == 0 and online == 0
    record = dict(profile=profile, markers=expected, accounts=accounts,
                  characters=characters, onlineCharacters=online, runtime='PASS')
    if profile == 'hellgames':
        assert characters == 0
    else:
        folder = root/'server/game/data/scripts/custom'
        roster = (folder/'NormalNpcRoster/NormalNpcRoster.java').read_text(encoding='utf8')
        pilots = (folder/'RealHumanPilots/RealHumanPilots.java').read_text(encoding='utf8')
        names = set(re.findall(r'new Profile\(\d+,"([^"]+)"', roster))
        names.update(re.findall(r'prepareOne\("([^"]+)"', pilots))
        actual = set(query('SELECT char_name FROM characters;').splitlines())
        assert names == actual, 'Unexpected or missing technical characters'
        count = int(query('SELECT COUNT(*) FROM lab_normal_npc_profiles;'))
        assert count == 39
        assert query('SELECT @@innodb_flush_log_at_trx_commit;') == '1'
        record.update(technicalCharactersOnly=True, preparedNpcProfiles=count,
                      durabilitySettingRestored=True)
    results.append(record)
    (here/(profile+'-verified-game.log')).write_text(log, encoding='utf8')
(here/'runtime-verification.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print(json.dumps(results,indent=2))
