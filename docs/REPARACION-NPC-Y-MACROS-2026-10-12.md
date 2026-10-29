# Reparación de NPC y macros — 2026-10-12

## Resultado activo

- Thiago (50008, SchemeBuffer) y Mirellas (50010, Merchant) vuelven a abrir diálogos.
- Macros de amenaza de Hellkevin corregidos conservando IDs, nombres e iconos:
  `autotarget`, `Amenaza` y `Amenaza2` ahora ejecutan `//amenaza`.
- Macros **IA Mago** y **IA Fisico** creados en Alt+R, con `//ia mago` y `//ia fisico`.
- Aplicado en caliente sin desconectar al jugador ni reiniciar el combate.

## Causas y alcance

El perfil `CustomWorldOnly=True` salía del constructor de SevenSigns antes de
inicializar propietarios/proporciones de sellos. El diálogo base de cualquier NPC
consulta esos propietarios; desempaquetar un Integer inexistente lanzaba un NPE.
La corrección inicializa los tres sellos en estado neutral y hace que las consultas
devuelvan valores neutrales cuando no hay entrada. No reactiva eventos, spawns ni
planificaciones clásicas. La sustitución en caliente de las consultas también sirve
para el singleton actual, cuyos mapas ya estaban vacíos.

En el diagnóstico Hellkevin tenía `chatBanned=false` y los controladores `.ia` y
`.amenaza` estaban registrados. Por tanto no se retiró ningún castigo del servidor.
El aviso mostrado por el cliente es compatible con su límite de chat al repetir
macros, pero no se verificó internamente ese contador del cliente.

Además dos macros contenían `.amenaza macro`, que es la orden de CREACIÓN, no la
acción de seleccionar. Se migraron las tres variantes de amenaza existentes.
Las nuevas versiones GM utilizan el canal nativo de administración (`//...`),
evitando mensajes ordinarios de chat por pulsación. `.amenaza`/`.agresor` y `.ia`
siguen disponibles; las funciones y permisos de sus controladores se conservan.
`//ia macros` permite instalar los dos macros IA de nuevo sin duplicarlos.

Los aliases `admin_amenaza` y `admin_ia` están registrados con acceso 100.
No conceden privilegios a usuarios normales. El creador `.amenaza macro` ahora
genera `//amenaza` para GM y `.amenaza` para usuarios normales.

## Verificación

`reports/lab-service-repair-2026-10-12/diagnostic.txt`: datos previos, mapas vacíos,
macros originales y ausencia de bloqueo de chat en servidor.

`reports/lab-service-repair-2026-10-12/repair.txt`: SUCCESS; consultas neutrales de
los tres sellos, diálogos de ambos NPC sin excepciones, aliases registrados,
permisos de Hellkevin, migración y creación de macros, cliente aún conectado.
Los diálogos se probaron con un Player temporal sin guardar personajes ni realizar
compras. No se modificaron estadísticas, equipo, buffs ni sesiones IA del usuario.

## Persistencia

Fuentes y scripts actualizados en source, server y el overlay del proyecto;
`MasterHandler` registra los nuevos aliases y `AdminCommands.xml` sus permisos.

Windows mantiene bloqueado `server/libs/GameServer.jar` mientras está ejecutándose.
La reparación ya está en memoria. Para persistirla en el próximo arranque normal,
la clase SevenSigns corregida queda en:

`server/pending-core-patches/20261012-lab-service-repair/org/.../SevenSigns.class`.

`Start-L2Local.ps1` aplica las clases pendientes exclusivamente antes de iniciar
un GameServer nuevo, después de comprobar que no existe uno ya arrancando; añade
una marca `.applied` cuando termina correctamente. No reemplaza clases ajenas.
Sintaxis del lanzador validada y aplicación del parche comprobada sobre una copia
del JAR. No hace falta reiniciar ahora.

Backup: `backups/lab-service-repair-2026-10-12/`.
