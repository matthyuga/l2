# Dust2 V2: escala reducida, espejo y UV corregidos

Kevin mostró desproporción de personaje/peldaños; confirmó caminos en espejo y luego A boca abajo en captura. Se corrigieron tres cosas: escalaGoldSrc1.5->0.625 (41.67% anterior); reflexiónY alrededor141000,57000,8000; UVverticalV->1-V en37mallas/12.533coords. Geometría visual y texturas originales conservadas. Nueva geodata/colliders regenerados; NO solo escala visual.

Ruta real E:/l2-local/research/dust2-scale-v2. Instalado9archivos con respaldo E:/l2-local/backups/dust2-scale-v2-20261014-152101.561pisos/897paredes nativos,11.914capas conectadas y40spawns. Referencias a3.176colliders antiguos retiradas y exports desactivados. Muelle/nave intactos; Vigilia del Dragón sigue maqueta sin instalar.

GameServer14564 apagado sin clientes; nuevo20180. Login23432 intacto. PASS server-smoke:40pisos,192subidas de8/16u, movimiento/paredes/niveles/paz/respawn/viajesCT/T/regreso y pisos previos. Actual .dust2: CT14128055460Zefectivo7965; T14048057440Z8125.

**Pendiente validación visual/física de Kevin de la V2:** se preguntó si escala/escaleras/A/caminos ya correctos. Confirmación de pisos/paredes previa era para la versión grande, no trasladarla automáticamente. Critical anterior de salida anghel_fog/StaticExit sin resolución confirmada.

installation.json principal Dust2 actualizado con hashes actuales y current_version scale-v2. Restore local V2 vuelve solo a versión grande; restore principal retira todoDust2 conservando estado previo de nave/muelle. Ambos con cliente/GS cerrados y guardas. Ver README de V2. Sin commit/push.
