# Dust2 — cobertura de cámara V9, 14/10/2026

V8 quedó instalada a las17:23. Kevin respondió «faltan algunas zonas» y dejó al personaje en una zona donde la cámara se aleja y muestra desperfectos. Posiciones leídas del servidor:142414,56349,8000 a las17:26:40; después142557,54506,8088. Capturas reales Shot00082..85 de system-hud muestran vistas altas de paredes/contornos expuestos. PNG de inspección en ../dust2-camera-v8/qa. No confundir mejoría parcial con contención completa.

Hallazgo: el filtro de V8 dejó228 rectángulos completos de techo sin bloqueo de barridos porque una parte interfería con otra capa caminable. Por ejemplo, CameraCeil0486 cubre X142288..142544,Y56336..56352,Z8086, pero solo tres celdas en su extremo oeste causaron la exclusión de toda la pieza. La primera posición de Kevin estaba debajo de su parte libre. La posición posterior sí tenía una pequeña pieza habilitada directamente encima; los huecos vecinos siguen permitiendo escapar con cámara oblicua. No atribuir todos los defectos a una sola pieza.

V9 recupera4621 celdas de techo omitidas, agrupadas en462 piezas pequeñas.3721 mantienen su altura.900 se elevan lo necesario para salir de una envolvente conservadora de personaje de9u de radio y88u sobre el suelo visual en las capas vecinas. La búsqueda de obstáculos incluye celdas vecinas completas, con margen25u respecto a centros, no solo el centro de la celda del techo. Elevación máxima216u; puede permitir más alejamiento en lugares con niveles superpuestos.

Se añaden2101 uniones cortas entre alturas de techo. Se restan tramos ya cubiertos por uniones V8 y los que invadirían el paso del personaje:206 uniones tuvieron recorte de espacio corporal. Por ello no prometer un cerramiento topológico hermético en toda orientación o en todo el mapa. Son2563 nuevos actores ocultos deco01.Box02, sin nueva malla, AI ni textura. Carga/trazas del cliente aún deben observarse. Los payloads anteriores se conservan byte por byte salvo la lista de actores de myLevel. Rampas, geodata, escala, mapa visible, comandos y user.ini intactos.

Preparación: prepare.py lee el mapa V8 vivo con guardia SHA y split-proposal.json de V8 (propuesta almacenada de las4621 celdas). Reagrupa las nuevas piezas, audita su separación corporal, conserva exportaciones antiguas y verifica cifrado Ver121+CRC. No ejecutar sobre V9 instalada. verification.json y bounds-audit.json contienen el resultado.

check_rays.py compara geometría de cajas de techo/uniones y paredes físicas V4, con barrido(0.1,0.1,5), desde suelo+50. Prueba72 orientaciones horizontales y5 inclinaciones ascendentes(15,30,45,60,85grados),360 direcciones por punto. Resultado en latest_user:67 direcciones sin límite a1800u en V8,0 en V9. previous_user:151->0. CT y escalera2 permanecen0->0. Distancia máxima de primer contacto en los puntos del usuario589u y491u. Es una comprobación geométrica con cajas alineadas; no ejecuta la función nativa de cámara ni verifica la apariencia de todos los bordes, ni las inclinaciones inferiores al horizonte. No declarar validación del cliente basándose en ella.

Instalador install.py: exige L2 cerrado, hashes de origen/candidato y8 manifiestos anteriores, backup y actualización de hashes. No requiere reiniciar GameServer. Pendiente cierre de L2 solicitado mediante async y prueba visual posterior en la posición que dejó Kevin. No modificar permisos, DLL ni controles globales de cámara.

La escalera larga está confirmada por Kevin en V7; el critical de salida sigue sin causa determinada.


Instalada tras cierre confirmado por Kevin: backup `E:/l2-local/backups/dust2-camera-v9-20261014-173421`. Los nueve manifiestos coinciden con los archivos vivos. Sin reinicio del servidor. Pendiente comparaci?n visual en el cliente.
