# L2 — corrección recepción de exploración V4.1

Proyecto real E:\l2-local; cliente E:\l2\system-hud. El usuario probó V4 y
Goddard seguía oculta. Servidor sí guardó exploración y ciudades; cliente logueaba
REJECTED malformed fog snapshot. No se midió el límite exacto del texto nativo.

25/10 23:24: instalado transporte fragmentado64 caracteres, validación/reunión
completa antes de aplicar. DLL y dos scripts en runtime/fuente respaldados en
backups\exploration-walking-v4-chunks-20261025-232334. Sólo GameServer reiniciado
con L2 cerrado por el usuario. Exploración existente conservada.

Detalles: research\exploration-walking-v4\CHUNK-FIX.md e installation.json.
Pruebas Java95, nativas20467, D3D9 HAL. Falta validación REAL del cliente L2.
No afirmar éxito visual todavía. Buscar RECEIVED complete chunked personal/global
exploration snapshot en NexusMapFog.log después de entrar. Si falla, diagnosticar
recepción de fragmentos; no resetear el mapa ni variables FOG4.
