
> Actualizacion 11/10/2026: reemplazada la conducta de grupo por agendas independientes y corregido OOM/bando. Ver GIRAN-SIEGE-ESCUADRONES-V2.md; las ordenes de movimiento V1 descritas abajo son historicas.
# Giran: prueba de asedio — 10/10/2026

Abrir `.giran` (tambien `.siegegiran`) con Hellkevin GM, lider de Hellsing. No requiere cliente modificado. Preparacion gratuita del laboratorio. Castillos restantes y combates `.arena`, `.ia`, `.agite` conservan su modulo; no pueden usar simultaneamente los mismos pilotos.

## Equipos

Todos atacantes, cuatro miembros por escuadron: Hellkevin y los diecinueve perfiles Player reales reservados del laboratorio, nivel80, main y tres subclases, equipo +4 y habilidades existentes.

| Clan | Lider | Otros integrantes |
|---|---|---|
| Hellsing | Hellkevin | Vaelkor, Noctis, Selene |
| Holly | Kaelis | Gorvak, Myrentha, Ignara |
| Sacred | Caelan | Arden, Zhurak, Morvain |
| Fury | Riven | Eryndor, Korvash, Aelira |
| Waves | Brunna | Lethiel, Sylira, Velith |

Fury y Waves creados a nivel5, cada uno con alianza propia del mismo nombre y crest de clan/alianza tomada de los originales crest-ally-fury.bmp y crest-ally-waves.jpg. DDS DXT1 con clan16x16/alianza8x16, doce filas visibles y cuatro de relleno. No vuelve el error de dimensiones12 no potencia de2. Los tres clanes anteriores conservan nivel, lider, alianza, emblemas, reputacion y skills. No se entregaron nuevas skills de clan/hero.

## Prueba

1. Esperar roster19/19; finalizar otros eventos, salir de party y combate. Desactivar invulnerabilidad GM. El castillo debe continuar sin propietario y sin otro siege activo.
2. `.giran` → Reunir escuadrones: crea cinco parties nativas, lleva a todos al campamento frente a Giran, prepara buffs/consumibles de los pilotos. No inicia el asedio; hay diez minutos para comenzar.
3. Iniciar siege: activa el motor nativo, puertas, tres torres de control, dos de fuego y guardias. Duracion120min. Aparecen Ares y Nyx una sola vez, dentro del castillo.
4. Seguir y asistir: los diecinueve siguen a Hellkevin y asisten su target de guardia, boss, torre o puerta. Asalto automatico: seleccionan esos blancos cercanos dentro de1600unidades; sin blanco siguen al jugador. Avanzar por las puertas con el grupo; no hay teletransporte a traves de puertas ni ruta estrategica de asedio automatica.
5. Retirada devuelve pilotos al campamento. Finalizar detiene el siege iniciado por este panel, desinvoca summons de los pilotos, desmonta parties, retira bosses y devuelve personajes a su posicion original. Cancelar antes de iniciar solo retira la preparacion.

Los pilotos usan skills/items y daño nativos, asistencia/heal/resurreccion por party, summons, shots y potas; no atacan players, mascotas, comerciantes ni el artefacto. El autoataque fisico mantiene la intencion del motor. Los muertos aceptan resurreccion; en esta prueba vuelven al campamento tras30s si nadie los resucita. Hellkevin conserva muerte/resurreccion normales. Los buffs de pilotos se reinician para la prueba y sus consumibles pueden consumirse normalmente; no se reemplazan equipo, main ni subclases.

La conquista la decide el motor: Hellkevin como lider usa Seal of Ruler (246) sobre el artefacto, a menos200unidades y altura valida. Los otros lideres tienen la skill nativa pero la IA no captura automaticamente. Giran inicial NPC; si se conquista se conserva propietario y resultado. Finalizar no borra una conquista, ni restablece silenciosamente el castillo a NPC. El fin nativo limpia inscripciones y reprograma fecha; si no hubo conquista Reunir/Registrar vuelve a inscribir cinco clanes. Si hubo conquista se necesita preparar expresamente otra modalidad antes de repetir.

## Defensores

382 posiciones nativas de guardias configuradas para Giran (no son382 bosses). Ares903200 y Nyx903201 son copias aisladas de los benchmarks900200/900201, sin modificar los originales del Coliseo. Conservan stats, skills, apariencia y combate base del motor. HP18000/16000 respectivamente; EXP/SP0 y sin drops, respawn desactivado. IA especial, fases, decisiones de defensa y balance para veinte atacantes quedan pendientes, tal como solicito Kevin.

Se instalo geodata23_22 de Giran: faltaba en el servidor. Parser nativo valida los65536bloques, veinte campamentos y dos posiciones de bosses con piso y NSWE transitables. Nyx se posiciona en117700,145150 con piso-2640; el ancla anterior estaba bloqueada y se corrigio antes de la prueba. Fuente fija: https://raw.githubusercontent.com/naustagic/L2JOrion_Interlude/98e351766c569504210a24d96a9f39262f19b397/L2jOrion_Geodata/geodata/23_22.l2j ; SHA256 aedaa9a4e2bc1b82957ca5610109c550930ecdf18bcb80f1f1064aeb26b1fa46,4412705bytes. Core GeoEngine sin modificaciones; regiones anteriores21_19/24_19 conservadas. El servidor carga tres regiones.

## Verificacion y continuidad

368 checks PASS: clanes persistidos y recargados, miembros reservados/main/subs, parties nativas, registros atacantes DB/cache, puertas/zona/artefacto, campamentos con altura geodata, DDS validos y templates aislados. El verificador no cargo a Hellkevin, no inicio el asedio ni cambio propietario. Combate completo, recorrido de puertas y balance todavia requieren la prueba ingame.

Snapshots antes/despues: clanes originales/skills/castillo/382guardias identicos; entre todos los personajes solo cambio clanid de los ocho nuevos miembros. Los perfiles continúan offline al terminar la comprobacion. Hash del core y archivos del cliente conservados. Solo scripts/4DDS/XML nuevos; GameServer reiniciado, LoginServer conservado.

Fuentes research/giran-siege y server/game/data/scripts/custom/GiranSiegeLab. XML server/game/data/stats/npcs/custom/giran_lab_guardians.xml. Backup backups/giran-siege-2026-10-10. Fuentes, assets, documentos y continuidad32 copiados a source/dist y cloud-repo, sin commit/push. Instalacion de clanes opt-in -Dlab.giran.install=true, NO repetir: los clanes ya existen. Verificacion opt-in -Dlab.giran.verify=true one-shot terminada; arranque normal no instala ni inicia asedio.
