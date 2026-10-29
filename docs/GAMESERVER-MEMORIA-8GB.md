# GameServer: límite de memoria de 8 GiB

11/10/2026. Cambio autorizado por Kevin. Arranque normal validado con Java: `MaxHeapSize=8589934592` (8192 MiB) y `InitialHeapSize=536870912` (512 MiB). No se preasignan los 8 GiB completos; el heap puede crecer según la demanda y Java puede conservar espacio libre para reutilizarlo. El proceso consume memoria adicional fuera del heap.

`Start-L2Local.ps1` selecciona ahora 8192 MiB por defecto si la computadora tiene al menos 24 GiB de RAM total utilizable. En esta PC: 32 GiB instalados, i9-11900K. En equipos portátiles con menos RAM conserva el cálculo anterior de 2/3/4 GiB. El parámetro explícito `-GameHeapMb` sigue admitiendo de2048 a8192 MiB. El cliente L2 y LoginServer mantienen su configuración.

Se mantuvieron `-Xms512m`, ZGC y el pool acotado de32 buffers de búsqueda de caminos (~65 MiB). No se modifica core, IA, geodata ni cantidad de bots: siguen19 perfiles. Aumentar el heap no demuestra una capacidad mayor de combate; esa capacidad requiere pruebas de carga.

GameServer reiniciado con L2 cerrado y sin conexiones de jugadores. Inicio normal sin verificadores de combate. Primera medición tras arrancar:1076 MiB de heap usados, máximo8192 MiB; login registrado y puerto7777 abierto. No se reproduce una batalla para validar este cambio de configuración.

Launcher sincronizado con `cloud-repo/ops/windows/Start-L2Local.ps1`, sin commit ni push. Respaldo: `backups/game-heap8-2026-10-11/Start-L2Local.before.ps1` y registros anteriores. Continuidad40 en W10/W11 y copia de Nexus en el disco portátil.
