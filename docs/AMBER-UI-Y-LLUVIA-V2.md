# Amber y habilidades: accesos visibles y lluvia con potencia propia

2026-10-10. Usar el cliente habitual **2-JUGAR**.

## Uso

En **Alt+K**, debajo de la rejilla, hay botones **Principal, Sub 1, Sub 2, Sub 3, Comunes, Amber y Todas**. Cada filtro muestra sus iconos en las pestañas nativas de activas y pasivas; se pueden arrastrar a la barra. El botón **Nombres de clases / índice** conserva la página con los nombres reales de main/subclases y los detalles de origen. «Todas» vuelve a reunirlos, ordenados por grupos.

El botón cuadrado **IA**, con marco dorado y fondo rojo, está tanto en Alt+K como debajo de las acciones de la ventana del summon. Al pulsarlo enciende/apaga **Asistencia de Amber**. El mismo icono identifica la habilidad 19014 dentro del filtro Amber y se puede arrastrar a la barra. Al encender se ve su icono de efecto en los buffs del amo y el mensaje «asistencia IA activada». Al apagar se retira el efecto. El contrato debe estar vigente y Amber invocada; la invocación sigue empezando manual. Seguir/Detener apagan la asistencia.

Los botones directos de clase no abren otro diálogo: filtran la rejilla actual. No conceden skills ni cambian clase o estadísticas. El acceso IA del summon es un control adicional de la misma habilidad del amo; no existe un segundo controlador independiente.

## Lo encontrado en la pelea contra Noctis

El registro no contenía activación de IA de Hellkevin. Amber esperó las órdenes manuales; no era una prueba de la asistencia encendida. La lluvia tuvo tres impactos por 203,86 de daño previo a la distribución nativa. En esa pelea Noctis solicitó Ultimate Defense, y hubo un impacto de un punto por bloqueo perfecto. Su HP también aumentó entre impactos, por lo que las recuperaciones del rival ocultaban parte del efecto en la barra. Run manual30; evidencia en backups/amber-ui-rain-2026-10-10/user-fight-before.log y lab_combat_events/lab_ai_actions.

## Lluvia

Ahora cada impacto usa la fórmula nativa de habilidad física y **potencia3000**, sumada al PAtk con soulshot de Amber. Potencia es un parámetro de la fórmula, no daño garantizado. Mantiene tres impactos, radio200, carga3,5s, 120MP, tres Beast Soulshots y recarga45s. Captura PAtk y elemento al comenzar; el fuego sigue aportando su mejora aunque expire durante la carga. La estimación de la IA considera esa potencia al valorar áreas.

Se conservan PDef, mitigación física de skills, UD, escudo y resistencias. Un bloqueo perfecto sigue siendo exactamente un punto; no se multiplica por el snapshot de fuego. No cambia el daño del arco básico ni las estadísticas del amo.

Al acabar informa los impactos y pérdidas observadas de **CP y HP**. El log mantiene además el daño calculado, que puede diferir de la pérdida del jugador por Transfer Pain, absorciones y recuperaciones concurrentes. La captura inmediata de barras es una observación, no una predicción del estado final tras curas posteriores.

## Archivos y validación

Cliente: sólo Interface.xdat, Interface.u, skillgrp.dat y skillname-e.dat; nuevo paquete aislado AmberAssistIconsV1.utx. Las ventanas ajenas, los exports previos no relacionados y las filas de otros skills se comparan byte a byte. Los efectos V10 y los iconos anteriores de Amber quedan intactos. El nuevo icono se exportó del paquete y sus1024 píxeles/orientación coinciden con el original generado por código.

Servidor: AmberContract/AmberAssist/AmberContractVerification, SkillCatalog y amber_contract.xml. No se modifica GameServer.jar, RequestActionUse, equipo, stats, cámara ni los pilotos reales. El botón usa bypass de voz existente y el ciclo nativo del activable. Los callbacks se recargan desde el paquete construido y se verifican parámetros, comparaciones de nombres y saltos VM.

Backup: backups/amber-ui-rain-2026-10-10/. Fuentes y XML espejados en source/dist y cloud overlay. Prueba opt-in: lab.amber.verify=true, lab.amber.protection.only=true y lab.amber.ui.rain=true. Usa personajes reservados en una instancia privada y limpia los efectos, summons y reservas de HP al terminar. La reacción defensiva se ensaya con daño mágico nativo real para evitar depender de que un autoataque del probe acierte.

Los archivos del cliente y las comprobaciones del servidor permiten verificar la instalación; la apariencia y los clics reales de la interfaz todavía requieren revisión del usuario en L2.

Resultado final: **66 comprobaciones PASS** con da�o m�gico nativo real, reacci�n/TP/curanderos, acceso IA ON/OFF, filtros sin mutaci�n de clase, potencia de lluvia, UD, bloqueo perfecto, tres impactos reales, consumo de recursos y p�rdidas de CP/HP. Compilaci�n Java y verificaci�n de paquetes/DAT/texture correctas.

Correccion posterior al primer arranque: el cliente rechazo AmberAssistIconsV1.utx porque se habia instalado el paquete UCC sin envoltorio. Se instalo Lineage2Ver121 con clave dependiente del nombre exacto, CRC32 comprobado y descifrado identico a los 4849 bytes originales. Solo cambia ese UTX; interfaz, DAT y servidor conservados. Las 66 pruebas anteriores validaban el servidor, no la carga real del cliente. Pendiente nueva apertura de L2 y prueba visual del usuario.
