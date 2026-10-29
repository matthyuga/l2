from pathlib import Path
import re
root=Path(__file__).resolve().parent
paths=[root/'README.md',root.parents[3]/'CABELLOS-INTEGRACION-20261023.md',root.parent/'README.md',root.parents[3]/'descarga de assets/cabellos/2026-10-23/LEEME.md',root.parents[3]/'research/resource-library/README.md',Path('K:/_CodexNexus/inbox/20261023-l2-cabellos-implementados.md')]
words='cosméticos Están también Cómo botón añadieron definición crónica catálogo además decodificación estadísticas cristalización menús Verificación reinició abrió exportación instalación Auditoría reparación comprobación restauración construcción todavía decisión economía público Actualización revisión Instalación continúa Validación técnica pidió únicos'.split()
for p in paths:
 s=p.read_text(encoding='utf8')
 for word in words:
  bad=re.sub(r'[^\x00-\x7f]','?',word)
  if '?' in bad:s=s.replace(bad,word)
 s=s.replace('28000?28012','28000–28012').replace('H0001?H0020','H0001…H0020').replace(' ? Cabellos',' → Cabellos').replace(' ? 23/10/2026',' — 23/10/2026').replace('IDs?nicos','IDs únicos')
 assert '?' not in s,p
 p.write_text(s,encoding='utf8')
