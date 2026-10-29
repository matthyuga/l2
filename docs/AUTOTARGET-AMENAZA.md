# Autotarget de amenaza — 2026-10-12

Implementado y activo en el GameServer local.

## Uso

Escribir `.amenaza macro` una vez en el chat general. Crea un macro nativo llamado
**Amenaza**, con una única línea `//amenaza` para GM (`.amenaza` para usuarios
normales). Abrir **Alt+R** y arrastrarlo a la
barra de acciones. Repetir la orden no duplica el macro ni sobrescribe otros.
Si hay 24 macros, primero se debe liberar un espacio.

También se puede escribir `.amenaza` o `.agresor` directamente en el chat general.
Para GM, `//amenaza` evita pasar por el chat ordinario al repetir el macro.
Cada pulsación selecciona al responsable del último golpe directo recibido durante
los últimos 30 segundos. No inicia ataques ni cambia el objetivo al recibir daño.

## Reglas

- Autoataque directo: cuenta si produce daño aceptado, incluso absorbido por CP.
- Hydro Blast: cuenta para su objetivo original, aunque el atacante cambie después de target.
- Aqua Splash y otras áreas dirigidas: cuentan solamente para su objetivo principal.
- Salpicaduras, golpes secundarios de lanza, auras y áreas sin objetivo individual: no cuentan.
- Daño periódico, autocostes, daño reflejado y daño transferido a terceros: no cuentan.
- Invocaciones y mascotas: se recuerda a su dueño. Un bot Player/NPC se recuerda a sí mismo.
- El comando exige responsable vivo, aparecido, seleccionable, visible, en la misma
  instancia, dentro de regiones circundantes y a menos de 2000 unidades con línea de visión.
- Respeta bloqueo de target y estados que impiden seleccionar. Si falla, conserva
  el objetivo actual; no retrocede a agresores anteriores.
- El registro no se guarda en base de datos y se limpia al morir o salir del mundo.

## Implementación

`MagicUseTask` conserva el objetivo principal capturado al comenzar el lanzamiento.
`HitTask` distingue el golpe principal de los golpes secundarios de lanza; los dos
golpes de un arma dual siguen siendo directos. Un contexto temporal por hilo acota
la aplicación del daño y se retira en `finally` mediante `AutoCloseable`.
`PlayerStatus` registra el agresor después de los rechazos de invulnerabilidad,
permisos de daño y duelo, antes de absorciones por CP/MP/servitor. El registro
compara identidades de atacante y víctima, excluyendo reflejos y transferencias.

`DirectThreat` mantiene una entrada transitoria por Player con referencia débil al
responsable y reloj monotónico. `ThreatCommand` se registra en `MasterHandler`.
No cambia el protocolo ni requiere parches del cliente. Daños de scripts propios
que llamen directamente a `reduceHp` sin una acción nativa no se consideran ataques
directos: necesitarían integrar explícitamente el contexto de objetivo original.

## Validación y despliegue

- Compilación Java 25 de las seis clases de núcleo y del comando: correcta.
- Servidor reiniciado sin clientes conectados; comandos registrados y operativos.
- **26 comprobaciones PASS**, con personajes temporales en una instancia privada.
  Incluyen daño real, casteo programado de Hydro Blast con cambio de selección,
  Aqua Splash con lista de afectados reordenada, summon, exclusiones, caducidad,
  visibilidad/distancia/instancia/muerte y creación idempotente del macro.
- Resultado: `reports/direct-threat-2026-10-12/verification.txt`.
- Arnés: `tools-src/DirectThreatVerification.java` y `tools-src/verify-direct-threat.ps1`.
- Backup de JAR, fuentes y scripts: `backups/direct-threat-2026-10-12/`.
- JAR actualizado solamente con las clases compiladas del núcleo; los scripts se
  conservan en `server/game/data/scripts` y `source/.../dist/game/data/scripts`.
- Fuentes espejadas en `cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude`.

La comprobación inicial del arnés medía solamente HP y se corrigió para incluir CP;
la ejecución final completa es la que figura como SUCCESS en el reporte.

Actualización posterior: ver `REPARACION-NPC-Y-MACROS-2026-10-12.md` para la
reparación de diálogos con Seven Signs desactivado y los macros GM sin chat normal.
