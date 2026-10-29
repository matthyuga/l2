# Estado de la prueba — 15/10/2026

## Resultado realizado
Se extrajeron tres movimientos corporales de Chara Studio RX22 con UnityPy, jerarquía/rest local580nodos y curvas evaluadas. Fuente/catalogo/validación en studio/README.md. REA identificó ensamblado Unity/Mono previamente (evidencia ev_57aeb5f6ff6b394d25f0c523e243d85ccc7b6098e4ca83418acea5123ec61dc4).

Se adaptó postura agachada y combinó con movimiento de manos de otro clip para una humana Fighter76huesos. Blender3.5.1, mallas nativas sin texturas para QA. Se corrigió orientación izquierda/derecha y transferencia por dirección anatómica tras detectar deformación en primer render. Se ajustó apoyo vertical contra botas evaluadas. Borrador artístico: manos aún necesitan alinearse al objeto bomba, dedos, entrada/salida y continuidad de bucle. Sin IK runtime de Studio. Solo un cuerpo.

- Vista animada: retarget/Dust2-BombWork-preview.gif
- Blender: retarget/Dust2_BombWork_FFighter-QA.blend
- Movimiento: retarget/Dust2_BombWork_FFighter.psa
- Paquete nuevo: native/Dust2BombWork.ukx
- Pruebas: native/bombwork-validation.json, social-roundtrip-validation.json.

Escritor nativo nuevo resuelve serialización TRoughArray y secuencias de Lineage2: UModel acepta UKX y exporta todos151frames/76huesos con error máximo0.0 en posiciones y cuaterniones respecto PSA. No equivale a aceptación/reproducción en cliente real.

## Cliente de laboratorio
ABRIR-PRUEBA-ANIMACION.cmd abre copia independiente de system-hud en client-lab/system. El l2.ini usa cifrado413 y rutas originales absolutas, con override de animaciones SOLO en client-lab/animations. No modificar original.

Fighter.ukx aislado cambia únicamente Social_bow_FFighter para facilitar prueba con acción Reverencia de humana Fighter mujer.112secuencias restantes y796exports preservados byte por byte. Original Fighter SHA8a22d41ceaa78d52a10b856b923462eb8eb08d61b203d0d7904e464857ae988c. Reemplazo fca90fac4df83e0bcc2af47f74b83cf64edd6625f3670f4230dbeeafaafcc892. Guardas en launcher evitan correr con original cambiado o cliente abierto.

El primer arranque con INI111 mostró Files are corrupted!! Please, full check; usuario aportó captura. Se cambió INI a413. Siguiente Start-Process devolvió cancelación de operación. Aún NO se comprobó que413 resuelva ese aviso. Usuario luego abrió cliente habitual E:/l2/system-hud/L2.exe (confirmado sky.list_windows), no la copia de laboratorio. No cerrar ni matar ese cliente por fuerza.

## Próxima prueba concreta
1. Salir limpiamente del cliente habitual.
2. Ejecutar ABRIR-PRUEBA-ANIMACION.cmd.
3. Si arranca, entrar con humana Fighter mujer y pulsar Reverencia en acciones. No alterar raza/personaje del usuario automáticamente. Personaje temporal de prueba preferible.
4. Confirmar secuencia completa, suelo, deformaciones, reanudación de reposo. Otros observadores requieren mismos recursos.
5. Si persiste full check, investigar paquete/config de laboratorio comparando baseline, sin parches de integridad nuevos ni tocar perfil habitual.

## Aún no implementado
No hay bomba, CT/T, objetivos A/B, kit, casteos ni reglas de interrupción. La fase actual es validación técnica de animación. Integración por skill nueva pendiente: skillgrp animation observado usa selectores cortos; no está demostrado que acepte nombres arbitrarios. Engine expone LinkSkelAnim/PlayAnim, pero SkillAction nativas inspeccionadas son efectos/trails. No inventar SkillAction_PlayAnimation.

La otra sesión controla salas PvP; no tocar su runtime/core/scripts/DB. Este trabajo solo crea archivos de investigación y cliente separado. No commit/push.

## NPC solicitado por usuario
15/10/2026: creado maniquí completo Fighter mujer con material azul y secuencia wait_Hand de151frames; display59080 añadido SOLO al lab. NPC privado902680 via agente temporal enGS25176, espera Hellkevin10min, aparece al lado/sameinstance, desaparece20min. Sin DB/core/scripts sala/cliente habitual. Leer npc/README.md y npc/npc-runtime.txt antes de retomar o reejecutar. Usuario cerró lab para instalar y se está reabriendo. Render real pendiente.
