from pathlib import Path
import json,hashlib,zipfile,pefile
D=Path(__file__).resolve().parent;P=Path('E:/l2-local')
tests=json.loads((D/'build/native-test-results.json').read_text());assert tests['passed']==4121
p=pefile.PE(str(D/'build/NexusHairHslUi.dll'));assert p.FILE_HEADER.Machine==0x14c
exports=[e.name.decode() for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name];assert all(n in exports for n in ['NexusHslOpen','NexusHslRead','NexusHslSet','NexusHslFinish'])
raw=(D/'build.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf8',errors='replace');assert '50 open/preview/apply/close cycles' in log
m=json.loads((P/'research/character-creation/2026-10-26-orc-faces-removed-v14/installation.json').read_text())
for r in m['files']:assert hashlib.sha256(Path(r['target']).read_bytes()).hexdigest()==r['after_sha256']
files=['hsl_picker.h','hsl_math.h','hsl_picker.cpp','hsl_picker.def','demo.cpp','dll_test.cpp','build-native.cmd','README.md','native-interface.png','build/NexusHairHslUi.dll','build/NexusHairHslDemo.exe','build/preview-original.png','build/native-test-results.json']
archive=D/'Interfaz-HSL-nativa-preparada.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(D/name,name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(D/'verification.json').write_text(json.dumps(dict(native_checks=4121,dll_cycles=50,dll_exports=exports,architecture='x86',active_v14_hashes_unchanged=True,game_integration=False,source_sha256={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in files}),indent=2),encoding='utf8')
(D/'index.html').write_text('''<!doctype html><html lang="es"><meta charset="utf-8"><title>Interfaz HSL preparada</title><style>body{background:#121922;color:#e5dfcf;font:17px Arial;max-width:1000px;margin:40px auto;padding:24px}p{line-height:1.6}a{color:#e8c486}img{max-width:100%;border:1px solid #96845c}</style><h1>Interfaz HSL nativa preparada</h1><p>Ventana Windows de 32 bits, con aspecto adaptado a L2. No está instalada ni conectada al creador o al servidor.</p><p><a href="build/NexusHairHslDemo.exe">Abrir demostración local</a> · <a href="Interfaz-HSL-nativa-preparada.zip">Descargar componente y fuentes</a> · <a href="../2026-10-26-hsl-selector/index.html">Vista previa 3D con colores</a></p><img src="native-interface.png" alt="Ventana nativa HSL con tono, saturación, luminosidad y botones Original, Aceptar y Cancelar"><p>En el demo, la muestra de color cambia y se prueban Aceptar/Cancelar. La imagen de personaje del demo es fija. El prototipo 3D anterior permite ver el tinte sobre los modelos reales. El siguiente paso es conectar ambos comportamientos al motor y al estado del creador.</p></html>''',encoding='utf8')
for page in [P/'research/character-creation/2026-10-26-mega-audit/galeria/index.html',P/'research/character-creation/2026-10-26-mega-audit/comparison/index.html']:
 s=page.read_text(encoding='utf8');label='Ver interfaz HSL nativa preparada'
 if label not in s:
  pos=s.index('</h1>')+5;s=s[:pos]+'<p><a href="../../2026-10-26-hsl-native-ui/index.html">'+label+'</a> · sin instalar en el juego</p>'+s[pos:];page.write_text(s,encoding='utf8')
note='''Interfaz HSL nativa preparada: DLL y demo Win32 x86, HSL/HEX, botones y callbacks transaccionales. 4121 comprobaciones nativas, 50 ciclos DLL sin crecimiento de handles. Screenshot nativo revisado. No integrado/instalado al juego; v14 activo sin cambios. Paquete research/character-creation/2026-10-26-hsl-native-ui/Interfaz-HSL-nativa-preparada.zip, README con contrato y limitaciones.'''
with (P/'BITACORA-TANDA2-PEINADOS-20261026.md').open('a',encoding='utf8') as f:f.write('\n\n'+note+'\n')
Path('K:/_CodexNexus/inbox/20261026-l2-hsl-interfaz-nativa-preparada.md').write_text('# L2: interfaz HSL nativa preparada, no instalada\n\n'+note+'\n\nRuta real E:/l2-local/research/character-creation/2026-10-26-hsl-native-ui. No afirmar integrada en creador. Falta botón/puente, renderer dinámico y persistencia/sincronización. Demo cambia swatch, imagen fija; prototipo WebGL anterior sí tiñe modelos. No archivos activos de L2 modificados. Galería tiene enlace de revisión.\n',encoding='utf8')
print('PASS: x86 exports, 4121 native checks, 50 DLL cycles; ZIP CRC valid; active game files unchanged.')
