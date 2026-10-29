# Giran: escuadrones y correccion de bloqueo — 11/10/2026

`.giran` → Reunir escuadrones → Iniciar siege. El modo inicial ahora es Objetivos por escuadron. Hellsing escolta a Hellkevin; los otros cuatro clanes avanzan con capitan, blanco, progreso y ruta propios. Reagrupar conmigo vuelve a la escolta; Retirada y Finalizar conservan su funcion. El panel muestra la tarea actual de cada clan. Los pilotos no castean conquista.

| Escuadron | Agenda |
|---|---|
| Hellsing | Escolta, proteccion y asistencia del conquistador |
| Holly | Puerta exterior norte, cristal de entrada, puerta interior norte, torre de fuego oriental |
| Sacred | Puerta exterior sur, guardias del patio sur, puerta interior sur, cristal oriental |
| Fury | Puerta exterior norte, Ares, puerta interior norte, cristal central |
| Waves | Puerta exterior sur, guardias del patio norte, puerta interior sur, torre de fuego norte, Nyx |

Al terminar su agenda, cada clan protege al conquistador. Comparten los cuellos de botella cuando hace falta romper las mismas puertas, pero conservan objetivos propios. Los integrantes siguen a su capitan, se reagrupan si quedan lejos, atienden amenazas cercanas y mantienen autoataque nativo. Cadencias de decision 750–1300 ms y salida escalonada 1,6 s por clan; no se teletransportan atravesando puertas. Reintento de movimiento si estan detenidos 12 s. Los objetivos eliminados por otro escuadron tambien se dan por completados.

## Bloqueo y bando

El GameServer agoto sus 2 GB de heap: OutOfMemoryError en IA/red/schedulers. La reserva ThreadLocal de caminos retenia 468 NodeBuffer y unos 900 MB de arrays. Se reemplazo por una reserva global exclusiva, sin espera bloqueante, limitada por los conteos configurados: 32 buffers, 68.513.792 bytes de arrays como maximo. Si estan ocupados, la solicitud devuelve null para el reintento nativo, sin retener un buffer por hilo. El algoritmo A* y geodata se conservan. Jar: solo cambiaron PathFinding.class, su SingletonHolder y ClanMember.class para reconocer pilotos activos sin socket; todas las otras entradas, incluidos parches anteriores, son identicas.

Start-L2Local.ps1 usa 4 GB de heap en esta PC de 32 GB. Ajusta automaticamente 2/3/4 GB segun memoria fisica y permite -GameHeapMb; LoginServer se conserva. No basta con subir memoria: el pool acotado corrige la retencion.

Los pilotos ahora enlazan ClanMember.setPlayer al cargar. ClanMember.isOnline reconoce Player.isLabControlled cuando esta activo sin socket: antes, el chequeo de offline shop excluia a todos los pilotos aunque el enlace estuviera presente. El motor nativo les asigna estado atacante y lado Giran; antes faltaba ese enlace/reconocimiento y Amber llego a considerar enemigo a Riven. No se modifico Amber: ahora su comprobacion nativa isSiegeFriend reconoce a los atacantes aliados. Experiencia/nivel del piloto reservado se conservan durante la prueba y al limpiar. Se recuperaron seis perfiles que habian bajado a 79 por muertes de este asedio: Myrentha, Noctis, Ignara, Aelira, Arden y Selene. Hellkevin no se cargo ni se modifico.

## Conquista manual

No requiere item. Seal of Ruler (246, nivel 1) consume 50 MP y tarda 180.000 ms: tres minutos fijos, sin reduccion por casting speed. Solo el lider de un clan atacante inscrito, durante el siege, sobre el artefacto correcto y a su altura. La comprobacion de conquista admite hasta 200 unidades/45 de diferencia vertical; el alcance de casteo de la skill es 85, por lo que hay que acercarse al pedestal. Mantener el casteo sin interrupcion. Los 300 Gemstone C (2131) corresponden a Build Headquarters (247), no a Seal of Ruler. Fuente local: server/game/data/stats/skills/00200-00299.xml y condiciones nativas de conquista.

## Validacion

Pool: 128 hilos, 25.600 solicitudes, arrendamiento exclusivo, limite 32 buffers y menos de 80 MiB en arrays; PASS. Prueba nativa opt-in de 85 segundos: 619 checks, 19 Players reservados en cinco parties, amistad entre todos los pares de atacantes, objetivos reales atacables, artefacto excluido, 17 pilotos desplazados y 94 defensores/puertas con perdida real de HP. Para verificar avance sin esperar romper puertas, la prueba abrio solo las puertas exteriores a los 35 s y dio invulnerabilidad temporal a los pilotos. No mide balance ni una conquista completa; esos quedan para la prueba de Kevin.

Limpieza nativa terminada: 19 pilotos offline nivel 80, bosses retirados, parties desarmadas, lock liberado. Snapshots: Hellkevin completo e inventario, cinco clanes/skills, castillo/fecha/inscripciones y 382 guardias configurados identicos. Propietario Giran NPC. Full run de castillo, rutas interiores bajo combate y balance requieren prueba ingame. IA especial de Ares/Nyx sigue pendiente; conservan combate base.

Fuentes/pruebas: research/giran-siege-v2. Backup: backups/giran-siege-v2-2026-10-11 (OOM/histograma/Jar/scripts anteriores/snapshots/proof). Continuidad 33 en W10/W11 y Nexus. Source/dist/cloud overlay sincronizados, sin commit/push. No repetir instalador V1 ni lab.giran.install=true: clanes ya creados. Verificador V2 opt-in -VerifyGiranAgenda; arranque normal no inicia siege ni prueba automatica.
