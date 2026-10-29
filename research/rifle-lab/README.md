# Rifle Koikatsu → L2: M4A1 prototipo

15/10/2026. Usuario solicita buscar AK47/M16/rifle en Koikatsu y, si viable, integrarlo como arma. Esta sesión no toca salasPvP de la otra sesión.

## Qué se encontró
M4A1 identificado en CSV y prefab [mk90]M4A1 del zipmod [MakotoYuki90]Fantasy Weapons Pack2, en K:/JUEGOS/KOIKATSU22 (ruta real con espacio KOIKATSU 22). Fuente/manifest SHA256 exacto en models/M4A1/provenance.json. Modelo con ACOG, accesorios y Masterkey:20renderer parts,20944carasfuente,12texturasPNG. No se afirma ausencia global deAK47/M16: solo búsqueda acotada de packs/inventario. Todosoriginales read-only.

También pack real AgiShark/MixamoStudio categoríaGun: Aim/Fire/Reload/RifleIdle/Run/Cover. Seisclipsextraídos a JSON580huesos60fps,384/384bindingsresueltos0unknown; nombres/CSV/hash en motions/README.md. Rifle genérico, sin asociación específicaM4. No cargadorcomoobjeto/recarga funcional probado.

## Conversión y prueba
- Arma standalone build/HGRifleM4A1.ukx, SkeletalMesh M4A1,1hueso,12materiales+RifleIcon. Malla20931caras tras importación/exportaciónBlender (13menos quefuente; fuente no tienecarasdegeneradas probadas, no atribuir reducción a13degeneradas sin evidencia).
- NPC build/HGRifleDemo.ukx/RifleMesh: cuerpoFighter mujer76huesos +rifle anclado mano derecha,23048caras13materiales; poseIdle_Aiming adaptada, mano izquierda sostieneguardamanos. Vista lateral inspeccionada build/RifleNPC-side-first.png; falta clienteL2. Posición/agarre weaponstandalone necesita comprobación equipando, no inferir delNPCcombinado.
- Animación build/HGRifleMotion.ukx exportDust2Motion/seqwait_Hand desde build/Idle_Aiming_FFighter.psa,126frames60fps. Fire_Rifle_FFighter.psa/blend también adaptado para editor, no asignado todavía a skill/disparo.
- Texturas fuente convertidas opacasRGB (alpha Unity puede máscara), tamaño máximo1024pow2. Se conserva diseño, no shadersPBR completos. UCC usa imágenes sinDXT por xDxTexausente. Paquetes ~71MB cada uno por mipmapsRGBA sinDXT; potencial optimización futura.
- build/native-validation.json: UModelrecargaexportaarma1hueso+NPC76,carasigualPSK,12/13texturasadaptadaspíxelesexactos; offsets/tamaños todos exports delUCCoriginalpreservados; solo1byteAnimation meshNPCcambiado. Evita critical previo de malla reubicada. No confirma rendercliente.

## Instalado
Cliente SOLO laboratorio E:/l2-local/research/dust2-animation-study/client-lab. L2 estaba cerrado antes de copiar. weapongrp yitemname413roundtripPASS:1621registrosarmas y9765nombres anteriorespreservados +1. npcgrp preservado +display59083. Trespaquetes nuevos enlab/animations. Perfilhabitual E:/l2/system-hud intacto.

Objeto ID32580 M4A1-Prototipo, categoríaBOW,LR_HAND,EQUIP,baseShortBow13 sin grado. Mantiene reglas/arrows/MP/cadencia animaciones dearco de referencia. No balas,ráfagas,muzzleflash,daño nuevo,recarga real ni tipoRIFLE implementados. Icon propio HGRifleM4A1.RifleIcon. No se entregó objeto a personaje ni se modificó inventario/DB.

XML nuevo32580-rifle-prototypes.xml agregado runtime server/game/data/stats/items,source/dist ycloud-overlaylocal con mismoSHA. No core/clases/scriptsPVP ni archivospreexistentescambiados. Registro enGSactual27412 mediante RiflePrototypeItems agent: soloañade template32580 aarrays/map yXMLruntime a_itemFiles para reload,futurosarranques. Resto templates mantienen identidad. No reinicio por esta sesión. El GS25176anterior ya había sido reemplazado por otro trabajo; siempre detectarPIDantesdeattach.

Auditoría real build/runtime-audit.txt PASS:32580esWeaponBOW,LR_HAND,EQUIP yiconcustom, igualbase; no itemscreados. getBaseAttackRange40es propiedadbase deltemplate; XMLstats pAtkRange500esmodificadordeestadísticas, no afirmar alcance efectivo probado solo porgetterbase.

Prueba manual arma: SOLO cliente lab y GM //create_item 32580 1, luego equipar. Este comando crea itempersistente al ejecutarlo; no lo ejecutamos por el usuario. No abrirperfilhabitualconesteitem hasta instalar allí susrecursos/catálogos.

## NPC de vista
build/m4-demo.jar AgentClassM4A1DemoAgent cargadoGS27412. ID902683/display59083, nombre M4A1-Apuntado. EsperaHellkevin10min, aparece85u enfrente/sameinstance/GeoEngine, invulnerable, limpia20min trasspawn. build/rifle-runtime.txt estado. Sinplantillapersistente/DB/coremodificado. NO reejecutarmientrasactivo. Se lanzó clientelabactualizado; visualingamependiente delusuario.

## Recuperación y continuidad
build/installation.json tieneSHAantes/después ybackups. No reejecutar install_rifle.py ni loaders sobreIDyaactivo. Para rollback cerrarclienteyverificarSHA,cuidadoitems32580persistidos: no quitar template si existeninstancias. El NPC puedeeliminarse con agente transitorio que accedeM4A1DemoAgent.npc/timer; no tirarGS. No restaurarcatálogosviejos encimaadicionesposteriores.

Código reusable: models/extract_m4.py,motions/extract_rifle_motion.py (nombre exactover carpeta),build/retarget_rifle.py,build/build_rifle.py,compile_rifle.py,link_npc.py,verify_native.py,install_rifle.py; items/stage_items.py yloader. No commit/push;Nexusnotabreve.

Acceso manual E:/l2-local/PROBAR-M4A1-L2.cmd creado para abrir perfil lab correcto. Intento deStartProcess seguía pendiente y no había procesoL2observado alúltimochequeo; no declarar cliente abierto. SiNPCespera expira, readrifle-runtimeantes reactivar. Esto no afecta disponibilidad item32580 enservidor.

## Critical de inicio y correccion V2 (15/10/2026)
El cliente inicial fallo en FL2NpcData::Serialize / NpcDataLoad durante InitEngine (captura 16:37:11). El NPC tenia 13 texturas; el resto del catalogo llegaba a 5. Sospecha de incompatibilidad de la entrada; no se ha probado un limite exacto del motor. Se desactivo el agente/NPC anterior con remove-m4.jar sin reiniciar GS ni tocar IA de bots.

Se hornearon los 12 materiales originales a un atlas de albedo 2048x2048, respetando UV repetidas mediante bake de Blender. Arma V2: 1 material; NPC V2: 2. Paquetes HGRifleM4V2.ukx y HGRifleDemoV2.ukx instalados SOLO en cliente lab. Se modificaron exclusivamente filas32580 de weapongrp y59083 de npcgrp; otras filas preservadas exactas. Icono conserva paquete anterior. No cambios adicionales de servidor/XML/IA.

Evidencia: build/atlas-validation.json, atlas-native-validation.json (caras y pixeles de atlas exactos tras exportar paquetes), atlas-fix-installation.json (SHA), atlas-fix-backup. No repetir instalador: backups con guardia. UV exportada es RifleAtlasUV. Primer intento de atlas por tiles se rechazo por UV fuera de rango; usar bake_atlas_v2.py.

Se abrio cliente corregido. Usuario confirmo por respuesta: "Llego al acceso / estoy en Giran". Esto confirma superado el critical de inicio; render en juego del NPC/arma sigue pendiente. Agente V2 m4-demo-v2.jar vuelve a colocar SOLO NPC temporal al conectar Hellkevin (ID902683/display59083), enfrente85u, limpia20min. Estado rifle-runtime-v2.txt. Clase anterior permanece desactivada; no reactivar agentes duplicados. No se concedieron items. Otra sesion trabaja en cerebro IA de bots: no modificar ni reiniciar servidor por esta demo.

## Vista real V2 y correccion de malla V3 preparada
Usuario envio capturas: NPC visible, rifle con triangulos negros estirados hacia los pies y NPC suspendido. Diagnostico runtime position-audit.txt: personaje Z=-3431, NPC Z=-3401 (geodata lo subio30u). NO certificar V2 visual como correcta.

RifleNPCV2 tenia61229wedgesPSK/60548 tras UCC y23048caras combinadas. Hipotesis: presupuesto/indices de malla del cliente antiguo; limite exacto NO demostrado. Preparado V3 con soldadura de vertices coincidentes y decimacion solo rifle; asignacion rigida completa a mano derecha. Rifle3557caras, NPC5675; UCC exporta7880/11660wedges. mesh-v3-validation.json compara caras con posiciones/materiales/pesos y atlas pixel exactos tras UCC. Vista offline RifleNPCV3-side-first.png inspeccionada, sin los estiramientos. No prueba juego todavia.

Preparados build/install_mesh_v3.py con guardia L2cerrado + SHAesperados V2 y backup nuevo (no reejecutar tras instalar); paquetes HGRifleM4V3 y HGRifleDemoV3. Preparado agente M4A1DemoAgentV3 que retira V2 y genera demo temporal, esta vez Z del jugador en lugar de plataforma GeoEngine30uarriba. Estado futuro rifle-runtime-v3.txt. Al momento de esta nota: aun NO instalado/adjuntado V3; se pidio al usuario cerrar cliente. No tocar IA/core ni reiniciar servidor de otra sesion.

V3 INSTALADO tras confirmacion de cierre del usuario (15/10/2026). install_mesh_v3.py termino correctamente: npcgrp6527 y weapongrp1622, SOLO filas59083/32580 cambiadas, demas registros identicos. Backup mesh-v3-backup, manifiesto mesh-v3-installation.json. Se confirmo que no habia L2 activo. GS27412 sigue el mismo; se espero a que el attach ajeno mechanics-v2.jar terminara antes de adjuntar agente de demo.
M4A1DemoAgentV3 adjuntado: retira V2, espera Hellkevin; estado rifle-runtime-v3.txt. Cliente lab reabierto. Prueba visual V3 pendiente. No nuevos cambios en IA/core/XML ni reinicios ni items concedidos.

V4 preparada 15/10: ver E:\l2-local\research\rifle-lab\v4-build\README.md. Cuerpo con texturas reales y cara faltante restaurada, seis estados distintos, contacto mano izquierda corregido. 19 verificaciones nativas PASS, preview six-states.png offline. Origen malla25/rot49152 y colision demo25 para compensacion vertical (validacion juego pendiente). Instalador con guardias y ciclo visual NPC12seg/estado listo; se pidio cierre cliente antes de instalar. No afirmar V4 instalada aun: revisar installation.json y rifle-runtime-v4.txt. No tocar AI/core ni reiniciar servidor de otra sesion.

V4 INSTALADO tras cierre confirmado por usuario. v4-build/install.py finalizo: backup y installation.json, solo cliente laboratorio, catalogo npcgrp6527->6533 y ocho paquetes nuevos; comprobados SHA. GS27412 confirmado mismo proceso, sin attach ajeno activo. m4-demo-v4.jar adjuntado una vez: retira V3, READY espera Hellkevin para ciclo6estados12s. Cliente lab solicitado abrir. Verificar procesoL2 y rifle-runtime-v4.txt; apariencia/altura ingame aun pendientes, no declarar solucionadas sin captura. Sin reinicio ni cambios AI/core/DB/inventario.

V5 INSTALADA 15/10 por feedback visual V4: pies corregidos (toes rigidos/rest foot +yaw), mirada aim/fire alineada con rifle, corte geometrico alpha del pelo para evitar zonas negras, ciclo continuo de1NPC sin respawn entreestados. Ver v5-build/README.md y native-validation.json. Solo lab npcgrp filas59083/59084 +3paquetes, SHA/backups en installation.json. GS27412 mismo, m4-demo-v5.jar adjuntado1vez; retiraV4 y espera Hellkevin, estado rifle-runtime-v5.txt. Cliente lab reabierto. Validacion visual V5 aun pendiente; no afirmar altura/negro resueltos definitivamente.
Usuario aclara objetivo final: especializacion/clase APRENDIBLE por jugador para rifle, no NPC final. Esta pasada sigue banco de pruebas; NO implemento clase, balas,damage, progresion ni inventario. IA bots de otra sesion intacta, sin reinicio.
