# Gludio Sky Dock

Integración local de prueba sobre el Coliseo, 14/10/2026.

Leer primero [MUELLE-AEREO-GLUDIO.md](../../MUELLE-AEREO-GLUDIO.md).

- `.muelle`: acceso para personajes existentes, desmontados y fuera de combate/instancias.
- `.muelle coliseo`: descenso al área de práctica.
- Nacimiento de personajes nuevos: 149000,46700,12040.
- `installation.json`: estado instalado y respaldo exacto; `restore.py` verifica hashes antes de restaurar.
- `stage-proof.json`, `geodata-audit.json`, `material-conversion.json`, `native-load-proof.json`, `installed-native-load-proof.json`, `wrapper-proof.json`: evidencias.
- Primera validación visual y recorrido dentro del cliente pendientes.

Los scripts build/install son reproducibles desde la base anterior, no finalizadores para reejecutar sobre el mapa ya instalado. No ejecutar restore si otra sesión modificó los mismos archivos: sus guardas abortan en ese caso.
