# Cómo está construido nuestro L2

Inspección del 15/10/2026. Este documento describe el laboratorio instalado; las facilidades y reglas de pruebas no son automáticamente las del servidor público definitivo.

## Qué estamos usando realmente

`2-JUGAR.cmd` inicia los servicios locales, espera que el mundo esté preparado y ejecuta `E:\l2\system-hud\L2.exe L2Protocol`. Por tanto, **system-hud es la variante habitual**. La carpeta `system` no es una referencia suficiente para describir el cliente que usamos.

El código del servidor está en `source/L2J_Mobius_CT_0_Interlude/java`; el runtime está en `server`. Es L2J Mobius CT0 Interlude, Java, con modificaciones locales. El servidor permite la revisión de protocolo **746**. Los seis binarios principales inspeccionados de system-hud son PE **x86 de 32 bits**, aunque Windows y el Java del servidor puedan ser de 64 bits.

## Las piezas y sus responsabilidades

| Pieza | Papel en este proyecto | Dónde mirar |
|---|---|---|
| Lanzador local | Prepara servicios y abre la variante elegida | `2-JUGAR.cmd`, `Start-L2Local.ps1`, `Wait-L2LabReady.ps1` |
| L2.exe | Arranque del cliente; importa Core, Engine, Window y bibliotecas Windows/gráficas | `E:\l2\system-hud` |
| Core / Engine | Infraestructura y motor nativo; l2.ini selecciona Engine.GameEngine y Engine.Input | DLL y configuración del cliente |
| WinDrv / NWindow / Window | Integración con Windows, entrada y ventanas; imports observados incluyen DirectInput8Create y consultas del teclado | DLL del cliente |
| Interface.u | Lógica de ventanas del cliente; hay modificaciones locales documentadas en ventanas de skills y summon | `system-hud/Interface.u` |
| Interface.xdat | Definición visual/disposición de ventanas | `system-hud/Interface.xdat` |
| DAT del cliente | Catálogos que relacionan identificadores con nombres, iconos y presentación; no sustituyen las reglas del servidor | `system-hud/*.dat` |
| Recursos gráficos y sonido | Escenarios, modelos, animaciones, texturas y audio | Carpetas compartidas de `E:\l2` |
| LoginServer | Autenticación y selección del servidor; autocreación activada en configuración | `server/login`, `server/libs/LoginServer.jar` |
| GameServer | Mundo, personajes, combate, inventario, IA, validación de acciones e instancias | `server/game`, `server/libs/GameServer.jar` |
| MariaDB | Persistencia de cuentas, personajes y demás tablas; no se consultaron filas privadas en esta inspección | `database/data` y herramientas portables |
| Panel de laboratorio | Herramientas locales para administrar y estudiar el laboratorio | `lab-panel`; no es el cliente del juego |

La atribución funcional general de DLL se apoya en configuración, imports y uso local; no implica haber decompilado todos sus métodos.

## Cómo se conectan

La configuración del cliente decodificada conserva `ServerAddr=127.0.0.1`. El LoginServer escucha en **2106**, el GameServer en **7777**, y ambos servicios se comunican por **19014**. MariaDB se inicia localmente en **3307**. Se observaron estos valores en configuración y lanzador; no se certificó en esta etapa qué procesos estaban escuchando.

El flujo es: cliente → LoginServer para autenticar y elegir servidor → GameServer para jugar → base de datos para persistir. El enlace 19014 es entre servicios, no la entrada de jugadores. La configuración `AutoCreateAccounts=True` pertenece a nuestro laboratorio.

En el código, `GamePacketHandler` selecciona paquetes y comprueba el estado de conexión. `ClientPackets` registra ProtocolVersion (0x00), AuthLogin (0x08), EnterWorld (0x03), MoveToLocation (0x01) y RequestBypassToServer (0x21). `ProtocolVersion` rechaza revisiones que no estén en la lista configurada. Un botón del cliente solicita una acción; la autoridad para aceptarla permanece en el servidor.

## Por qué hay varias carpetas system

Se inventariaron **seis variantes**: system, system-amber, system-clean, system-hud, system-local y system-solo. No se borró ni cambió ninguna.

| Archivo | Variante habitual system-hud | Qué demuestra la comparación |
|---|---:|---|
| L2.exe | 491.540 bytes | Mismo SHA256 que amber y clean |
| Engine.dll | 30.704.468 bytes | Mismo SHA256 que amber y clean |
| NWindow.dll | 3.850.260 bytes | Mismo SHA256 que amber y clean |
| Interface.u | 2.043.169 bytes | Distinto de amber/clean (1.964.561 bytes) |
| Interface.xdat | 537.543 bytes | Distinto de amber/clean |

Estos hashes identifican igualdad o diferencia, no antigüedad ni calidad. Los nombres de carpeta no garantizan por sí solos qué versión es más nueva. `system-local` además contiene un clmods.dll distinto del de Damage; **no aparece en system-hud** entre los archivos examinados. No se concluye que ninguna variante carezca por completo de protecciones.

El l2.ini activo busca primero `../system-hud/*.u` y después `../System/*.u`, y carga recursos de carpetas compartidas. Por eso reemplazar un archivo en una carpeta secundaria puede no cambiar lo que usa el acceso habitual, y algunos paquetes pueden resolverse por la ruta alternativa. Esto es importante para evitar diagnósticos sobre la copia equivocada.

## Qué ya personalizamos

- **Skills y Amber:** la documentación de V3 registra cambios en Interface.u/XDAT, texturas y DAT, coordinados con SkillList y SkillCatalogView/Model del servidor. Los botones filtran lo que se muestra; no otorgan habilidades. El código actual de RequestBypassToServer conserva una ruta explícita para acciones de esa ventana y validaciones para otras acciones.
- **Salas PvP:** WorldContent.ini permite ElvenPvpRoom y otros módulos personalizados. PvpRooms.java muestra el menú, administra la instancia, cuenta cuatro segundos y decide el retorno. El cliente recibe ExShowScreenMessage para el indicador textual y paquetes de posición. No hay aún un widget gráfico nuevo de cuenta regresiva.
- **Mundo de laboratorio:** CustomWorldOnly=True y CustomSpawnDirectory=data/lab/world-spawns. No conviene interpretar sus NPCs y facilidades como un mundo Interlude estándar intacto.
- **Carga e identidad:** recursos propios de splash y textura de carga están documentados en PRECARGA-Y-FONDO-EPICO-V1.md. Eso cambia presentación, no combate.
- **Muelle y aeronaves:** hay integraciones documentadas de escenarios y naves estacionadas. El transporte aéreo con pasajeros en movimiento sigue requiriendo un prototipo y prueba real; tener el modelo visible no acredita que ya vuele.

Los documentos históricos aportan trazabilidad de cambios. Esta inspección no volvió a ejecutar sus pruebas ni certificó cada archivo instalado contra todos sus manifiestos.

## Recursos encontrados

Inventario del primer nivel de las carpetas compartidas: **157 mapas UNR**, **311 UKX y 10 USK** de animación/modelos, **215 USX** de static meshes, **392 UTX** en textures y **271 UTX** en systextures. Es un inventario de archivos; no un recuento de modelos únicos, mapas jugables o recursos cargados simultáneamente.

La geometría que ve el cliente y la geodata del servidor son piezas diferentes. Agregar una plataforma o nave visible requiere comprobar también suelo, tránsito y posiciones en el servidor. Para una cubierta móvil, además hacen falta transporte y posiciones relativas; una malla por sí sola no lo resuelve.

## Qué aporta REA y hasta dónde llegamos

REA/Ghidra abrió el L2.exe **activo** con SHA256 `790d9068796714389d82a400d14d26dcb9e6ecdfc6c2b5eba92ebd1a441b10ee`. En 0x109224da decompiló el punto de entrada: inicializa el security cookie y llama al arranque CRT. La cadena InitEngine está en 0x1095b348; la referencia encontrada pertenece a un manejador de error que llama appUnwindf y relanza una excepción. Eso **no es el cuerpo de inicialización del motor**.

Para entender nuestras reglas, el código Java disponible y los scripts son más directos que decompilar el cliente. Para entender un control visual, una función nativa o un formato concreto, REA y los lectores de paquetes permiten profundizar. No se recuperó el código fuente original completo del cliente ni se verificó su comportamiento visual en una sesión nueva.

## Guía para futuros cambios

| Objetivo | Primera capa que conviene estudiar/modificar |
|---|---|
| Flag PvP, recompensas, timer, votación, respawn | Script/configuración/Java del servidor |
| Menú del NPC | HTML y handler del servidor |
| Barra gráfica nueva y paneles propios | Interface.u + XDAT + texturas; servidor comunica el estado |
| Nombres e iconos propios | DAT + recursos del cliente, coordinados con los IDs del servidor |
| Nuevo terreno o muelle | Mapa/meshes del cliente + geodata y spawns del servidor |
| Nave que transporta jugadores | Vehicle y paquetes del servidor + soporte y prueba del cliente |

## Evidencias y alcance

`research/client-architecture/inventory.json`: tamaños, SHA256, secciones e imports de los archivos seleccionados de las seis variantes, y recuentos de recursos del primer nivel. `active-input-imports.json`: funciones de entrada importadas por la variante activa. `l2.ini.decoded.txt`: copia decodificada, sin alterar el original. `rea-*.json`: evidencia de REA, incluidos sus límites. Los scripts inventory.py y summarize.py permiten repetir la inspección.

No se modificaron cliente, servidor, base de datos ni reglas; se crearon únicamente informes y archivos de análisis. No se comprobó equivalencia completa entre todo el fuente y los JAR desplegados. Las comprobaciones del código describen ese fuente; la configuración y archivos inventariados describen las copias instaladas.
