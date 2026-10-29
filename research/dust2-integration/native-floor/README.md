> Confirmación posterior de Kevin, 14/10/2026: «Sí, ahora pisos y paredes funcionan». Suelo y bloqueo de paredes confirmados por el usuario dentro de L2 tras instalar native-walls. Las incidencias y pendientes anteriores se conservan debajo como historial; no equivalen al estado actual. El critical de salida sigue sin confirmación de resolución.

# Soporte nativo continuo para Dust2 — 14/10/2026

Kevin confirmó que las bases nativas CT/T sí permitían caminar en algunas partes, pero al salir de ellas caía. Esto demuestra apoyo local real con actores nativos; la colisión del mapa importado sigue sin sostener el resto del recorrido. No certificar todavía la causa interna exacta del recurso importado.

Se instaló un soporte separado de la geometría visual: **1.591 actores de colisión con el cubo original `deco01.Box02`**, sin modificar su paquete ni su colisión nativa. Cada cubo se transforma como loseta rectangular invisible, 4u de espesor y0.1u de solape lateral para evitar juntas de coma flotante. BHidden oculta la representación; las propiedades de colisión permanecen explícitamente activas.

El soporte se genera desde la geodata instalada, conservando el componente navegable de61.234 capas conectado al inicio CT. Cubre también los40 inicios CT/T. Se agrupan celdas de igual altura en rectángulos de hasta64x64 celdas; no se unen pisos distintos. Las losetas superiores quedan a geoZ-43.35, según la calibración actual del proyecto. Es un suelo escalonado en rampas, con pasos según la geodata, no un gran plano horizontal. Los techos de pisos superpuestos no se rellenan con sólidos gruesos.

Las dos bases diagnósticas grandes anteriores quedaron ocultas, sin colisión y fuera de las referencias de myLevel para que no añadan bultos al recorrido. Se preservan5.103 payloads anteriores del mapa, exceptuando myLevel y esas dos bases. No se cambió geodata, servidor, reglas ni mapa visual de Dust2, muelle o aeronave. El coste añadido es1.591 actores estáticos compartiendo una malla de12 triángulos, no1.591 copias de un recurso pesado. El rendimiento dentro del cliente queda pendiente de observar.

## Evidencia y límites

- `verification.json`: las1.591 transformaciones deserializan con sus propiedades previstas; cobertura única de61.234 centros de capas;7.955 rayos contra triángulos nativos transformados (centro/corners por loseta), todos con soporte;40 spawns incluidos.
- Se verifica espesor4u, cobertura de esquinas y pequeños solapes sin huecos geométricos entre losetas de la misma altura.
- Paquete original Box02: caja rectangular de24 vértices/12 triángulos con secciones de colisión; no se usó el importador UE2 para construir estos colliders.
- Cifrado Ver121, CRC, preservación de payloads y hashes instalados comprobados.
- **Falta prueba real en cliente del soporte continuo.** Se pidió a Kevin reiniciar L2 y recorrer pasillos/rampas. No afirmar navegación completa o critical de salida resueltos solo con estas verificaciones.
- La colisión lateral de paredes importadas y LOS de combate todavía requieren comprobación independiente. El soporte es para suelo; las restricciones NSWE del servidor continúan aplicando.
- El critical de salida reportado13:41:19 (PurgeGarbage/anghel_fog/StaticExit) no tiene causa confirmada y no se declara corregido por este cambio.

## Instalación y restauración

Cliente cerrado al instalar; se sustituyó únicamente `E:/l2/Maps/24_19.unr`. Respaldo previo `E:/l2-local/backups/dust2-native-floor-20261014-135416`. El manifest principal `../installation.json` conserva el nuevo hash, de modo que `../restore.py` puede retirar toda la integración Dust2 y restaurar el estado previo a Dust2 con nave/muelle. Ese rollback completo exige cliente y GameServer cerrados.

Para revertir únicamente este soporte se puede restaurar el mapa de este respaldo con cliente cerrado y guardas de hash; actualizar el manifest principal si se hace. No ejecutar scripts históricos de muelle/nave sobre el mapa actual.

Reproducción: `build.py` solo prepara el mapa y el plan; `verify.py` verifica geometría; `install.py` aplica con guardas y respaldo. `build.py` rechaza añadir soportes duplicados. GameServer21308 continúa sin reinicio; LoginServer18184 intacto. Sin commit/push.
