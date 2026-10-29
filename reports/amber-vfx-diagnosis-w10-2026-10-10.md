# Amber: diagnóstico visual comunicado por el usuario — 10/10/2026

Usuario: ve flechas ascendentes, pero no caída sobre la zona; no ve fuego al activar el buff; ve una explosión en el enemigo y no la carga en el arco. Pendiente aclarar si la observación corresponde a W11 o a una nueva ejecución en W10. No se inició L2 ni se instalaron parches durante este diagnóstico.

Hallazgos leyendo scripts y deserializando paquetes/catálogos:

- Las filas instaladas 19002 (orden de fuego) y 19005 (buff real) tienen description vacío. Aplicar fuego modifica stats y duración, pero no enlaza una animación de activación ni un aura persistente. FireShot (19009) es un efecto por ataque, distinto de encender el buff.
- BeastSoulShot envía 19013 con Amber como actor y destino; el efecto apunta a Weapon_L_Bone con AttachOn=3. Por tanto el handler no envía la carga al enemigo. Esto no certifica que el cliente resuelva correctamente ese enganche.
- Attack transmite una bandera soulshot por hit. La explosión observada al impactar puede ser el efecto nativo del golpe cargado. No eliminarla ni declararla carga mal dirigida sin distinguir temporalmente carga e impacto.
- Rain/FireRain son efectos separados de SkyVolley. El servidor captura x/y/z del objetivo al comenzar, mantiene un área circular fija de radio 200 y aplica tres pulsos separados 500ms, después de la carga de 3500ms y con retraso de 650ms por oleada. No simula una trayectoria balística ni una flecha individual por víctima.
- Las partículas descendentes se distribuyen en un cuadrado X/Y ±180; sus esquinas quedan fuera del círculo de daño. No usan colisión y carecen de un emisor específico para el impacto en el suelo. Su aparición escalonada y altura 320–360 a velocidad -600 no representan un único instante de caída por oleada.
- Rain/FireRain/Mark utilizan ShotActions sobre un anchor de DrawScale 0.001; las filas visuales usan cast_style=12. Falta probar su reproducción en el cliente: enlaces resueltos y checks de daño no permiten atribuir la invisibilidad a una causa concreta.

Herramienta reproducible de lectura: `research/amber-l2/scripts/diagnose_amber_vfx.groovy` (UnrealSerializerFactory y AmberCatalog). Usa los catálogos descifrados del verificador anterior, correspondientes a los hashes verificados hoy.

Siguiente trabajo: separar visualmente carga del soulshot, activación de fuego, disparo, caída e impacto; reproducir los fallos actuales en L2; corregir fase/enganche del cliente y alinear distribución/tiempos visuales con la zona circular antes de afirmar una corrección.
