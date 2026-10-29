"""Create two isolated, local-only L2 runtimes from Lab, without its database."""
from pathlib import Path
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import time
import sys

LAB = Path('E:/l2-local')
HERE = Path(__file__).resolve().parent
JAVA = LAB / 'tools/jdk-25.0.4.1+1'
MARIA = LAB / 'tools/mariadb-11.8.9-winx64'
CLIENT = Path('E:/l2')
PROFILES = [
    dict(id='hellgames', name='L2 Hellgames', root='E:/l2-hellgames', address='127.0.0.2', heapMb=2048,
         scripts='HellgamesArrival', spawn=(149000,46700,12040)),
    dict(id='academy', name='L2 Academy', root='E:/l2-academy', address='127.0.0.3', heapMb=2048,
         scripts='LabTelemetry;RealHumanPilots;NormalNpcRoster;SoloArenaGauntlet;AcademyWorld', spawn=(148900,46100,-3400)),
]

def copy_tree(source, dest, excludes=()):
    dest.mkdir(parents=True, exist_ok=True)
    args = ['robocopy', str(source), str(dest), '/E', '/MT:16', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS', '/NP']
    if excludes: args += ['/XF', *excludes]
    if Path(source) == LAB / 'server/game/data':
        # CustomWorldOnly never loads the native quest tree. Keep it in Lab;
        # there is no reason to duplicate its thousands of unused HTML files.
        args += ['/XD', str(Path(source)/'scripts/quests')]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode >= 8:
        raise RuntimeError('Copy failed: ' + str(source) + ' -> ' + str(dest) + ': ' + r.stdout[-1500:])

def set_ini(path, values):
    text = path.read_text(encoding='utf-8-sig')
    for key, value in values.items():
        text, n = re.subn(r'(?m)^' + re.escape(key) + r'\s*=.*$', lambda _: key + ' = ' + str(value), text)
        if not n:
            text += '\n' + key + ' = ' + str(value) + '\n'
        assert n <= 1, (path, key, n)
    path.write_text(text, encoding='utf8')

def copy_client(root):
    dest = root / 'client/Lineage II'
    dest.mkdir(parents=True, exist_ok=True)
    for folder in ['animations','camtextures','forcefeedback','l2text','maps','music','sounds','staticmeshes','systextures','textures','voice']:
        source = CLIENT / folder
        if source.exists():
            print(root.name, 'client', folder, flush=True)
            copy_tree(source, dest / folder)
    copy_tree(CLIENT / 'system-hud', dest / 'system', ('Shot*','*.log','*.bak','*.dmp'))
    return dest / 'system'

def prepare(profile):
    root = Path(profile['root'])
    assert root.resolve().parent == Path('E:/').resolve() and root.name in ['l2-hellgames','l2-academy']
    if root.exists():
        manifest = root / 'environment.json'
        assert manifest.exists(), 'Existing root without preparation manifest'
        previous = json.loads(manifest.read_text(encoding='utf8'))
        assert previous.get('state') == 'preparing' and previous.get('id') == profile['id'], 'Refusing to overwrite a prepared or unrelated environment'
        print(profile['name'], 'resuming incomplete preparation', flush=True)
    root.mkdir(exist_ok=True)
    (root / 'environment.json').write_text(json.dumps({**profile, 'state':'preparing','public':False}, indent=2), encoding='utf8')
    for folder in ['run','logs','database','server/libs']:
        (root / folder).mkdir(parents=True, exist_ok=True)
    print(profile['name'], 'copying independent runtime', flush=True)
    copy_tree(JAVA, root / 'tools/jdk')
    copy_tree(MARIA, root / 'tools/mariadb')
    for path in (LAB / 'server/libs').iterdir():
        if path.is_file(): shutil.copy2(path, root / 'server/libs' / path.name)
    for kind in ['login','game']:
        for folder in ['config','data']:
            copy_tree(LAB / 'server' / kind / folder, root / 'server' / kind / folder, ('hexid.txt','*.log','*.bak'))
        for filename in ['console.cfg','log.cfg','java.cfg']:
            source = LAB / 'server' / kind / filename
            if source.exists(): shutil.copy2(source, root / 'server' / kind / filename)
        (root / 'server' / kind / 'log').mkdir(exist_ok=True)
    ip = profile['address']
    set_ini(root/'server/login/config/Server.ini', {'LoginserverHostname':ip,'LoginHostname':ip,'LoginserverPort':2106,'LoginPort':19014})
    set_ini(root/'server/game/config/Server.ini', {'LoginHost':ip,'LoginPort':19014,'GameserverHostname':ip,'GameserverPort':7777,'MaximumOnlineUsers':1 if profile['id']=='academy' else 2000})
    private = root / 'database/credentials-private.json'
    if not private.exists(): private.write_text(json.dumps({'root':secrets.token_hex(24),'app':secrets.token_hex(24)}), encoding='utf8')
    passwords = json.loads(private.read_text(encoding='utf8'))
    root_password, app_password = passwords['root'], passwords['app']
    database = 'l2_' + profile['id']
    for kind in ['login','game']:
        set_ini(root/f'server/{kind}/config/Database.ini', {'URL':f'jdbc:mysql://{ip}:3307/{database}?useUnicode=true&characterEncoding=utf-8&allowPublicKeyRetrieval=true&useSSL=false', 'Login':'l2app','Password':app_password})
    (root/'server/game/config/ipconfig.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<gameserver address="{ip}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../data/xsd/ipconfig.xsd"><define subnet="127.0.0.0/8" address="{ip}" /></gameserver>
''', encoding='utf8')
    set_ini(root/'server/game/config/Custom/WorldContent.ini', {'CustomWorldOnly':'True','CustomSpawnDirectory':'data/environments/spawns','CustomScriptFolders':profile['scripts']})
    set_ini(root/'server/game/config/Custom/StartingLocation.ini', dict(CustomStartingLocation='True',CustomStartingLocX=profile['spawn'][0],CustomStartingLocY=profile['spawn'][1],CustomStartingLocZ=profile['spawn'][2]))
    set_ini(root/'server/game/config/Player.ini', {'StartingLevel':1})
    spawns = root / 'server/game/data/environments/spawns'
    spawns.mkdir(parents=True, exist_ok=True)
    if profile['id'] == 'academy':
        shutil.copy2(LAB/'server/game/data/lab/world-spawns/World.xml', spawns/'World.xml')
        target = root/'server/game/data/scripts/custom/AcademyWorld'
        target.mkdir(exist_ok=True)
        shutil.copy2(HERE/'AcademyWorld.java', target/'AcademyWorld.java')
        from patch_academy import patch
        patch(root)
    else:
        (spawns/'README.txt').write_text('No public spawns enabled yet. Add validated XML when promoting content to Hellgames.', encoding='utf8')
        target = root/'server/game/data/scripts/custom/HellgamesArrival'
        target.mkdir(exist_ok=True)
        shutil.copy2(HERE/'HellgamesArrival.java', target/'HellgamesArrival.java')
    guardians = root/'server/game/data/stats/npcs/custom/giran_lab_guardians.xml'
    if guardians.exists():
        guardians.write_text(guardians.read_text(encoding='utf8').replace('"../../xsd/npcs.xsd"','"../../../xsd/npcs.xsd"'), encoding='utf8')
    (root/'server/login/banned_ip.cfg').touch(exist_ok=True)
    cfg = f'''[mariadbd]
basedir={root.as_posix()}/tools/mariadb
datadir={root.as_posix()}/database/data
port=3307
bind-address={ip}
skip-name-resolve
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
max-connections=30
innodb-buffer-pool-size=128M
log-error={root.as_posix()}/logs/mariadb-error.log
'''
    (root/'database/my.ini').write_text(cfg, encoding='utf8')
    (root/'database/client.ini').write_text(f'[client]\nhost={ip}\nport=3307\nuser=root\npassword={root_password}\n', encoding='utf8')
    if not (root/'database/data/mysql').exists():
        result = subprocess.run([str(root/'tools/mariadb/bin/mariadb-install-db.exe'), '--datadir='+str(root/'database/data'), '--password='+root_password, '--port=3307', '--silent'], capture_output=True, text=True)
        if result.returncode:
            (root/'logs/database-init-private.log').write_text(result.stdout+result.stderr, encoding='utf8')
            raise RuntimeError('Database initialization failed; see private local log')
    # The installer emits its own my.ini in the data directory. Explicit defaults-file above is authoritative.
    out = (root/'logs/database-bootstrap-stdout.log').open('w')
    err = (root/'logs/database-bootstrap-stderr.log').open('w')
    db = subprocess.Popen([str(root/'tools/mariadb/bin/mariadbd.exe'), '--defaults-file='+str(root/'database/my.ini'), '--console'], stdout=out, stderr=err)
    (root/'run/database.pid').write_text(str(db.pid))
    cli = [str(root/'tools/mariadb/bin/mariadb.exe'), '--defaults-extra-file='+str(root/'database/client.ini')]
    try:
        for _ in range(90):
            if db.poll() is not None: raise RuntimeError('Database bootstrap exited')
            ping = subprocess.run(cli + ['--batch','--skip-column-names','-e','SELECT 1'], capture_output=True)
            if ping.returncode == 0: break
            time.sleep(.5)
        else: raise RuntimeError('Database bootstrap timed out')
        # Native schema only; never dump or copy Lab accounts/characters/items.
        sql = f'CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4; USE `{database}`;\n'
        for kind in ['login','game']:
            for source in sorted((LAB/f'server/db_installer/sql/{kind}').glob('*.sql')):
                text = source.read_text(encoding='utf-8-sig')
                assert not re.search(r'(?im)^\s*(USE |CREATE DATABASE|DROP DATABASE)', text), source
                if source.name == 'gameservers.sql':
                    text = re.sub(r'(?im)^INSERT INTO.*?;\s*$', '', text)
                sql += text + '\n'
        sql += f"CREATE USER 'l2app'@'127.0.0.1' IDENTIFIED BY '{app_password}'; GRANT ALL ON `{database}`.* TO 'l2app'@'127.0.0.1';\n"
        if not (root/'database/schema-ready').exists():
            r = subprocess.run(cli + ['--batch'], input=sql, text=True, capture_output=True)
            if r.returncode:
                (root/'logs/schema-import-private.log').write_text(r.stderr, encoding='utf8')
                raise RuntimeError('Schema import failed; see private local log')
            (root/'database/schema-ready').write_text(database)
        check = subprocess.run(cli+['--batch','--skip-column-names','-e',f'SELECT (SELECT COUNT(*) FROM {database}.accounts),(SELECT COUNT(*) FROM {database}.characters);'], capture_output=True,text=True,check=True)
        assert check.stdout.strip() == '0\t0', 'New environment unexpectedly contains account/character data'
    finally:
        subprocess.run([str(root/'tools/mariadb/bin/mariadb-admin.exe'), '--defaults-extra-file='+str(root/'database/client.ini'),'shutdown'],capture_output=True)
        db.wait(timeout=30); out.close(); err.close()
    print(profile['name'], 'clean database verified; copying client', flush=True)
    system = copy_client(root)
    # Change only this independent client's endpoint; no edits to Lab or Damage.
    node = LAB / 'tools/node-v24.22.0-win-x64/node.exe'
    codec = LAB / 'l2ini-local.js'
    subprocess.run([str(node),str(codec),'set',str(system/'l2.ini'),ip],capture_output=True,check=True)
    patcher = HERE/'client-profile.cjs'
    subprocess.run([str(node),str(patcher),str(system/'l2.ini')],capture_output=True,check=True)
    subprocess.run([str(node),str(HERE/'brand-client.cjs'),str(system/'servername-e.dat'),profile['name']],capture_output=True,check=True)
    shutil.copy2(HERE/'environment.gitignore', root/'.gitignore')
    if profile['id'] == 'hellgames': shutil.copy2(HERE/'HELLGAMES-DECISIONES-INICIALES.md', root/'DECISIONES-INICIALES.md')
    for name in ['Start-Environment.ps1','Stop-Environment.ps1','Status-Environment.ps1']:
        shutil.copy2(HERE/name, root/name)
    (root/'1-INICIAR.cmd').write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Environment.ps1" -ServicesOnly\r\npause\r\n',encoding='ascii')
    (root/'2-JUGAR.cmd').write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Environment.ps1"\r\nif errorlevel 1 pause\r\n',encoding='ascii')
    (root/'5-DETENER.cmd').write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-Environment.ps1"\r\npause\r\n',encoding='ascii')
    (root/'3-ESTADO.cmd').write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Status-Environment.ps1"\r\npause\r\n',encoding='ascii')
    profile.update(state='prepared', public=False, initialAccounts=0, initialCharacters=0,
                   sourceCoreSha256=hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest())
    (root/'environment.json').write_text(json.dumps(profile, indent=2),encoding='utf8')
    (root/'README.md').write_text(f'''# {profile['name']}

Entorno separado preparado el 17/10/2026. Dirección local {ip}; login 2106, juego 7777, enlace 19014, base de datos 3307.

- `2-JUGAR.cmd`: inicia sus servicios y su copia del cliente.
- `1-INICIAR.cmd`: solo servicios.
- `5-DETENER.cmd`: detiene exclusivamente procesos registrados de este entorno.
- Datos de personajes, cuentas, ejecutables, cliente, configs y logs propios. No se copió la base del Lab.
- No hay sincronización automática con Lab ni exposición a Internet. Hellgames es la base del futuro servidor público, todavía en preparación.
- Configuración de base local en database/client.ini y server/*/config/Database.ini: contienen credenciales; no publicar.
- Las bibliotecas y recursos son una copia del Lab de esta fecha; no implica que todos los experimentos estén aprobados. Solo se cargan los custom scripts del perfil.
''',encoding='utf8')
    print(profile['name'], 'PREPARED', ip, flush=True)

if __name__ == '__main__':
    selected = PROFILES if len(sys.argv) == 1 else [p for p in PROFILES if p['id'] == sys.argv[1]]
    assert selected, 'Unknown profile'
    for profile in selected:
        prepare(profile)
