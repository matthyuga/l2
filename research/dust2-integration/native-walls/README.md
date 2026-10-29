> Confirmación posterior de Kevin, 14/10/2026: «Sí, ahora pisos y paredes funcionan». Suelo y bloqueo de paredes confirmados por el usuario dentro de L2 tras instalar native-walls. Las incidencias y pendientes anteriores se conservan debajo como historial; no equivalen al estado actual. El critical de salida sigue sin confirmación de resolución.

# Paredes y límites de soporte nativo — 14/10/2026

Kevin confirmó mejora con el soporte continuo de suelo, pero volvió a caer después de atravesar partes del mapa. Se necesita colisión lateral, además de apoyo vertical. No se da por resuelto el mapa por la mejora parcial anterior.

Se añadieron **1.583 actores de colisión nativa `deco01.Box02`**, invisibles, que cubren5.434 bordes cerrados de la geodata conectada de Dust2. Usan una malla original del cliente sin modificar sus datos. Las paredes tienen2u de espesor y hasta384u de altura sobre el suelo; se limitan antes del siguiente piso cuando corresponde. Los segmentos largos se agrupan hasta64celdas y tienen0.2u de solape para cerrar juntas. Las1.591 losetas de soporte de piso anteriores permanecen intactas.

Esto es una envolvente de colisión basada en la cuadrícula de geodata de16u, **no una reconstrucción exacta por polígonos de cada pared visual de CS**. Puede haber pequeños desfases respecto de las texturas, esquinas con colisión escalonada y puertas/pasos que requieran calibración en el cliente. No afirmar que toda la física del recurso importado se reparó: se usa soporte nativo independiente porque el importado sigue sin sostener/bloquear correctamente.

Los bordes abiertos se conservan. En particular se respetan320 descensos dirigidos con destino apoyado. Ocho bordes ambiguos en esquinas de rampas/escaleras se omiten porque compartían una transición abierta a una altura próxima; la primera verificación detectó que invadían pasos válidos y se corrigió antes de instalar. No se levanta una pared gruesa atravesando túneles: se limita la altura con los pisos superiores.

## Comprobaciones

- Relectura de los actores añadidos y verificación de sus flags de colisión, ocultación, transformación y extensión nativa.
- Cobertura exacta de los5.434 bordes planificados por las1.583 cajas.
- Comprobados239.100 pasos dirigidos abiertos contra barreras de otras alturas:0conflictos en las líneas centrales de las celdas. Esto no certifica aún todas las holguras de la cápsula del personaje en esquinas/puertas.
- Se conservan1.591 actores de piso, los payloads previos del mapa fuera de myLevel y la geodata instalada. Nave/muelle no se modifican.
- Cifrado Ver121, CRC y payload completo verificados antes de copiar; hashes instalados y manifest principal actualizados.
- **Pendiente prueba ingame por Kevin** de paredes, puertas y rampas. No se declara solucionado el critical de salida anghel_fog/StaticExit ni la LOS de combate.

## Instalado

Kevin confirmó cliente cerrado antes del cambio. Se sustituyó solo `E:/l2/Maps/24_19.unr`; no se cambió GameServer21308 ni se reinició LoginServer18184. Respaldo previo `E:/l2-local/backups/dust2-native-walls-20261014-140156`.

`build.py` prepara desde el mapa y geodata actuales sin instalar; rechaza duplicados. `verify.py` comprueba geometría y pasos abiertos; `install.py` instala con guardas y respaldo. El manifest principal `../installation.json` mantiene el hash actual para su rollback completo. No aplicar instaladores históricos encima del mapa actualizado. Sin commit/push.
