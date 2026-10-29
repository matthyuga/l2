# Alternativas de PvP flag revisadas

15/10/2026. Comparación de código local, módulo Orion descargado y publicaciones públicas. No se compilaron ni instalaron estas alternativas. Son módulos/parches, no necesariamente packs completos ni compatibles directamente con Mobius actual.

| Alternativa | Diferencia comprobada | Mapas/ejemplos y alcance |
|---|---|---|
| Mobius local FlagPvPZone | Flag al entrar, limpieza inmediata al salir; muerte llama salida y revive llama entrada | La clase no fija mapas. Ya tenemos el fuente |
| Orion RandomZone | Auto-flag configurable, instancias, restricciones de clases y selección aleatoria con reloj; al salir llama updatePvPStatus en vez de poner flag a cero directamente | Siete ejemplos ya descargados. Sin voto en los controladores inspeccionados |
| Mobius Pvp Flag Zone, durgus | Publicación añade Noblesse al entrar y limpia flag al salir; no trae rotación en el controlador mostrado | Ejemplo Primeval. Revisión mediante contenido indexado; acceso directo 403, parche completo no descargado. https://l2jmobius.org/forum/index.php?topic=11872.0 |
| ChaoticZone, Juvenil Walker | Configura flag, Noblesse, recuperación de recursos y mensajes; al salir programa la expiración normal del flag | Publicación etiquetada C5 con ejemplos Primeval, Pagan Temple, Monastery, Ketra e Imperial Tomb; necesita adaptación y corrección. https://l2jmobius.org/forum/index.php?topic=5629.0 |
| Lisvus C4, JMD13 | Implementación mínima; quita flag al salir, sin reloj/votos en el parche mostrado | Otra crónica; el código publicado contiene updatetPvPFlag, posible errata. https://gist.github.com/JMD13/8a14f647661440a3333405f8e6619c0b |

La demora del flag tras salir de ChaoticZone no equivale a nuestra franja con expulsión a los cuatro segundos. Sus opciones de curación y Noblesse tampoco deben incorporarse por defecto. Hay inconsistencias en el ejemplo (condición de curación de entrada y minZ/maxZ de Monastery), por lo que no se considera listo para instalar.

Conclusión técnica: para HELLGAMES, conservar la infraestructura Mobius propia y usar Orion como referencia para catálogo/reloj; revisar ChaoticZone por el tratamiento del flag al salir y sus ejemplos de zonas. Ninguno de estos controladores aporta por sí solo lobby de salas, votos de siguiente mapa y nuestra salida vulnerable. Las coordenadas definen zonas sobre el mundo existente; no implican nuevos mapas UNR.
