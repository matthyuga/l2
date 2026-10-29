# Correccion de emblemas de clan y alianza — 10/10/2026

El cliente fallo al importar `crest.crest_2_1`: dimensiones 16x12 no eran potencias de dos.
La instalacion anterior habia enviado DDS DXT1 clan16x12 y ally8x12. El dibujo visible tiene esas medidas, pero la textura DDS necesita altura16.

Corregidos los seis emblemas: DDS clan16x16 (256bytes), ally8x16 (192bytes). Dibujo superior de12filas conservado exactamente, comprobados los bloques DXT1 byte por byte; cuatro filas inferiores de relleno negro. Sin reescalar el dibujo. Nuevas IDs7–12 para evitar que el cliente reutilice las copias antiguas. No se necesita borrar cache ni editar el cliente.

PrepareCrests.java ahora valida los PNG originales16x12/8x12 y genera DDS con altura16 y controles de cabecera/tamano. Aplicacion transaccional guarded por estado anterior y ausencia de jugadores, con GameServer detenido. Solo se cambiaron crest_id/ally_crest_id y blobs nuevos: clanes, niveles, alianzas, lideres y miembros identicos. Core, buffs summons, Amber, pilotos, skills y cliente sin cambios.

Backup: backups/crest-pow2-2026-10-10 contiene seis DDS anteriores, snapshotDB antes/despues y logs. Artefactos y scripts: crest/pow2. DDS corregidos tambien en crest/prepared. No repetir apply con --apply despues de instalar.

Verificacion: seis DDS validos dentro del limite nativo, compresion y dibujos originales intactos, IDs renovadas, snapshot de clanes/miembros sin cambios funcionales, GameServer carga seis crests y prepara19/19 rivales. JAR y archivos cliente conservan fingerprints anteriores. Pendiente que usuario confirme visualmente entrada y emblemas. No se inicio combate ni se abrio su cliente.
