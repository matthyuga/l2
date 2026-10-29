from pathlib import Path
import re
import sys

client = Path(__file__).resolve().parents[3] / 'l2/system-hud'
config = client / 'NexusMapFog.ini'
action = sys.argv[1] if len(sys.argv) == 2 else ''
if action not in ('partial', 'total', 'off', 'anchor'):
    raise SystemExit('Uso: control.py partial | total | off | anchor')
text = config.read_text(encoding='ascii')
if '[MapFog]' not in text:
    raise SystemExit('Configuracion de prueba no reconocida.')
if action == 'anchor' and 'Layout=GiranV2' in text:
    print('Giran tiene una ubicacion fija: esta version ya no necesita centrar el rectangulo.')
    raise SystemExit(0)
key = 'Revision' if action == 'anchor' else 'Mode'
match = re.search(r'(?m)^' + key + r'=(\d+)\s*$', text)
if not match:
    raise SystemExit('Falta parametro: ' + key)
value = int(match.group(1)) + 1 if action == 'anchor' else {'off': 0, 'partial': 1, 'total': 2}[action]
text = text[:match.start(1)] + str(value) + text[match.end(1):]
config.write_text(text, encoding='ascii')
print({'partial': 'Cobertura semitransparente.', 'total': 'Cobertura opaca.', 'off': 'Cobertura apagada.',
       'anchor': 'La cobertura se centrara en la vista actual del mapa.'}[action])
print('El cambio se aplica al dibujar el mapa, en un segundo como maximo.')
