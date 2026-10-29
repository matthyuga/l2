# Exploración caminando y niebla sincronizada — V4, 25/10/2026

## Estado

Instalada con cliente cerrado. GameServer reiniciado y log confirma ExplorationWalking V4 ready; puerto7777 listo. Cliente nativo V4 instalado, pendiente de prueba visual dentro de L2. No confundir los tests del atlas aislado con una validación de la recepción del paquete en el cliente real.

Kevin señaló que caminar fuera de Giran y viajar a Goddard no revelaba nada: V2/V3 seguían siendo una regla gráfica fija. Esta entrega conecta exploración del servidor con la cobertura del cliente. Para esta prueba, entrar/caminar revela entorno sin exigir baliza. Las campañas, recuperación política y GK no se activan por descubrir una celda.

## Comportamiento

- Activación automática para jugadores GM humanos online; se excluyen Player.isLabControlled, muertos, teletransportes en curso e instancias privadas para registrar movimiento. No cambia el comportamiento de bots ni añade recompensas.
- Cada segundo se comprueba la posición y se registran la celda continental y sus ocho vecinas. Celda4096 unidades; el revelado aparece en tramos, con transición espacial suave, no un círculo recalculado a cada paso.
- Un teleport revela la llegada una vez asentado el personaje, nunca el trayecto imaginario entre origen y destino.
- Giran permanece despejada por su máscara municipal inicial.
- Cada personaje guarda su propia cartografía. La unión global indica terreno conocido; un segundo personaje ve allí cobertura parcial hasta explorarlo personalmente.
- Primera entrada a una TownZone muestra Lugar descubierto: <nombre> una vez por personaje. Goddard utiliza la zona real del servidor, no un círculo dibujado a mano.
- `.exploracion estado` informa cantidades; `.exploracion pausa` y `.exploracion continuar` controlan el registro automático. No usar `.explora anclar` para este sistema: ese comando conserva el ensayo V1 independiente.

## Datos y persistencia

Grid versionado100x150,4096 unidades/celda, origen de mundo(-131072,-262144);15000bits/1875bytes por capa. PlayerVariables FOG4_PERSONAL en character_variables.val(TEXT) guarda Base64 personal. FOG4_TOWN_<id> guarda ciudades. FOG4_PAUSED conserva la preferencia de pausa. El conocimiento global queda en server/game/data/exploration-walking-v4/global.base64 mediante reemplazo atómico. El archivo se crea cuando se descubre terreno. No se migraron ni borraron los datos V1.

## Transporte real servidor→cliente

Snapshots por la conexión del juego usando ExShowScreenMessage, texto reservado:
`#NXFOG4|playerId|sequence|globalBase64|personalBase64`.
Longitud máxima5500, cada Base64 máximo2500. Se envía cuando cambia el progreso/conocimiento o al reconectar; refresco máximo10seg si no hubo cambios. El proxy V4 intercepta solamente ese prefijo antes de mostrar el mensaje. Los títulos normales siguen su ruta original.

REA localizó NConsoleWnd::OnExShowScreenMessage RVA1696b0, thiscall/RET4, primer parámetro L2ParamStack. Su cuerpo consume10enteros y un puntero UTF16. Evidencia en ../map-fog-analysis-20261025/rea-v4-packet-bridge.json. La disposición data/index/count de L2ParamStack se comprobó adicionalmente con pefile/capstone sobre el export Top de Core.dll: esa lectura es de herramientas locales, no evidencia REA.

El cliente valida el prefijo, la estructura/cotas y Base64; reemplaza ambas capas completas, no une progreso personal de personajes distintos. La recepción efectiva en el juego y supresión del texto técnico deben confirmarse visualmente/log. No hay archivos locales compartidos entre jugadores ni un servidor web auxiliar. Esta versión asume clientes GM del laboratorio actualizados; la negociación de capacidades para clientes antiguos o lanzamiento público sigue pendiente.

## Representación gráfica

Proxy en ../map-fog-walking-v4. Conserva guardias, trampolines y corrección de opacidad V3. Un material marcador de16x16 se sustituye únicamente cuando coinciden sus ocho píxeles identificadores exactos. Direct3D recibe un atlas propio1024x2048, generado a partir de las dos capas y la máscara original de Giran. No se sustituyen otras texturas.

El mapa nativo conserva su dibujo/arrastre. La cobertura usa la proyección nativa mundial/urbana y UV flotantes del mismo backend, para que una vista urbana pueda muestrear una porción pequeña del atlas. La interpolación de celdas y una perturbación leve con las nubes suavizan los bordes. El atlas se regenera solo al cambiar la cartografía. Giran conserva la excepción municipal exacta; no es el revelado de una cuadrícula gruesa.

Archivos cliente nuevos NexusMapFogV4.u y NexusFogFieldV4.bin; el paquete/máscara V2 se conserva para rollback. Log NexusMapFog.log: debe mostrar START V4, INSTALLED, RECEIVED personal/global exploration snapshot y MATCHED V4 overlay. Un log de recepción/atlas no prueba por sí solo la alineación visual.

## Pruebas realizadas

- Fuentes Java compiladas contra GameServer.jar actual.
-16 checks FogGrid: dos jugadores separados, movimiento, teleport sin línea, bordes, codec, tamaño máximo.
-20406 checks nativos base;20411 al decodificar el paquete producido por Java y comprobar CLEAR personal, PARTIAL global y TOTAL desconocido.
- Test HAL con la DLL real: marcador exacto sustituido por atlas1024x2048, píxeles GPU transparentes en Giran y opacos en desconocido,16Present correctos.
- Marcador UCC, wrapper121/roundtrip/CRC; binario de nubes y máscara derivado de los assets V2.
- ScriptEngine cargó ExplorationWalking V4 y servidor abrió7777. El log contiene además avisos previos de validación XML de otros NPC; no se modificaron en esta entrega.

Pendiente en cliente real: caminar y comprobar avance, Goddard y su aviso, persistencia al reconectar, un segundo personaje y recepción del protocolo sin texto técnico en pantalla. No se promete actualización de niebla a cada píxel ni animación temporal de disolución.

## Instalación y restauración

installation.json y backups/exploration-walking-v4-20261025-230223 contienen archivos, hashes y respaldo. Se añadieron scripts/whitelist en runtime y fuente distribuible y los assets/proxy cliente; no se reemplazó GameServer.jar ni NWindow/Interface. V1 sigue cargado como ensayo aislado. Se reinició solo GameServer, con cliente cerrado y sin conexiones7777.

Para volver a V3, cerrar cliente y detener GameServer; ejecutar restore.py de esta carpeta y reiniciar después. Conserva variables personales y el archivo global nuevo. Si hubiera otro cambio concurrente de archivos, el restaurador se detiene por hashes.
