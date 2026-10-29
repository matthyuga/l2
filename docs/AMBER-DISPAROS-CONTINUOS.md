# Amber: disparos continuos

10/10/2026. Cambio solicitado después del diagnóstico de cadencia.

Amber encadena los disparos automáticos al completar la preparación de cada flecha. Se elimina la recarga adicional de su actor, que antes añadía aproximadamente 1,21 segundos de espera al ciclo observado de 2,51 segundos. La preparación sigue dependiendo de su Atk. Spd.; en la prueba anterior equivalía aproximadamente a 1,30 segundos. El resultado exacto se comprueba con lanzamientos reales en la prueba opt-in.

Manual e IA comparten un límite por disparo. Repetir la orden Atacar o cambiar de blanco no adelanta la siguiente flecha antes de completar la preparación. Se conserva el ataque nativo: daño, críticos, fallos, soulshots, selección de objetivos, controles y reglas PvP. El cambio aumenta la cadencia sostenida respecto de la versión previa; no altera el daño individual.

La lluvia mantiene su carga de 3,5 segundos y bloquea el arco mientras carga. Las órdenes Seguir/Detener siguen interrumpiendo la asistencia. La IA debe activarse tras invocar; la invocación empieza manual.

Producción: sólo AmberServitor.java. Verificación: AmberContractVerification.java, bandera `lab.amber.cadence=true`, combinada con protección y UI/lluvia. La prueba usa los tres personajes reservados de Amber en una instancia privada, registra lanzamientos y daño nativo real, compara cinco disparos automáticos con cinco manuales bajo órdenes repetidas, y comprueba bloqueo durante carga y parada efectiva. No mantiene el monitor de la sesión durante las esperas de los temporizadores.

Fuentes copiadas con guardas de concurrencia a source/dist y cloud overlay. Backup: `backups/amber-cadence-2026-10-10`. Cliente y GameServer.jar conservados.


Resultado: **76 comprobaciones PASS**. Preparacion medida 1298 ms; media IA 1299,03 ms, manual con ordenes repetidas 1299,28 ms. Cinco disparos por modo y diez impactos nativos con dano real. Cliente y core sin cambios, fuentes espejadas. Arranque final en modo normal.
