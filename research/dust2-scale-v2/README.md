# Dust2: escala, espejo y texturas V2 — 14/10/2026

Kevin reportó que el mapa era demasiado grande para el personaje, ciertos peldaños no se podían subir y los caminos estaban reflejados. Confirmó explícitamente «Los caminos están en espejo». Después mostró una captura donde la señal A y la franja decorativa aparecían boca abajo. Se corrigieron tres problemas separados.

## Instalado

- Escala anterior1.5 unidades L2 por unidad GoldSrc -> **0.625**. Tamaño lineal actual41.6667% del anterior. Actores visuales DrawScale0.2 sobre mallas de3.125 unidades por unidad BSP.
- Reflexión en ejeY respecto del origen141000,57000,8000 para corregir la disposición en espejo. Transformación: X=141000+0.625*xCS, Y=57000-0.625*yCS, Z=8000+0.625*zCS. Los37 actores visuales usan DrawScale3D(1,-1,1), materiales existentes de doble cara.
- Inversión vertical de UV V->1-V en12.533 coordenadas de las37 mallas. La textura PNG exportada del recurso nativo era idéntica a la imagen de entrada, mientras las UV nativas conservaban la convención vertical de Blender. Se cotejó además una muestra de SandTrim con las coordenadas S/T del BSP original. No se editó la imagen para disimular el fallo; se corrigió el mapeado.
- Geodata y colisiones **regeneradas** con la transformación nueva. No se escalaron solamente las mallas visuales dejando debajo las losetas antiguas.
- Nuevas llegadas CT141280,55460 (suelo7960; llegada efectiva7965) yT140480,57440 (suelo8120; llegada efectiva8125), handler y zonas peace/respawn actualizados runtime/source/cloud.

La escala toma como referencia el hull humano de72u del [SDK GoldSrc de Valve](https://github.com/ValveSoftware/halflife/blob/master/dlls/util.h), que se convierte en45u; el perfil humano local de L2 usa collisionHeight23. Es una calibración inicial de proporción, pendiente aceptación visual con el personaje real, no una igualdad certificada de las dimensiones de todas las razas.

## Suelos, paredes y escalones

El generador trabaja en una copia y usa clearance64 y fusión vertical8, apropiados a la nueva escala, sin modificar globalmente geolib ni otras zonas. Se preserva el régimen de paso ascendente<=16u. La envolvente nativa sigue usando el cubo original deco01.Box02.

-15.063 celdas añadidas a geodata,366 multicapa.
-11.914 capas alcanzables desde CT; los40 inicios CT/T conectados.
-561 losetas de suelo y897 paredes nuevas.
-2.589 bordes cerrados cubiertos;44.735 conexiones dirigidas abiertas comprobadas sin conflicto con paredes de otros niveles.
-1.569 conexiones ascendentes en8o16u, de las que se muestrearon192 para prueba real del GameServer.

Se desactivaron y retiraron de myLevel las3.176 referencias de colisiones antiguas(bases iniciales,1.591 pisos y1.583 paredes), que permanecen como exports históricos ocultos/sin colisión. Los actores nuevos tienen prefijosHGDust2V2Floor yHGDust2V2Wall. Se conservan byte por byte5.066 payloads ajenos a Dust2 fuera de myLevel, incluidos muelle y aeronave.

La geodata se reconstruye sobre el respaldo anterior a Dust2, que ya contenía muelle y nave. **Antes de instalar se comprobaron hashes de todos los archivos instalados y de la geodata actual**, para no descartar cambios concurrentes. No usar ese respaldo como base si el archivo actual tiene cambios ajenos sin integrar.

## Validación y límites

- Las37 mallas conservan exactamente geometría y normales; todas las UV cambian solo V según lo previsto; lazy offsets nativos de colisión se rebasan.
- Mapa final releído; se verifican nuevas escalas y que ninguna referencia a colisión antigua permanezca en myLevel.
- Cobertura geométrica del soporte, esquinas, pequeños solapes y espesor4u verificados. Paredes verificadas contra pasos abiertos por nivel.
- Cifrado Ver121, CRC y roundtrip íntegro de ambos paquetes antes de instalar.
- GameServer activo nuevo20180, anterior14564 apagado ordenadamente sin clientes conectados. LoginServer23432 no se reinició.
- `server-smoke.txt`: PASS con Player transitorio, sin personaje persistente:40 alturas de inicio,192 subidas, pasos abiertos/bloqueados, pisos superpuestos, paz/respawn, comandos CT/T y regreso al origen. Pisos de muelle/nave/Coliseo conservados.
- **Pendiente prueba de Kevin dentro del cliente**: proporciones, escaleras, A derecha y caminos sin espejo. El PASS del servidor no certifica física/visual/cámara ingame. La confirmación del usuario de pisos/paredes del paso anterior pertenece a la versión grande, no valida automáticamente esta versión reducida.
- El critical anterior al cerrar(anghel_fog/StaticExit) sigue sin resolución confirmada. No se modificó el sistema de aeronave nueva ni se integró Vigilia del Dragón.

## Respaldo y reproducción

Instalados9 archivos con respaldo `E:/l2-local/backups/dust2-scale-v2-20261014-152101`. `installation.json` registra hashes antes/después; el manifest principal `../dust2-integration/installation.json` se actualizó para que su rollback completo siga funcionando.

`restore.py` retira solo V2 y restaura la versión grande anterior con pisos y paredes: requiere cliente y GameServer cerrados y hashes intactos. El restore principal de Dust2 retira todo Dust2 y vuelve al estado previo a Dust2 con muelle/nave. No ejecutar instaladores históricos sobre este mapa modificado. Sin commit/push.

`prepare.py` prepara visual/UV/desactiva colisión previa y genera el build de geodata aislado; `build_geodata.py` reconstruye capas; `prepare_colliders.py` adapta los constructores anteriores sin tocar sus fuentes; ejecutar native-floor/build+verify y promover su mapa staged antes de native-walls/build+verify; `prepare_server.py`, prepare_smoke.py yprepare_stair_probe.py preparan comandos y pruebas; `verify_stage.py` verifica/cifra; `install.py` instala con guardas y respaldo. Es un pipeline secuencial, no reejecutar pasos de forma ciega sobre la instalación ya actualizada.
