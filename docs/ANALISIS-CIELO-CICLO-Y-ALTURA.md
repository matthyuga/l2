# Cielo, ciclo diario, iluminación y altura de nuestro Interlude

Análisis del 21/10/2026. Cliente habitual: `E:\l2\system-hud`, identificado por los lanzadores del proyecto. Servidor: L2J Mobius CT0 local. Solo lectura de originales; no se ejecutó el juego ni se modificaron paquetes, reloj, servidor o configuraciones del cliente.

## Resultado principal

**El cliente ya separa cielo, sol visible, luna y luz solar direccional móvil. También interpola colores y tamaños según la hora.** Nuestra idea puede apoyarse en este sistema nativo. Los panoramas descargados son recursos nuevos que habrá que adaptar a él; no demuestran que sus transiciones o sus sombras ya estén integradas.

El mapa actual del muelle (`Maps/24_19.unr`) contiene esos actores. No hay que colocar el sol como NPC ni llevarlo a alturas jugables gigantescas.

## 1. Quién lleva el tiempo

El servidor calcula un reloj 6 veces más rápido que el real: 24 horas de juego duran 4 horas reales. Noche de 00:00 a 06:00 (una hora real) y día de 06:00 a 24:00 (tres horas reales). La referencia es la medianoche local de la fecha de arranque; no es un contador de progreso persistido en la base de datos.

Los cambios de período afectan spawns, eventos y Shadow Sense. `/time` consulta ese reloj.

`CharSelected` transmite la hora durante la entrada del personaje. Existe `ClientSetTime`, con minutos y velocidad, pero no se encontró un envío efectivo de ese paquete en el código inspeccionado. No se debe afirmar que haya resincronización periódica implementada.

En el cliente, `UL2NEnvManager::SetNTime`, inspeccionado en `engine.dll` a VA `0x10515620`, almacena hora/minuto/segundo y construye una hora fraccionaria con factores aproximadamente 1/60 y 1/3600. Su `IsDay` (`0x105142d0`) compara con 6 y 24. Falta trazar completamente el camino desde cada paquete de red hasta este objeto y medir posibles desajustes durante ejecución.

Referencias completas: `research/day-night-analysis/server-findings.md`; vistas nativas en `native-interpolation-cfg.json`.

## 2. Cielo y cuerpos celestes son piezas distintas

En el mapa actual del muelle se comprobaron:

| Elemento | Función y evidencia |
|---|---|
| `SkyZoneInfo0` | Zona de cielo separada; Z=24727,02; panning y lens flares. `ZoneInfo.LinkToSkybox` enlaza zonas con un SkyZoneInfo. |
| `NSun0` | Disco solar; textura `L2_Skies.FlareSet.Sun01`; Radius=350, LimitMaxRadius=50; Z=24766,68. |
| `NMoon0` | Luna; textura `L2_Skies.moon.moon`; Radius=245; Z=24762,84. |
| `NMovableSunLight0` | Luz solar; LightBrightness=70, bSunAffect=true. La clase conservada en Engine.u se describe como luz solar direccional móvil. |

Las posiciones serializadas de sol y luna no son por sí solas la trayectoria que se ve al jugar. Son la configuración inicial de actores de un escenario celeste separado.

El paquete `l2_skies.utx` contiene sol y luna independientes, nubes con TexPanner, estrellas con TexRotator y modificadores de color de cielo/horizonte. La nube WhiteCloud usa PanRate=0.002. El cielo original no es simplemente una fotografía completa con el sol pintado.

**Movimiento corroborado en código máquina:** `ANMovableSunLight::GetSunLightDirection` (`engine.dll`, VA `0x10343220`) calcula un vector a partir de una hora flotante; emplea constantes 6/24, factores angulares y llamadas importadas a `core.dll!appSin` y `appCos`. La magnitud empleada en esta rutina es 32768; no es una altura máxima del mundo ni una distancia que deba copiarse a un personaje. En el tramo diurno, la expresión angular observada es proporcional a `(hora - 6) × π/18 - π/2`. `UL2NEnvManager::GetSunLightDirection` tiene además su propio camino de cálculo de sol/luna y orientación; no se debe asumir que el helper anterior sea el único camino usado por todo el renderer.

Esto establece cálculo nativo dependiente del tiempo; no es una observación de la órbita en una sesión de juego.

## 3. Cómo ocurren las transiciones

Los cuatro archivos `timeenv0.int` a `timeenv3.int` contienen perfiles completos de ambiente, cada uno con sus propias curvas horarias. **No equivalen a mañana/tarde/noche/tormenta por su número.** La asignación semántica de cada perfil a eventos o zonas no se ha cerrado.

Sus tablas incluyen:

- Color y escala del sol y de la luna.
- Color del cielo, horizonte/bruma y tres capas de nube.
- Iluminación ambiental diferenciada de terreno, personajes, mallas estáticas y BSP.
- Luz solar HSV diferenciada para esas mismas categorías.

En el perfil 0, por ejemplo, el sol cambia desde RGB 255/122/23 a las 06:00 a colores más claros durante el día, y vuelve a tonos cálidos al terminarlo. El cielo tiene claves nocturnas, amanecer, horas diurnas y cierre en 24:00. Son ejemplos de datos, no una captura visual.

**Interpolación comprobada en el binario activo:**

- `UL2NTimeLight::GetColor` a `0x10514e70` busca dos claves temporales vecinas y mezcla cada canal mediante una proporción temporal; el resultado RGB se convierte a byte.
- `UL2NTimeLight::GetScale` a `0x10515590` calcula el equivalente a `a + (b-a) × (hora-ti)/(tj-ti)`.
- `UL2NEnvManager::ChangeEnv` a `0x1051a420` mantiene identificadores de entornos y tiempos de transición; `CalcEnvDelta` a `0x10514720` y `GetEnvColor` a `0x10515a70` calculan proporciones y mezclas. Esto demuestra mecanismos de mezcla de perfiles, aunque no se reconstruyó toda su interfaz y selección.

Por tanto, el motor ya puede hacer cambios graduales de **parámetros**. Eso no demuestra que pueda mezclar automáticamente dos panoramas nuevos cualesquiera: texturas, materiales y capas adicionales requieren su propia adaptación.

Advertencias de formato observadas: hay secciones HSV duplicadas en algunos perfiles y un caso con NUM=1 junto a múltiples entradas COLOR. No usar un editor genérico que elimine duplicados o reescriba los perfiles sin reproducir su lector nativo. Algunos brillos HSV son flotantes y superan 255.

## 4. Luz, sombras, clima y eventos

La arquitectura permite distinguir luz ambiental y luz solar por categoría de objeto. También hay zonas interiores serializadas con bSunAffect=false, por lo que la respuesta a la luz no tiene por qué ser idéntica en todo el mapa.

**Sombras:** no se comprobó todavía qué superficies recalculan sombras geométricas al avanzar la hora y cuáles conservan lightmaps, iluminación de vértices o sombras pintadas en las texturas. La mera existencia de una luz móvil o de `SetShadowTick` no prueba sombras solares dinámicas modernas. En Actor.uc, bShadowCast se describe como sombras estáticas; los defaults heredados no se dedujeron de propiedades ausentes en el mapa.

**Pendiente por decisión de Kevin (21/10/2026):** posponer la investigación y las pruebas de sombras hasta que lo retome expresamente.

**Clima:** existen datos de niebla por zona, L2FogInfo con colores por hora, propiedades de viento y controles meteorológicos en emisores. Esto es soporte estructural; no se comprobó un sistema completo operativo de tormenta/arena con lluvia, rayos y audio sincronizados.

**Overrides disponibles:** `//atmosphere sky day`, `night` y `red` envían paquetes visuales a todos los jugadores. No cambian el reloj ni la lógica del servidor. SunRise/SunSet no envían la posición del sol ni una configuración arbitraria de luz; ExRedSky lleva una duración. El handler nativo `UGameEngine::OnRedSky` (`0x1048d540`) entra en el mecanismo de cambio de entorno con identificador 3. Esto no prueba un comando existente para elegir verde o violeta libremente.

## 5. Qué significan los límites de altura

| Capa | Límite o dato observado | Lo que no significa |
|---|---|---|
| Coordenada del personaje reportada por cliente | ValidatePosition trata Z fuera de [-20000,20000] como anormal. | No es el techo del cielo ni el máximo del renderer. |
| Regiones verticales del servidor | Constantes -16000/+16000 y celdas de 2000. | No son un clamp universal: valores externos se agrupan en regiones extremas. |
| Geodata compleja y multicapa | Alturas codificadas -16384..16376, pasos de 8. | No limita las posiciones de sol/luna en el escenario del cielo. |
| Cielo real del muelle | Sol y cielo ya están alrededor de Z=24700. | No es una altura jugable segura ni una prueba de espacio infinito. |

Todas son **unidades nativas de L2**, no metros del Taller. El máximo vertical efectivo del renderer, las restricciones de vuelo y el recorrido seguro del jugador no quedaron medidos. También se detectó un posible borde defectuoso del particionado en Z exactamente 16000; está documentado como hallazgo estático sin reproducción, no como fallo confirmado al jugar.

## 6. Aplicación a nuestro proyecto

La vía respaldada por este análisis es conservar el reloj de L2 y adaptar su cielo/sol/iluminación:

1. Preparar una copia aislada del cliente/mapa y registrar un ciclo visual de referencia, con `/time`.
2. Probar cambios acotados en una copia de las curvas de ambiente, conservando el sol/luna nativos y las diferencias entre zonas.
3. Medir la respuesta real de terreno, árboles, personajes, edificios y sombras en varios horarios.
4. Adaptar panoramas sin sol —o capas de cielo/nubes— para no duplicar el disco solar ni dejar resplandores incompatibles con su dirección.
5. Tratar clima y eventos como estados adicionales coordinados con la hora; comprobar cómo entrar y salir de perfiles especiales antes de prometer colores arbitrarios desde el servidor.

El Taller puede servir para diseñar y comparar estas etapas, pero no sustituye la validación del cliente Interlude.

## Evidencia, identidad y alcance

- `research/day-night-analysis/environment-findings.md`: configuración, recursos, mapas y clases conservadas.
- `active-system-comparison.json`: los cuatro timeenv son idénticos byte a byte en system y system-hud.
- `active-engine-comparison.json`: Engine.u difiere entre variantes; se corroboraron 13 textos de clases relevantes, idénticos. No trasladar offsets de la variante auxiliar al paquete activo.
- `engine-inventory.json`: SHA-256 del engine.dll activo, exports y cadenas con offsets.
- `native-function-views.json`, `native-interpolation-cfg.json`: instrucciones nativas y grafos locales de ramas; pefile + Capstone, x86 de 32 bits. Estos resultados son inspección estática ordinaria, no REA Evidence ni ejecución del juego.
- `server-findings.md`: referencias exactas del código Java.

REA MCP no abrió una sesión nativa: el proveedor Ghidra informó `runtime_missing` en su detección de Java. El Java portable sí ejecutó `-version` por CLI. El diagnóstico CLI, sin cambiar configuraciones, tampoco tenía GHIDRA_INSTALL_DIR en ese proceso. Se continuó con parsers de paquetes, ScriptText conservado y desensamblado x86 con herramientas ya instaladas. No se instaló software ni se alteró la configuración de REA. Las conclusiones nativas se atribuyen a esa lectura ordinaria.

Cobertura: reloj y reglas del servidor respondidos; separación de cielo/sol/luna respondida; interpolación de color/escala corroborada estáticamente; dirección solar dependiente del tiempo corroborada estáticamente. Sin resolver en ejecución: sincronización continua, interpretación íntegra de perfiles, respuesta de sombras y clima, y límites verticales del renderer/vuelo.
