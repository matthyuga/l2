# Dust2: bomba y animaciones de Studio — investigación inicial

15/10/2026. Usuario indica que salas PvP están en otra sesión. Alcance aquí: estudiar bomba estilo CS y movimientos de Koikatsu para acciones L2. No se modificaron runtime, cliente, DB ni scripts compartidos de salas.

## Observado
- REA inspect_managed_artifact sobre CharaStudio_Data/Managed/Assembly-CSharp.dll confirma Unity/Mono, CIL, metadata completa. SHA256 361ee4c5a7dafbfa56845bb0a71a034ef388ce07663b7709b858136eb3486958; MVID cdaa1658-214e-4370-bd5b-16aee18cdad1. Evidencia padre ev_57aeb5f6ff6b394d25f0c523e243d85ccc7b6098e4ca83418acea5123ec61dc4, resumen ev_39e15bd4dacafaab76d0b37e270109f8bbce1bc96f1b3788929cc70eabe0e348. Inspección estática, sin ejecutar ni decompilar.
- UnityPy local lee abdata/studio/anime/00.unity3d (412 AnimationClip,18 AnimatorController) y 04.unity3d (66 clips,2 controllers). No son 478 movimientos distintos garantizados: hay nombres repetidos, poses y clips cortos.
- Ejemplo f_tachi_00_12: 30 fps,6.5s,963 bindings,197 frames densos/236 curvas. Canales serializados en m_MuscleClip.m_Clip.data. Las listas externas vacías de Rotation/Position/Float no significan ausencia de movimiento.
- inventory_studio.py produce studio-animation-sample.json con nombres, duración, identificadores, canales y hashes. No exporta ni adapta movimientos; no se eligió candidato por apariencia.
- research/amber-l2/README.md documenta esqueleto humano Fighter de76huesos y ruta Blender/PSK. Documenta también importación PSA mediante UCC incompatible con UModel; Amber resolvió reutilizando movimiento NATIVO. No demuestra importación de un movimiento nuevo de Studio ni soporte para jugadores.

## Ruta propuesta, aún sin validar
1. Seleccionar visualmente un movimiento sencillo agachado/manos a objeto; registrar paquete e ID, y si depende de IK/FK o Timeline.
2. Exportar con rig/avatar de origen o capturar/bakear pose evaluada si necesita Animator/IK. AssetStudio soporta exportación FBX de Animator con AnimationClips vinculados; compatibilidad de este clip concreto pendiente.
3. Retarget en Blender a UN esqueleto nativo L2. Corregir raíz, ejes, escala, rodillas, pies y manos; producir entrada/bucle/salida. No transferir automáticamente la malla Koikatsu.
4. Resolver serialización MeshAnimation compatible con el cliente Interlude antes de instalar. Un PSA o FBX legible en Blender no basta. No reutilizar sin comprobar la ruta UCC que falló antes.
5. Probar reproducción para un cuerpo L2 en paquete/copia de cliente aislados, y luego conexión con skill/acción. MagicSkillUse/SocialAction por sí solos no transmiten una animación arbitraria nueva. Resto de razas/sexos y observación por otros clientes pendientes.

## Diseño de bomba, no implementación
Usuario pide colocación con casteo y desactivación lenta sin kit/rápida con kit. Duraciones no fijadas. Propuesta: servidor gobierna plazo; animación tiene bucle independiente. Estados posible: transportada, colocando, plantada, desactivando, desactivada/explotada. Validar bando, zona/distancia, vivo, objeto/kit y exclusión de acciones simultáneas; decidir cancelación por movimiento/daño/control y empate desactivación/explosión. Kit comprobado por servidor, no velocidad de casteo del personaje. Reglas exactas y objetivos A/B pendientes de definición. No iniciar integración en salas de otra sesión.

Fuentes técnicas primarias: https://github.com/Perfare/AssetStudio/blob/master/README.md ; https://github.com/Perfare/AssetStudio/blob/master/AssetStudioGUI/Exporter.cs ; https://www.gildor.org/projects/umodel/readme .
