# HUD y dano recibido de Riven / Noctis

2026-10-09. Funciona en pruebas manuales `.ia`, no altera stats ni formulas.

Al seleccionar el Player piloto, se envia el mismo panel nativo CP/HP de
Olimpiadas que ya usaban los NPC fakePlayers. HP/CP se actualizan cada500ms.
Efectos activos no pasivos se envian cada segundo con ExOlympiadSpelledInfo.
Al perder target/terminar se cierra; si se cambia a NPC fakePlayer se restaura
su HUD previo. No cambia flags reales de Olimpiadas ni invulnerabilidad.

`.ia efectos` abre una lista HTML actual de buffs y debuffs del piloto,
con nombre/nivel/tiempo, rojo debuffs y azul buffs. Max36 filas, renovar con
el comando. No es historial de resistencias. Solo operador de prueba activa.
Alt+F no se pudo confirmar en User.ini: no se modifica ningun atajo.
La vista de iconos depende de que la interfaz instalada dibuje ese paquete.

Dano del piloto o su summon al operador: mensajes2204..2207 con dos
parametros (atacante y cantidad). Fisico naranja, critico rojo, magico rosa,
critico magico rosa intenso. Chat: `[ENEMIGO] nombre: recibes cantidad...`;
numero en pantalla `-cantidad`, misma zona nativa que dano saliente.
No son numeros anclados al modelo3D del atacante. El valor es el impacto del
evento de dano del motor, no una medicion aislada de HP perdido: puede
repartirse entre CP/HP/TransferPain. No se muestra dano propio de ArcanePower.
No se sustituyen mensajes estandar, asi que puede haber tambien linea nativa.
No se anaden colores arbitrarios a texto del servidor: usa registros cliente.

Cliente cambiado SOLO E:\l2\system-hud\systemmsg-e.dat. Registro original
2087 ->2091; los originales2200..2203 y restantes se conservan byte a byte.
Respaldo, decodificado y roundtrip cifrado verificado en
E:\l2-local\backups\pilot-hud-damage-2026-10-09.
Herramienta reproducible tools\Patch-PilotIncomingDamage.ps1 sobre datos
decodificados, rechaza IDs duplicados, conserva SafePackage.

No se implementa sombreado negro individual: el formato inspeccionado no
confirma un campo de sombra por mensaje. No se cambia fondo global del chat
ni Interface.u. Para sombreado real hace falta estudiar esa interfaz aparte.

Java compila, PASS4 formatos wire del paquete, cifrado413 roundtrip PASS.
Pendiente revision visual en cliente: barra CP/HP, iconos y numeros/colores.
Si no aparecen iconos, usar `.ia efectos` como alternativa comprobable.

Arranque final confirmado: AI_SMOKE SUCCESS10/10 y roster19/19+copias7/7PASS
despues de limpiar efectos temporales de la autoprueba. No valida el render
del HUD sin un cliente conectado: queda comprobacion visual del usuario.
